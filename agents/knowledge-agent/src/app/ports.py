import re
import unicodedata
from typing import Protocol
from app.models import Chunk, SearchFilters
class EmbeddingPort(Protocol):
    dimensions: int
    async def embed(self,texts:list[str])->list[list[float]]: ...
class VectorStorePort(Protocol):
    async def ensure_collection(self,dimensions:int)->None: ...
    async def replace_all(self,chunks:list[Chunk],vectors:list[list[float]])->None: ...
    async def upsert(self,chunks:list[Chunk],vectors:list[list[float]])->None: ...
    async def search(self,vector:list[float],limit:int,score_threshold:float,locale:str,filters:SearchFilters)->list[tuple[Chunk,float]]: ...
    async def health(self)->bool: ...
class RerankerPort(Protocol):
    async def rerank(self,query:str,hits:list[tuple[Chunk,float]])->list[tuple[Chunk,float]]: ...
class PassthroughReranker:
    async def rerank(self,query,hits): return hits
class LexicalReranker:
    """Small deterministic reranker for the dependency-free French demo profile."""
    _stop={"alors","apres","avec","cette","comment","dans","des","elle","entre","faire","faut","fonctionne","mon","pour","quels","quelle","sont","une"}
    @classmethod
    def _terms(cls,text):
        plain=unicodedata.normalize("NFKD",text.lower()).encode("ascii","ignore").decode()
        words=re.findall(r"[a-z0-9_]+",plain)
        return {word if "_" in word or len(word)<5 else word[:4] for word in words if len(word)>2 and word not in cls._stop}
    async def rerank(self,query,hits):
        wanted=self._terms(query)
        def ranked(hit):
            chunk,vector_score=hit
            title_terms=self._terms(f"{chunk.metadata.title} {chunk.metadata.source_filename}")
            content_terms=self._terms(chunk.content)
            title_overlap=len(wanted & title_terms)
            content_overlap=len(wanted & content_terms)
            return (title_overlap*3+content_overlap,vector_score)
        return sorted(hits,key=ranked,reverse=True)
class VectorStoreUnavailable(RuntimeError): pass

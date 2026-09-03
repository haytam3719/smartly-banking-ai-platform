from app.models import SearchHit, SearchRequest, SearchResponse
from app.ports import EmbeddingPort, LexicalReranker, RerankerPort, VectorStorePort
class KnowledgeSearchService:
    def __init__(self,embedder:EmbeddingPort,store:VectorStorePort,reranker:RerankerPort|None=None,max_context_characters:int=6000): self.embedder=embedder; self.store=store; self.reranker=reranker or LexicalReranker(); self.max_context=max_context_characters
    async def search(self,request:SearchRequest)->SearchResponse:
        vector=(await self.embedder.embed([request.query]))[0]
        # The deterministic local embedder is intentionally lightweight, so collect a broad
        # candidate set before lexical reranking. Production semantic embedders still benefit
        # from the same bounded recall window.
        candidates=await self.store.search(vector,200,request.score_threshold,request.locale,request.filters)
        ranked=await self.reranker.rerank(request.query,candidates); results=[]; seen=set(); total=0
        for chunk,score in ranked:
            dedupe=(chunk.metadata.document_id,chunk.content)
            if dedupe in seen: continue
            if total+len(chunk.content)>self.max_context: continue
            seen.add(dedupe); total+=len(chunk.content); results.append(SearchHit(content=chunk.content,document_id=chunk.metadata.document_id,document_type=chunk.metadata.document_type,score=score,metadata=chunk.metadata))
            if len(results)>=request.top_k: break
        return SearchResponse(results=results,context_characters=total)

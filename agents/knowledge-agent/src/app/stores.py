from datetime import date
import math
from qdrant_client import AsyncQdrantClient, models
from app.models import Chunk, SearchFilters
from app.ports import VectorStoreUnavailable

class InMemoryVectorStore:
    def __init__(self): self.items={}; self.available=True; self.dimensions=None
    async def ensure_collection(self,dimensions):
        if not self.available: raise VectorStoreUnavailable("Vector store unavailable")
        self.dimensions=dimensions
    async def upsert(self,chunks,vectors):
        if not self.available: raise VectorStoreUnavailable("Vector store unavailable")
        for chunk,vector in zip(chunks,vectors,strict=True): self.items[chunk.id]=(chunk,vector)
    async def replace_all(self,chunks,vectors):
        if not self.available: raise VectorStoreUnavailable("Vector store unavailable")
        self.items.clear()
        await self.upsert(chunks,vectors)
    async def search(self,vector,limit,score_threshold,locale,filters):
        if not self.available: raise VectorStoreUnavailable("Vector store unavailable")
        today=date.today(); hits=[]
        for chunk,candidate in self.items.values():
            m=chunk.metadata
            if not m.active or m.locale!=locale or m.effective_from>today or (m.effective_to and m.effective_to<today): continue
            if filters.document_type and m.document_type!=filters.document_type: continue
            if filters.version and m.version!=filters.version: continue
            score=sum(a*b for a,b in zip(vector,candidate,strict=True)); score=max(0.0,min(1.0,score))
            if score>=score_threshold: hits.append((chunk,score))
        return sorted(hits,key=lambda x:x[1],reverse=True)[:limit]
    async def health(self): return self.available

class QdrantVectorStore:
    def __init__(self,url:str,collection:str,api_key:str|None=None): self.client=AsyncQdrantClient(url=url,api_key=api_key,timeout=2); self.collection=collection
    async def ensure_collection(self,dimensions):
        try:
            if not await self.client.collection_exists(self.collection): await self.client.create_collection(self.collection,vectors_config=models.VectorParams(size=dimensions,distance=models.Distance.COSINE))
        except Exception as exc: raise VectorStoreUnavailable("Vector store unavailable") from exc
    async def upsert(self,chunks,vectors):
        try:
            points=[]
            for c,v in zip(chunks,vectors,strict=True):
                payload=c.model_dump(mode='json');payload['effective_from_ordinal']=c.metadata.effective_from.toordinal();payload['effective_to_ordinal']=(c.metadata.effective_to or date.max).toordinal();points.append(models.PointStruct(id=c.id,vector=v,payload=payload))
            await self.client.upsert(self.collection,points,wait=True)
        except Exception as exc: raise VectorStoreUnavailable("Vector store unavailable") from exc
    async def replace_all(self,chunks,vectors):
        """Atomically replace the demo collection so removed/versioned chunks cannot linger."""
        try:
            if await self.client.collection_exists(self.collection):
                await self.client.delete_collection(self.collection)
            await self.client.create_collection(self.collection,vectors_config=models.VectorParams(size=(len(vectors[0]) if vectors else 128),distance=models.Distance.COSINE))
            if chunks: await self.upsert(chunks,vectors)
        except VectorStoreUnavailable:
            raise
        except Exception as exc: raise VectorStoreUnavailable("Vector store unavailable") from exc
    async def search(self,vector,limit,score_threshold,locale,filters):
        today=date.today().toordinal(); must=[models.FieldCondition(key='metadata.active',match=models.MatchValue(value=True)),models.FieldCondition(key='metadata.locale',match=models.MatchValue(value=locale)),models.FieldCondition(key='effective_from_ordinal',range=models.Range(lte=today)),models.FieldCondition(key='effective_to_ordinal',range=models.Range(gte=today))]
        if filters.document_type: must.append(models.FieldCondition(key='metadata.document_type',match=models.MatchValue(value=filters.document_type)))
        if filters.version: must.append(models.FieldCondition(key='metadata.version',match=models.MatchValue(value=filters.version)))
        try:
            points=(await self.client.query_points(collection_name=self.collection,query=vector,query_filter=models.Filter(must=must),limit=limit,score_threshold=score_threshold,with_payload=True)).points
            return [(Chunk.model_validate(p.payload),float(p.score)) for p in points]
        except Exception as exc: raise VectorStoreUnavailable("Vector store unavailable") from exc
    async def health(self):
        try: await self.client.get_collection(self.collection); return True
        except Exception: return False

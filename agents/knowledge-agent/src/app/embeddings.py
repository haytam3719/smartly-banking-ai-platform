import hashlib, math
import httpx
from pydantic import BaseModel
class DeterministicEmbedding:
    """Hashing embedder for tests/local demos; stable, not production semantic quality."""
    def __init__(self,dimensions:int=128): self.dimensions=dimensions
    async def embed(self,texts:list[str])->list[list[float]]:
        return [self._one(text) for text in texts]
    def _one(self,text):
        values=[0.0]*self.dimensions
        tokens=[x for x in ''.join(c.lower() if c.isalnum() else ' ' for c in text).split() if x]
        for token in tokens:
            digest=hashlib.sha256(token.encode()).digest(); idx=int.from_bytes(digest[:4],'big')%self.dimensions; values[idx]+=1 if digest[4]%2 else -1
        norm=math.sqrt(sum(x*x for x in values)) or 1
        return [x/norm for x in values]
class _EmbeddingResponse(BaseModel):
    data:list[dict]
class OpenAICompatibleEmbedding:
    def __init__(self,client:httpx.AsyncClient,base_url:str,api_key:str,model:str,dimensions:int): self.client=client; self.url=base_url.rstrip('/')+'/embeddings'; self.api_key=api_key; self.model=model; self.dimensions=dimensions
    async def embed(self,texts):
        response=await self.client.post(self.url,headers={'Authorization':f'Bearer {self.api_key}'},json={'model':self.model,'input':texts}); response.raise_for_status(); data=_EmbeddingResponse.model_validate(response.json()).data; return [row['embedding'] for row in data]

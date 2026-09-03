from fastapi import FastAPI
from httpx import ASGITransport,AsyncClient
from app.api import router
from app.embeddings import DeterministicEmbedding
from app.service import KnowledgeSearchService
from app.stores import InMemoryVectorStore
async def test_search_api_and_health():
    store=InMemoryVectorStore();app=FastAPI();app.include_router(router);app.state.store=store;app.state.search_service=KnowledgeSearchService(DeterministicEmbedding(),store)
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
        response=await client.post('/internal/v1/search',json={"query":"fees","top_k":4,"locale":"fr-FR","filters":{"document_type":"account_fees"}})
        assert response.status_code==200;assert response.json()=={"results":[],"context_characters":0}
        assert (await client.get('/health')).json()=={"status":"UP","qdrant_available":True}
        assert (await client.get('/internal/v1/capabilities')).json()=={"capabilities":["knowledge.search"]}
async def test_unavailable_api_is_safe():
    store=InMemoryVectorStore();store.available=False;app=FastAPI();app.include_router(router);app.state.store=store;app.state.search_service=KnowledgeSearchService(DeterministicEmbedding(),store)
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
        response=await client.post('/internal/v1/search',json={"query":"fees","locale":"fr-FR"})
        assert response.status_code==503;assert response.json()["detail"]["code"]=="KNOWLEDGE_STORE_UNAVAILABLE"

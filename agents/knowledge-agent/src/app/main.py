import logging,os,sys
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from pythonjsonlogger.json import JsonFormatter
from app.api import router
from app.embeddings import DeterministicEmbedding,OpenAICompatibleEmbedding
from app.service import KnowledgeSearchService
from app.stores import InMemoryVectorStore,QdrantVectorStore
from app.telemetry import configure_tracing
handler=logging.StreamHandler(sys.stdout);handler.setFormatter(JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s'));logging.getLogger().handlers=[handler];logging.getLogger().setLevel(logging.INFO)
configure_tracing();HTTPXClientInstrumentor().instrument()
@asynccontextmanager
async def lifespan(app:FastAPI):
    mode=os.getenv('EMBEDDING_PROVIDER','deterministic'); client=httpx.AsyncClient(timeout=5)
    embedder=DeterministicEmbedding(int(os.getenv('EMBEDDING_DIMENSIONS','128'))) if mode=='deterministic' else OpenAICompatibleEmbedding(client,os.environ['EMBEDDING_BASE_URL'],os.environ['EMBEDDING_API_KEY'],os.getenv('EMBEDDING_MODEL','text-embedding-3-small'),int(os.getenv('EMBEDDING_DIMENSIONS','1536')))
    store=InMemoryVectorStore() if os.getenv('VECTOR_STORE','qdrant')=='memory' else QdrantVectorStore(os.getenv('QDRANT_URL','http://qdrant:6333'),os.getenv('QDRANT_COLLECTION','smartly_knowledge'),os.getenv('QDRANT_API_KEY'))
    app.state.store=store;app.state.search_service=KnowledgeSearchService(embedder,store,max_context_characters=int(os.getenv('MAX_CONTEXT_CHARACTERS','6000')))
    try: yield
    finally: await client.aclose()
app=FastAPI(title='Smartly Knowledge Agent',version='1.0.0',description='Retrieves untrusted documentary evidence; does not orchestrate conversations or authorize actions.',lifespan=lifespan);app.include_router(router);FastAPIInstrumentor.instrument_app(app,excluded_urls='/health')

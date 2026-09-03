import argparse,asyncio,os
from pathlib import Path
import httpx
from app.embeddings import DeterministicEmbedding,OpenAICompatibleEmbedding
from app.ingestion import IngestionPipeline
from app.loader import DocumentLoader
from app.stores import QdrantVectorStore
async def run(path:Path):
    async with httpx.AsyncClient(timeout=10) as client:
        mode=os.getenv('EMBEDDING_PROVIDER','deterministic'); dimensions=int(os.getenv('EMBEDDING_DIMENSIONS','128' if mode=='deterministic' else '1536'))
        embedder=DeterministicEmbedding(dimensions) if mode=='deterministic' else OpenAICompatibleEmbedding(client,os.environ['EMBEDDING_BASE_URL'],os.environ['EMBEDDING_API_KEY'],os.getenv('EMBEDDING_MODEL','text-embedding-3-small'),dimensions)
        store=QdrantVectorStore(os.getenv('QDRANT_URL','http://qdrant:6333'),os.getenv('QDRANT_COLLECTION','smartly_knowledge'),os.getenv('QDRANT_API_KEY'))
        count=await IngestionPipeline(DocumentLoader(),embedder,store).ingest_directory(path);print(f'Upserted {count} deterministic chunks')
def main():
    parser=argparse.ArgumentParser(description='Idempotently ingest governed documents into Qdrant');parser.add_argument('path',type=Path);args=parser.parse_args();asyncio.run(run(args.path))
if __name__=='__main__':main()

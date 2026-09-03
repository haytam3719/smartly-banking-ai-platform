from fastapi import APIRouter, HTTPException, Request
from app.models import SearchRequest, SearchResponse
from app.ports import VectorStoreUnavailable
router=APIRouter()
@router.post('/internal/v1/search',response_model=SearchResponse)
async def search(body:SearchRequest,request:Request)->SearchResponse:
    try: return await request.app.state.search_service.search(body)
    except VectorStoreUnavailable as exc: raise HTTPException(status_code=503,detail={"code":"KNOWLEDGE_STORE_UNAVAILABLE","message":"Knowledge retrieval is temporarily unavailable","retryable":True}) from exc
@router.get('/internal/v1/capabilities')
async def capabilities(): return {"capabilities":["knowledge.search"]}
@router.get('/health',include_in_schema=False)
async def health(request:Request):
    available=await request.app.state.store.health()
    return {"status":"UP" if available else "DEGRADED","qdrant_available":available}

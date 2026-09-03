import os
from typing import Annotated
from fastapi import APIRouter,Header,HTTPException,Request
from orchestrator.models import ChatRequest,ChatResponse,Principal
router=APIRouter()
async def handle(body:ChatRequest,request:Request,authenticated_subject_id:str|None,authenticated_customer_id:str|None,scopes:str|None,channel:str|None):
    dev=os.getenv('DEV_AUTH_MODE','true').lower()=='true'
    if not authenticated_subject_id and not dev:raise HTTPException(401,'Authenticated subject required')
    effective_customer=authenticated_customer_id or (body.customer_id if dev else None)
    if effective_customer!=body.customer_id:raise HTTPException(404,'Customer context not found')
    principal=Principal(subject_id=authenticated_subject_id or f'dev-user-{body.customer_id}',customer_id=effective_customer,scopes=[x.strip() for x in (scopes or 'account:read,card:read,transfer:read,customer:read,knowledge:search,account:open').split(',') if x.strip()],channel=channel or 'INTERNAL')
    return await request.app.state.chat_service.chat(body,principal,request.headers.get('X-Request-Id'),request.headers.get('X-Correlation-Id'))
@router.post('/chat',response_model=ChatResponse)
@router.post('/api/v1/chat',response_model=ChatResponse)
async def chat(body:ChatRequest,request:Request,authenticated_subject_id:Annotated[str|None,Header(alias='X-Authenticated-Subject-Id')]=None,authenticated_customer_id:Annotated[str|None,Header(alias='X-Authenticated-Customer-Id')]=None,scopes:Annotated[str|None,Header(alias='X-Scopes')]=None,channel:Annotated[str|None,Header(alias='X-Channel')]=None):return await handle(body,request,authenticated_subject_id,authenticated_customer_id,scopes,channel)
@router.get('/health/live',include_in_schema=False)
async def live():return {'status':'UP'}
@router.get('/health/ready',include_in_schema=False)
async def ready(request:Request):
    registry,policy=await __import__('asyncio').gather(request.app.state.registry.health(),request.app.state.policy.health());return {'status':'UP' if registry and policy else 'DEGRADED','registry':registry,'policy':policy}

from typing import Annotated
from fastapi import APIRouter,Depends,Header,Request
from card_agent.models import AgentRequest,AgentResponse,CAPABILITY
from card_agent.service import CardCapabilityService
router=APIRouter()
def service(request:Request)->CardCapabilityService:return request.app.state.service
@router.post("/internal/v1/capabilities/card.info.read",response_model=AgentResponse)
async def card_info(request:AgentRequest,capability_service:Annotated[CardCapabilityService,Depends(service)],trusted_customer_id:Annotated[str|None,Header(alias="X-Authenticated-Customer-Id")]=None)->AgentResponse:
    return await capability_service.execute(request,trusted_customer_id)
@router.get("/internal/v1/capabilities")
async def capabilities()->dict[str,list[str]]:return {"capabilities":[CAPABILITY]}
@router.get("/health",include_in_schema=False)
async def health()->dict[str,str]:return {"status":"UP"}


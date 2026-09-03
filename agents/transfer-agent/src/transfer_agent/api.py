from typing import Annotated
from fastapi import APIRouter, Depends, Header, Request
from transfer_agent.models import AgentRequest, AgentResponse, CAPABILITY
from transfer_agent.service import TransferCapabilityService

router = APIRouter()
def service(request: Request) -> TransferCapabilityService: return request.app.state.service

@router.post("/internal/v1/capabilities/transfer.status.read", response_model=AgentResponse)
async def transfer_status(request: AgentRequest, capability_service: Annotated[TransferCapabilityService, Depends(service)], trusted_customer_id: Annotated[str | None, Header(alias="X-Authenticated-Customer-Id")] = None, traceparent: Annotated[str | None, Header(pattern=r"^[\da-f]{2}-[\da-f]{32}-[\da-f]{16}-[\da-f]{2}$")] = None) -> AgentResponse:
    return await capability_service.execute(request, trusted_customer_id, traceparent)

@router.get("/internal/v1/capabilities")
async def capabilities() -> dict[str, list[str]]: return {"capabilities": [CAPABILITY]}

@router.get("/health", include_in_schema=False)
async def health() -> dict[str, str]: return {"status": "UP"}

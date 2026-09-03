from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request

from account_agent.models import AgentRequest, AgentResponse, Capability
from account_agent.service import AccountCapabilityService

router = APIRouter()


def service(request: Request) -> AccountCapabilityService:
    return request.app.state.service


@router.post("/internal/v1/capabilities/account.balance.read", response_model=AgentResponse)
async def balance(
    request: AgentRequest,
    capability_service: Annotated[AccountCapabilityService, Depends(service)],
    trusted_customer_id: Annotated[str | None, Header(alias="X-Authenticated-Customer-Id")] = None,
) -> AgentResponse:
    return await capability_service.execute(Capability.BALANCE_READ, request, trusted_customer_id)


@router.post("/internal/v1/capabilities/account.transactions.read", response_model=AgentResponse)
async def transactions(
    request: AgentRequest,
    capability_service: Annotated[AccountCapabilityService, Depends(service)],
    trusted_customer_id: Annotated[str | None, Header(alias="X-Authenticated-Customer-Id")] = None,
) -> AgentResponse:
    return await capability_service.execute(Capability.TRANSACTIONS_READ, request, trusted_customer_id)


@router.get("/internal/v1/capabilities")
async def capabilities() -> dict[str, list[str]]:
    return {"capabilities": [capability.value for capability in Capability]}


@router.get("/health", include_in_schema=False)
async def health() -> dict[str, str]:
    return {"status": "UP"}

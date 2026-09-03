from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from agent_registry.health import AgentHealthService
from agent_registry.models import AgentDefinition, Capability, RegistryHealthResponse, ResolutionResponse
from agent_registry.repository import YamlAgentRepository

router = APIRouter(prefix="/internal/v1")
logger = logging.getLogger(__name__)


def repository(request: Request) -> YamlAgentRepository:
    return request.app.state.repository


def health_service(request: Request) -> AgentHealthService:
    return request.app.state.health_service


@router.get("/agents", response_model=list[AgentDefinition])
async def list_agents(repo: Annotated[YamlAgentRepository, Depends(repository)]) -> list[AgentDefinition]:
    return repo.list()


@router.get("/agents/{agent_id}", response_model=AgentDefinition)
async def get_agent(agent_id: str, repo: Annotated[YamlAgentRepository, Depends(repository)]) -> AgentDefinition:
    agent = repo.get(agent_id)
    if agent is None:
        raise RegistryNotFound("AGENT_NOT_FOUND", "Agent not found")
    return agent


@router.get("/capabilities/{capability}", response_model=ResolutionResponse)
async def resolve_capability(capability: str, repo: Annotated[YamlAgentRepository, Depends(repository)]) -> ResolutionResponse:
    try:
        canonical = Capability(capability)
    except ValueError as exc:
        raise RegistryNotFound("CAPABILITY_NOT_FOUND", "Capability not found") from exc
    agent = repo.resolve(canonical)
    if agent is None:
        raise RegistryNotFound("CAPABILITY_NOT_FOUND", "Capability not found")
    logger.info("capability_resolved", extra={"capability": canonical.value, "agent_id": agent.id})
    return ResolutionResponse(capability=canonical, agent_id=agent.id, base_url=str(agent.base_url).rstrip("/"), version=agent.version, timeout_ms=agent.timeout_ms)


@router.get("/health/agents", response_model=RegistryHealthResponse)
async def agents_health(repo: Annotated[YamlAgentRepository, Depends(repository)], service: Annotated[AgentHealthService, Depends(health_service)]) -> RegistryHealthResponse:
    return await service.check(repo.list())


class RegistryNotFound(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message


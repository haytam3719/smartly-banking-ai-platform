from __future__ import annotations

import asyncio
from time import perf_counter
from typing import Callable

import httpx

from agent_registry.models import AgentDefinition, AgentHealth, HealthProbingConfig, RegistryHealthResponse


class AgentHealthService:
    def __init__(self, config: HealthProbingConfig, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._config = config
        self._transport = transport

    async def check(self, agents: list[AgentDefinition]) -> RegistryHealthResponse:
        results = await asyncio.gather(*(self._check_one(agent) for agent in agents), return_exceptions=True)
        safe_results: list[AgentHealth] = []
        for agent, result in zip(agents, results, strict=True):
            if isinstance(result, BaseException):
                safe_results.append(AgentHealth(agent_id=agent.id, enabled=agent.enabled, availability="UNAVAILABLE", checked=True))
            else:
                safe_results.append(result)
        degraded = any(result.availability == "UNAVAILABLE" for result in safe_results if result.enabled)
        return RegistryHealthResponse(status="DEGRADED" if degraded else "UP", agents=safe_results)

    async def _check_one(self, agent: AgentDefinition) -> AgentHealth:
        if not agent.enabled:
            return AgentHealth(agent_id=agent.id, enabled=False, availability="DISABLED", checked=False)
        if not self._config.enabled:
            return AgentHealth(agent_id=agent.id, enabled=True, availability="UNKNOWN", checked=False)
        started = perf_counter()
        url = f"{str(agent.base_url).rstrip('/')}{self._config.path}"
        try:
            async with httpx.AsyncClient(transport=self._transport, timeout=self._config.timeout_ms / 1000) as client:
                response = await client.get(url)
            latency_ms = round((perf_counter() - started) * 1000)
            available = 200 <= response.status_code < 300
            return AgentHealth(agent_id=agent.id, enabled=True, availability="AVAILABLE" if available else "UNAVAILABLE", checked=True, latency_ms=latency_ms, status_code=response.status_code)
        except httpx.HTTPError:
            return AgentHealth(agent_id=agent.id, enabled=True, availability="UNAVAILABLE", checked=True, latency_ms=round((perf_counter() - started) * 1000))


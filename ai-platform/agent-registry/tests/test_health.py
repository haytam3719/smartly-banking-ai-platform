from __future__ import annotations

import httpx

from agent_registry.health import AgentHealthService
from agent_registry.models import AgentDefinition, HealthProbingConfig


def _agent(agent_id: str, *, enabled: bool = True) -> AgentDefinition:
    return AgentDefinition(id=agent_id, name=agent_id, base_url=f"http://{agent_id}:8080", version="1.0.0", capabilities=["knowledge.search"], timeout_ms=500, enabled=enabled)


async def test_health_probe_isolates_agent_failures():
    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "healthy-agent":
            return httpx.Response(200, json={"status": "UP"})
        return httpx.Response(503)

    service = AgentHealthService(HealthProbingConfig(enabled=True, path="/health", timeout_ms=200), transport=httpx.MockTransport(handler))
    result = await service.check([_agent("healthy-agent"), _agent("down-agent"), _agent("disabled-agent", enabled=False)])
    assert result.status == "DEGRADED"
    assert [(item.agent_id, item.availability) for item in result.agents] == [
        ("healthy-agent", "AVAILABLE"), ("down-agent", "UNAVAILABLE"), ("disabled-agent", "DISABLED")
    ]


async def test_probing_disabled_returns_unknown_without_network():
    service = AgentHealthService(HealthProbingConfig(enabled=False))
    result = await service.check([_agent("unprobed-agent")])
    assert result.status == "UP"
    assert result.agents[0].availability == "UNKNOWN"
    assert result.agents[0].checked is False


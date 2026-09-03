from __future__ import annotations

from agent_registry.api import repository
from agent_registry.models import RegistryConfig
from agent_registry.repository import YamlAgentRepository


async def test_capability_resolution_returns_minimal_orchestrator_contract(app_client):
    _, client = app_client
    response = await client.get("/internal/v1/capabilities/transfer.status.read", headers={"X-Request-Id": "req-1"})
    assert response.status_code == 200
    assert response.json() == {
        "capability": "transfer.status.read",
        "agent_id": "transfer-agent",
        "base_url": "http://transfer-agent:8080",
        "version": "1.0.0",
        "timeout_ms": 1500,
    }
    assert response.headers["X-Request-Id"] == "req-1"


async def test_unknown_capability_is_clean_not_found(app_client):
    _, client = app_client
    response = await client.get("/internal/v1/capabilities/not.a.capability")
    assert response.status_code == 404
    assert response.json()["code"] == "CAPABILITY_NOT_FOUND"
    assert response.json()["retryable"] is False


async def test_disabled_agent_is_not_resolved(app_client):
    app, client = app_client
    raw = {
        "schema_version": 1,
        "agents": [{
            "id": "transfer-agent", "name": "Transfer Agent", "base_url": "http://transfer-agent:8080",
            "version": "1.0.0", "capabilities": ["transfer.status.read"], "timeout_ms": 500,
            "enabled": False, "metadata": {},
        }],
    }
    repo = YamlAgentRepository(RegistryConfig.model_validate(raw))
    app.dependency_overrides[repository] = lambda: repo
    try:
        response = await client.get("/internal/v1/capabilities/transfer.status.read")
        assert response.status_code == 404
        assert response.json()["code"] == "CAPABILITY_NOT_FOUND"
        details = await client.get("/internal/v1/agents/transfer-agent")
        assert details.status_code == 200
        assert details.json()["enabled"] is False
    finally:
        app.dependency_overrides.clear()


async def test_agent_listing_and_lookup(app_client):
    _, client = app_client
    agents = await client.get("/internal/v1/agents")
    assert agents.status_code == 200
    assert len(agents.json()) == 6
    workflow = await client.get("/internal/v1/agents/account-opening-workflow")
    assert workflow.json()["capabilities"] == ["account.opening.start", "account.opening.status"]


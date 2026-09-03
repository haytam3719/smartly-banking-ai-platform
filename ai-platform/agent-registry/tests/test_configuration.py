from __future__ import annotations

from pathlib import Path

import pytest

from agent_registry.models import RegistryConfig
from agent_registry.repository import RegistryConfigurationError, YamlAgentRepository


def _agent(agent_id: str, capability: str, *, priority: int = 0) -> dict:
    return {
        "id": agent_id,
        "name": agent_id,
        "base_url": f"http://{agent_id}:8080",
        "version": "1.0.0",
        "capabilities": [capability],
        "timeout_ms": 500,
        "enabled": True,
        "metadata": {},
        "priority": priority,
    }


def test_duplicate_capability_is_rejected_by_default():
    config = RegistryConfig.model_validate({"schema_version": 1, "agents": [_agent("agent-one", "card.info.read"), _agent("agent-two", "card.info.read")]})
    with pytest.raises(RegistryConfigurationError, match="duplicate capability ownership"):
        YamlAgentRepository(config)


def test_explicit_duplicate_configuration_uses_priority():
    config = RegistryConfig.model_validate({
        "schema_version": 1,
        "allow_duplicate_capabilities": True,
        "agents": [_agent("agent-one", "card.info.read", priority=10), _agent("agent-two", "card.info.read", priority=20)],
    })
    assert YamlAgentRepository(config).resolve(config.agents[0].capabilities[0]).id == "agent-two"


@pytest.mark.parametrize("content", [
    "not: [valid",
    "schema_version: 1\nagents:\n  - id: bad\n    base_url: not-a-url",
    "schema_version: 2\nagents: []",
])
def test_malformed_configuration_fails_startup_safely(tmp_path: Path, content: str):
    path = tmp_path / "agents.yaml"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(RegistryConfigurationError, match="configuration is invalid"):
        YamlAgentRepository.load(path)


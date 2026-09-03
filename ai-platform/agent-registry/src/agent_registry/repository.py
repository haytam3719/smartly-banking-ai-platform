from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import yaml
from pydantic import ValidationError

from agent_registry.models import AgentDefinition, Capability, RegistryConfig


class RegistryConfigurationError(ValueError):
    """Safe configuration error raised before the service accepts traffic."""


class YamlAgentRepository:
    def __init__(self, config: RegistryConfig) -> None:
        self.config = config
        self._by_id: dict[str, AgentDefinition] = {}
        owners: dict[Capability, list[AgentDefinition]] = defaultdict(list)
        for agent in config.agents:
            if agent.id in self._by_id:
                raise RegistryConfigurationError(f"duplicate agent id: {agent.id}")
            self._by_id[agent.id] = agent
            for capability in agent.capabilities:
                owners[capability].append(agent)
        duplicates = {capability: agents for capability, agents in owners.items() if len(agents) > 1}
        if duplicates and not config.allow_duplicate_capabilities:
            names = ", ".join(sorted(capability.value for capability in duplicates))
            raise RegistryConfigurationError(f"duplicate capability ownership: {names}")
        self._owners = {
            capability: tuple(sorted(agents, key=lambda agent: (-agent.priority, agent.id)))
            for capability, agents in owners.items()
        }

    @classmethod
    def load(cls, path: Path) -> "YamlAgentRepository":
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            config = RegistryConfig.model_validate(raw)
        except (OSError, yaml.YAMLError, ValidationError, TypeError) as exc:
            raise RegistryConfigurationError("agent registry configuration is invalid") from exc
        return cls(config)

    def list(self) -> list[AgentDefinition]:
        return sorted(self._by_id.values(), key=lambda agent: agent.id)

    def get(self, agent_id: str) -> AgentDefinition | None:
        return self._by_id.get(agent_id)

    def resolve(self, capability: Capability) -> AgentDefinition | None:
        return next((agent for agent in self._owners.get(capability, ()) if agent.enabled), None)


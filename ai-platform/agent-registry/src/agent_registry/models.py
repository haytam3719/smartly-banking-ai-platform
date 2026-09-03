from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_serializer, field_validator


class Capability(StrEnum):
    ACCOUNT_BALANCE_READ = "account.balance.read"
    ACCOUNT_TRANSACTIONS_READ = "account.transactions.read"
    CARD_INFO_READ = "card.info.read"
    TRANSFER_STATUS_READ = "transfer.status.read"
    CUSTOMER_INFO_READ = "customer.info.read"
    KNOWLEDGE_SEARCH = "knowledge.search"
    ACCOUNT_OPENING_START = "account.opening.start"
    ACCOUNT_OPENING_STATUS = "account.opening.status"


class AgentDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z][a-z0-9-]{1,62}$")
    name: str = Field(min_length=1, max_length=128)
    base_url: AnyHttpUrl
    version: str = Field(pattern=r"^\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?$")
    capabilities: list[Capability] = Field(min_length=1)
    timeout_ms: int = Field(ge=50, le=30_000)
    enabled: bool = True
    metadata: dict[str, str] = Field(default_factory=dict)
    priority: int = Field(default=0, ge=0, le=1000)

    @field_validator("capabilities")
    @classmethod
    def unique_capabilities(cls, capabilities: list[Capability]) -> list[Capability]:
        if len(capabilities) != len(set(capabilities)):
            raise ValueError("agent capabilities must be unique")
        return capabilities

    @field_serializer("base_url")
    def serialize_url(self, value: AnyHttpUrl) -> str:
        return str(value).rstrip("/")


class HealthProbingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = False
    path: str = Field(default="/health", pattern=r"^/[A-Za-z0-9/_-]*$")
    timeout_ms: int = Field(default=500, ge=50, le=10_000)


class RegistryConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: int = Field(ge=1, le=1)
    allow_duplicate_capabilities: bool = False
    health_probing: HealthProbingConfig = Field(default_factory=HealthProbingConfig)
    agents: list[AgentDefinition] = Field(min_length=1)


class ResolutionResponse(BaseModel):
    capability: Capability
    agent_id: str
    base_url: str
    version: str
    timeout_ms: int


class AgentHealth(BaseModel):
    agent_id: str
    enabled: bool
    availability: str
    checked: bool
    latency_ms: int | None = None
    status_code: int | None = None


class RegistryHealthResponse(BaseModel):
    status: str
    agents: list[AgentHealth]


class ErrorResponse(BaseModel):
    code: str
    message: str
    request_id: str
    retryable: bool

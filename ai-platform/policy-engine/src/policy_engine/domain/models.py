from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Role(StrEnum):
    CUSTOMER = "CUSTOMER"
    EMPLOYEE = "EMPLOYEE"
    SERVICE = "SERVICE"


class Channel(StrEnum):
    MOBILE = "MOBILE"
    WEB = "WEB"
    INTERNAL = "INTERNAL"


class Subject(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=128)
    roles: list[Role] = Field(min_length=1, max_length=16)
    scopes: list[str] = Field(default_factory=list, max_length=64)


class AuthorizationRequest(BaseModel):
    """A proposed action. Fields in this body are claims, not authentication."""

    model_config = ConfigDict(extra="forbid")

    subject: Subject | None = None
    customer_id: str | None = Field(default=None, min_length=1, max_length=128)
    capability: str = Field(min_length=1, max_length=128)
    resource: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] | None = None


class Obligation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    parameters: dict[str, str] = Field(default_factory=dict)


class AuthorizationResponse(BaseModel):
    allowed: bool
    decision_id: str
    reason_code: str
    obligations: list[Obligation] = Field(default_factory=list)


class AuthenticatedPrincipal(BaseModel):
    """Identity asserted by a trusted authentication boundary, never request JSON."""

    subject_id: str | None
    customer_id: str | None


class PolicyDecision(BaseModel):
    allowed: bool
    reason_code: str
    obligations: list[Obligation] = Field(default_factory=list)


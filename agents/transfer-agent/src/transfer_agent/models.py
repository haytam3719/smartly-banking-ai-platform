from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

CAPABILITY = "transfer.status.read"

class AgentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: str = Field(min_length=1, max_length=128)
    correlation_id: str = Field(min_length=1, max_length=128)
    conversation_id: str = Field(min_length=1, max_length=128)
    subject: str = Field(min_length=1, max_length=256)
    customer_id: str = Field(min_length=1, max_length=128)
    capability: str = Field(min_length=1, max_length=128)
    arguments: dict[str, Any]
    locale: str = Field(pattern=r"^[a-z]{2,3}(?:-[A-Z]{2})?$")

class ErrorResponse(BaseModel):
    code: str
    message: str
    request_id: str
    retryable: bool

class AgentResponse(BaseModel):
    success: bool
    capability: str
    data: Any
    error: ErrorResponse | None
    metadata: dict[str, Any]
    latency_ms: int = Field(ge=0)

class TransferArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")
    transfer_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._-]+$")

class TransferInfo(BaseModel):
    transfer_id: str
    amount: Decimal = Field(ge=0)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    beneficiary: str
    created_at: datetime
    status: str
    rejection_reason: str | None

class PolicyFacts(BaseModel):
    status: str
    rejection_reason: str | None

class CallContext(BaseModel):
    request_id: str
    correlation_id: str
    conversation_id: str
    traceparent: str | None = Field(default=None, pattern=r"^[\da-f]{2}-[\da-f]{32}-[\da-f]{16}-[\da-f]{2}$")

from typing import Any
from pydantic import BaseModel, ConfigDict, Field

CAPABILITY = "customer.info.read"

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

class CustomerProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    customer_id: str
    segment: str
    kyc_status: str
    country: str = Field(pattern=r"^[A-Z]{2}$")

class CallContext(BaseModel):
    request_id: str
    correlation_id: str
    conversation_id: str
    traceparent: str | None = Field(default=None, pattern=r"^[\da-f]{2}-[\da-f]{32}-[\da-f]{16}-[\da-f]{2}$")

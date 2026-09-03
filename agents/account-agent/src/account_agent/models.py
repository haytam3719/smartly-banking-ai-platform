from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Capability(StrEnum):
    BALANCE_READ = "account.balance.read"
    TRANSACTIONS_READ = "account.transactions.read"


class AgentRequest(BaseModel):
    """Pydantic representation of the canonical shared AgentRequest schema."""

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


class TransactionArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start_date: date | None = None
    end_date: date | None = None
    limit: int = Field(default=50, ge=1, le=100)

    @model_validator(mode="after")
    def dates_in_order(self) -> "TransactionArguments":
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_date must not be after end_date")
        return self


class BalanceArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AccountBalance(BaseModel):
    available_balance: Decimal
    currency: str
    account_type: str
    status: str


class NormalizedTransaction(BaseModel):
    transaction_id: str
    account_id: str
    type: str
    amount: Decimal
    currency: str
    merchant: str | None
    description: str | None
    occurred_at: datetime
    status: str


class CallContext(BaseModel):
    request_id: str
    correlation_id: str
    conversation_id: str


from __future__ import annotations

from datetime import date
from typing import Any

import httpx
from opentelemetry.propagate import inject
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from account_agent.metrics import DOWNSTREAM_ERRORS
from account_agent.models import AccountBalance, CallContext, NormalizedTransaction
from account_agent.ports import AccountPortError, CustomerNotFound, DownstreamTimeout, DownstreamUnavailable


class _RetryableRequest(Exception):
    def __init__(self, kind: str) -> None:
        self.kind = kind


class _BackendAccount(BaseModel):
    model_config = ConfigDict(extra="ignore")
    available_balance: Any
    currency: str
    type: str
    status: str


class _BalanceEnvelope(BaseModel):
    accounts: list[_BackendAccount]


class _BackendTransaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    transaction_id: str
    account_id: str
    type: str
    amount: Any
    currency: str
    merchant: str | None = None
    description: str | None = None
    occurred_at: str
    status: str


class _TransactionsEnvelope(BaseModel):
    transactions: list[_BackendTransaction]


class CoreBankingAccountAdapter:
    def __init__(self, client: httpx.AsyncClient, base_url: str, api_key: str | None = None) -> None:
        self._client = client
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key

    async def get_balances(self, customer_id: str, context: CallContext) -> list[AccountBalance]:
        payload = await self._get(f"/internal/v1/customers/{customer_id}/accounts/balance", {}, context)
        try:
            envelope = _BalanceEnvelope.model_validate(payload)
            return [AccountBalance(available_balance=item.available_balance, currency=item.currency, account_type=item.type, status=item.status) for item in envelope.accounts]
        except ValidationError as exc:
            DOWNSTREAM_ERRORS.labels(kind="malformed_response").inc()
            raise AccountPortError("Malformed core banking balance response") from exc

    async def get_transactions(self, customer_id: str, start_date: date | None, end_date: date | None, limit: int, context: CallContext) -> list[NormalizedTransaction]:
        params: dict[str, str | int] = {"limit": limit}
        if start_date is not None:
            params["start_date"] = start_date.isoformat()
        if end_date is not None:
            params["end_date"] = end_date.isoformat()
        payload = await self._get(f"/internal/v1/customers/{customer_id}/transactions", params, context)
        try:
            envelope = _TransactionsEnvelope.model_validate(payload)
            return [NormalizedTransaction.model_validate(item.model_dump()) for item in envelope.transactions]
        except ValidationError as exc:
            DOWNSTREAM_ERRORS.labels(kind="malformed_response").inc()
            raise AccountPortError("Malformed core banking transaction response") from exc

    async def _get(self, path: str, params: dict[str, str | int], context: CallContext) -> Any:
        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=0.01, min=0.01, max=0.05),
                retry=retry_if_exception_type(_RetryableRequest),
                reraise=True,
            ):
                with attempt:
                    return await self._request_once(path, params, context)
        except _RetryableRequest as exc:
            DOWNSTREAM_ERRORS.labels(kind=exc.kind).inc()
            if exc.kind == "timeout":
                raise DownstreamTimeout() from exc
            raise DownstreamUnavailable() from exc
        raise DownstreamUnavailable()

    async def _request_once(self, path: str, params: dict[str, str | int], context: CallContext) -> Any:
        headers = {
            "X-Request-Id": context.request_id,
            "X-Correlation-Id": context.correlation_id,
            "X-Conversation-Id": context.conversation_id,
        }
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        inject(headers)
        try:
            response = await self._client.get(f"{self._base_url}{path}", params=params, headers=headers)
        except httpx.TimeoutException as exc:
            raise _RetryableRequest("timeout") from exc
        except httpx.TransportError as exc:
            raise _RetryableRequest("transport") from exc
        if response.status_code == 404:
            DOWNSTREAM_ERRORS.labels(kind="not_found").inc()
            raise CustomerNotFound()
        if response.status_code >= 500:
            raise _RetryableRequest("server_error")
        if response.status_code >= 400:
            DOWNSTREAM_ERRORS.labels(kind="client_error").inc()
            raise AccountPortError("Core banking rejected the request")
        try:
            return response.json()
        except ValueError as exc:
            DOWNSTREAM_ERRORS.labels(kind="malformed_response").inc()
            raise AccountPortError("Malformed core banking response") from exc


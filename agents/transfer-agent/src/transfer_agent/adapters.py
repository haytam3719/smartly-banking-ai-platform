from __future__ import annotations
import httpx
from opentelemetry.propagate import inject
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, ValidationError
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential
from transfer_agent.metrics import DOWNSTREAM_ERRORS
from transfer_agent.models import CallContext, TransferInfo
from transfer_agent.ports import DownstreamTimeout, DownstreamUnavailable, TransferNotFound, TransferPortError

class _Retryable(Exception):
    def __init__(self, kind: str) -> None: self.kind = kind

class _BackendTransfer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    transfer_id: str
    beneficiary: str
    amount: Decimal
    currency: str
    created_at: datetime
    status: str
    rejection_reason: str | None = None

class CoreBankingTransferAdapter:
    def __init__(self, client: httpx.AsyncClient, base_url: str, api_key: str | None = None) -> None:
        self._client = client
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key

    async def get_transfer(self, customer_id: str, transfer_id: str, context: CallContext) -> TransferInfo:
        payload = await self._get(customer_id, transfer_id, context)
        try:
            transfer = _BackendTransfer.model_validate(payload)
            return TransferInfo.model_validate(transfer.model_dump())
        except (ValidationError, ValueError) as exc:
            DOWNSTREAM_ERRORS.labels(kind="malformed_response").inc()
            raise TransferPortError() from exc

    async def _get(self, customer_id: str, transfer_id: str, context: CallContext):
        try:
            async for attempt in AsyncRetrying(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=.01, min=.01, max=.05), retry=retry_if_exception_type(_Retryable), reraise=True):
                with attempt:
                    return await self._once(customer_id, transfer_id, context)
        except _Retryable as exc:
            DOWNSTREAM_ERRORS.labels(kind=exc.kind).inc()
            if exc.kind == "timeout": raise DownstreamTimeout() from exc
            raise DownstreamUnavailable() from exc
        raise DownstreamUnavailable()

    async def _once(self, customer_id: str, transfer_id: str, context: CallContext):
        headers = {"X-Request-Id": context.request_id, "X-Correlation-Id": context.correlation_id, "X-Conversation-Id": context.conversation_id}
        if context.traceparent: headers["traceparent"] = context.traceparent
        if self._api_key: headers["Authorization"] = f"Bearer {self._api_key}"
        inject(headers)
        url = f"{self._base_url}/internal/v1/customers/{customer_id}/transfers/{transfer_id}"
        try: response = await self._client.get(url, headers=headers)
        except httpx.TimeoutException as exc: raise _Retryable("timeout") from exc
        except httpx.TransportError as exc: raise _Retryable("transport") from exc
        if response.status_code == 404:
            DOWNSTREAM_ERRORS.labels(kind="not_found").inc()
            raise TransferNotFound()
        if response.status_code >= 500: raise _Retryable("server_error")
        if response.status_code >= 400:
            DOWNSTREAM_ERRORS.labels(kind="client_error").inc()
            raise TransferPortError()
        try: return response.json()
        except ValueError as exc:
            DOWNSTREAM_ERRORS.labels(kind="malformed_response").inc()
            raise TransferPortError() from exc

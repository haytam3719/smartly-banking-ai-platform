from __future__ import annotations
from decimal import Decimal
import httpx
from opentelemetry.propagate import inject
from pydantic import BaseModel,ConfigDict,ValidationError
from tenacity import AsyncRetrying,retry_if_exception_type,stop_after_attempt,wait_exponential
from card_agent.metrics import DOWNSTREAM_ERRORS
from card_agent.models import CallContext,CardInfo
from card_agent.ports import CardNotFound,CardPortError,DownstreamTimeout,DownstreamUnavailable

class _Retryable(Exception):
    def __init__(self,kind:str)->None:self.kind=kind

class _BackendCard(BaseModel):
    model_config=ConfigDict(extra="ignore")
    type:str;status:str;expiration_date:str;payment_limit:Decimal;amount_used:Decimal;currency:str

class CoreBankingCardAdapter:
    def __init__(self,client:httpx.AsyncClient,base_url:str,api_key:str|None=None)->None:
        self._client=client;self._base_url=base_url.rstrip("/");self._api_key=api_key
    async def get_primary_card(self,customer_id:str,context:CallContext)->CardInfo:
        payload=await self._get(customer_id,context)
        try:
            card=_BackendCard.model_validate(payload)
            available=max(card.payment_limit-card.amount_used,Decimal("0"))
            return CardInfo(card_type=card.type,status=card.status,expiration_date=card.expiration_date[:7],payment_limit=card.payment_limit,amount_used=card.amount_used,available_limit=available,currency=card.currency)
        except (ValidationError,ValueError) as exc:
            DOWNSTREAM_ERRORS.labels(kind="malformed_response").inc();raise CardPortError() from exc
    async def _get(self,customer_id:str,context:CallContext):
        try:
            async for attempt in AsyncRetrying(stop=stop_after_attempt(3),wait=wait_exponential(multiplier=.01,min=.01,max=.05),retry=retry_if_exception_type(_Retryable),reraise=True):
                with attempt:return await self._once(customer_id,context)
        except _Retryable as exc:
            DOWNSTREAM_ERRORS.labels(kind=exc.kind).inc()
            if exc.kind=="timeout":raise DownstreamTimeout() from exc
            raise DownstreamUnavailable() from exc
        raise DownstreamUnavailable()
    async def _once(self,customer_id:str,context:CallContext):
        headers={"X-Request-Id":context.request_id,"X-Correlation-Id":context.correlation_id,"X-Conversation-Id":context.conversation_id}
        if self._api_key:headers["Authorization"]=f"Bearer {self._api_key}"
        inject(headers)
        try:response=await self._client.get(f"{self._base_url}/internal/v1/customers/{customer_id}/cards/primary",headers=headers)
        except httpx.TimeoutException as exc:raise _Retryable("timeout") from exc
        except httpx.TransportError as exc:raise _Retryable("transport") from exc
        if response.status_code==404:DOWNSTREAM_ERRORS.labels(kind="not_found").inc();raise CardNotFound()
        if response.status_code>=500:raise _Retryable("server_error")
        if response.status_code>=400:DOWNSTREAM_ERRORS.labels(kind="client_error").inc();raise CardPortError()
        try:return response.json()
        except ValueError as exc:DOWNSTREAM_ERRORS.labels(kind="malformed_response").inc();raise CardPortError() from exc


from __future__ import annotations

from time import perf_counter

from pydantic import ValidationError

from account_agent.metrics import CAPABILITY_LATENCY
from account_agent.models import (
    AgentRequest,
    AgentResponse,
    BalanceArguments,
    CallContext,
    Capability,
    ErrorResponse,
    TransactionArguments,
)
from account_agent.ports import AccountPort, AccountPortError


class AccountCapabilityService:
    def __init__(self, port: AccountPort) -> None:
        self._port = port

    async def execute(self, endpoint_capability: Capability, request: AgentRequest, trusted_customer_id: str | None) -> AgentResponse:
        started = perf_counter()
        outcome = "failure"
        try:
            if request.capability != endpoint_capability.value:
                return self._error(request, "UNSUPPORTED_CAPABILITY", "Capability is not supported by this endpoint", False, started)
            if trusted_customer_id is None or trusted_customer_id != request.customer_id:
                return self._error(request, "CUSTOMER_CONTEXT_MISMATCH", "Trusted customer context does not match the request", False, started)
            context = CallContext(request_id=request.request_id, correlation_id=request.correlation_id, conversation_id=request.conversation_id)
            try:
                if endpoint_capability == Capability.BALANCE_READ:
                    BalanceArguments.model_validate(request.arguments)
                    balances = await self._port.get_balances(trusted_customer_id, context)
                    data = {"accounts": [balance.model_dump(mode="json") for balance in balances]}
                else:
                    arguments = TransactionArguments.model_validate(request.arguments)
                    transactions = await self._port.get_transactions(trusted_customer_id, arguments.start_date, arguments.end_date, arguments.limit, context)
                    data = {"transactions": [transaction.model_dump(mode="json") for transaction in transactions]}
            except ValidationError:
                return self._error(request, "INVALID_ARGUMENTS", "Capability arguments are invalid", False, started)
            except AccountPortError as exc:
                return self._error(request, exc.code, exc.safe_message, exc.retryable, started)
            outcome = "success"
            return AgentResponse(success=True, capability=request.capability, data=data, error=None, metadata={"source": "core-banking-simulator"}, latency_ms=_elapsed_ms(started))
        finally:
            CAPABILITY_LATENCY.labels(capability=endpoint_capability.value, outcome=outcome).observe(perf_counter() - started)

    def _error(self, request: AgentRequest, code: str, message: str, retryable: bool, started: float) -> AgentResponse:
        return AgentResponse(success=False, capability=request.capability, data=None, error=ErrorResponse(code=code, message=message, request_id=request.request_id, retryable=retryable), metadata={}, latency_ms=_elapsed_ms(started))


def _elapsed_ms(started: float) -> int:
    return max(0, round((perf_counter() - started) * 1000))


from time import perf_counter
from pydantic import ValidationError
from transfer_agent.metrics import CAPABILITY_LATENCY
from transfer_agent.models import AgentRequest, AgentResponse, CAPABILITY, CallContext, ErrorResponse, PolicyFacts, TransferArguments, TransferInfo
from transfer_agent.ports import TransferPort, TransferPortError

class TransferCapabilityService:
    def __init__(self, port: TransferPort) -> None: self._port = port

    async def execute(self, request: AgentRequest, trusted_customer_id: str | None, traceparent: str | None = None) -> AgentResponse:
        started = perf_counter()
        outcome = "failure"
        try:
            if request.capability != CAPABILITY:
                return self._error(request, "UNSUPPORTED_CAPABILITY", "Capability is not supported by this agent", False, started)
            try: arguments = TransferArguments.model_validate(request.arguments)
            except ValidationError:
                return self._error(request, "INVALID_ARGUMENTS", "A valid transfer_id is required", False, started)
            if trusted_customer_id is None or trusted_customer_id != request.customer_id:
                return self._error(request, "CUSTOMER_CONTEXT_MISMATCH", "Trusted customer context does not match the request", False, started)
            context = CallContext(request_id=request.request_id, correlation_id=request.correlation_id, conversation_id=request.conversation_id, traceparent=traceparent)
            try: transfer = await self._port.get_transfer(trusted_customer_id, arguments.transfer_id, context)
            except TransferPortError as exc:
                return self._error(request, exc.code, exc.safe_message, exc.retryable, started)
            outcome = "success"
            return AgentResponse(success=True, capability=CAPABILITY, data=transfer.model_dump(mode="json"), error=None, metadata={"source": "core-banking-simulator"}, latency_ms=_elapsed(started))
        finally:
            CAPABILITY_LATENCY.labels(outcome=outcome).observe(perf_counter() - started)

    @staticmethod
    def policy_facts(transfer: TransferInfo) -> PolicyFacts:
        return PolicyFacts(status=transfer.status, rejection_reason=transfer.rejection_reason)

    def _error(self, request: AgentRequest, code: str, message: str, retryable: bool, started: float) -> AgentResponse:
        return AgentResponse(success=False, capability=request.capability, data=None, error=ErrorResponse(code=code, message=message, request_id=request.request_id, retryable=retryable), metadata={}, latency_ms=_elapsed(started))

def _elapsed(started: float) -> int: return max(0, round((perf_counter() - started) * 1000))

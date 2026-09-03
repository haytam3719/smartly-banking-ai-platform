from time import perf_counter
from customer_agent.metrics import CAPABILITY_LATENCY
from customer_agent.models import AgentRequest, AgentResponse, CAPABILITY, CallContext, ErrorResponse
from customer_agent.ports import CustomerPort, CustomerPortError

class CustomerService:
    def __init__(self, port: CustomerPort) -> None: self._port = port
    async def execute(self, request: AgentRequest, trusted_customer_id: str | None, traceparent: str | None = None) -> AgentResponse:
        started = perf_counter(); outcome = "failure"
        try:
            if request.capability != CAPABILITY: return self._error(request, "UNSUPPORTED_CAPABILITY", "Capability is not supported by this agent", False, started)
            if request.arguments: return self._error(request, "INVALID_ARGUMENTS", "customer.info.read does not accept arguments", False, started)
            if trusted_customer_id is None or trusted_customer_id != request.customer_id: return self._error(request, "CUSTOMER_CONTEXT_MISMATCH", "Trusted customer context does not match the request", False, started)
            context = CallContext(request_id=request.request_id, correlation_id=request.correlation_id, conversation_id=request.conversation_id, traceparent=traceparent)
            try: profile = await self._port.get_customer(trusted_customer_id, context)
            except CustomerPortError as exc: return self._error(request, exc.code, exc.safe_message, exc.retryable, started)
            outcome = "success"
            return AgentResponse(success=True, capability=CAPABILITY, data=profile.model_dump(mode="json"), error=None, metadata={"source":"core-banking-simulator"}, latency_ms=_elapsed(started))
        finally: CAPABILITY_LATENCY.labels(outcome=outcome).observe(perf_counter() - started)
    def _error(self, request, code, message, retryable, started):
        return AgentResponse(success=False, capability=request.capability, data=None, error=ErrorResponse(code=code, message=message, request_id=request.request_id, retryable=retryable), metadata={}, latency_ms=_elapsed(started))
def _elapsed(started: float) -> int: return max(0, round((perf_counter() - started) * 1000))

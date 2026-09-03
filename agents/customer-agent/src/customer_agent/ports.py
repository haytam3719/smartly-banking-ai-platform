from typing import Protocol
from customer_agent.models import CallContext, CustomerProfile

class CustomerPort(Protocol):
    async def get_customer(self, customer_id: str, context: CallContext) -> CustomerProfile: ...

class CustomerPortError(Exception):
    code = "CUSTOMER_LOOKUP_FAILED"
    safe_message = "Customer profile could not be reliably retrieved"
    retryable = False

class CustomerNotFound(CustomerPortError):
    code = "CUSTOMER_NOT_FOUND"
    safe_message = "Customer not found"

class DownstreamTimeout(CustomerPortError):
    code = "CORE_BANKING_TIMEOUT"
    retryable = True

class DownstreamUnavailable(CustomerPortError):
    code = "CORE_BANKING_UNAVAILABLE"
    retryable = True

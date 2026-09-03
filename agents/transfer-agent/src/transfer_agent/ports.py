from typing import Protocol
from transfer_agent.models import CallContext, TransferInfo

class TransferPort(Protocol):
    async def get_transfer(self, customer_id: str, transfer_id: str, context: CallContext) -> TransferInfo: ...

class TransferPortError(Exception):
    code = "TRANSFER_LOOKUP_FAILED"
    safe_message = "Transfer status could not be reliably retrieved"
    retryable = False

class TransferNotFound(TransferPortError):
    code = "TRANSFER_NOT_FOUND"
    safe_message = "Transfer not found"

class DownstreamTimeout(TransferPortError):
    code = "CORE_BANKING_TIMEOUT"
    retryable = True

class DownstreamUnavailable(TransferPortError):
    code = "CORE_BANKING_UNAVAILABLE"
    retryable = True

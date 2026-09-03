from typing import Protocol
from card_agent.models import CallContext,CardInfo

class CardPort(Protocol):
    async def get_primary_card(self,customer_id:str,context:CallContext)->CardInfo:...

class CardPortError(Exception):
    code="DOWNSTREAM_ERROR";safe_message="Card information is temporarily unavailable";retryable=False
class CardNotFound(CardPortError):
    code="CARD_NOT_FOUND";safe_message="Card information not found"
class DownstreamTimeout(CardPortError):
    code="CORE_BANKING_TIMEOUT";safe_message="Card information request timed out";retryable=True
class DownstreamUnavailable(CardPortError):
    code="CORE_BANKING_UNAVAILABLE";retryable=True


from __future__ import annotations

from datetime import date
from typing import Protocol

from account_agent.models import AccountBalance, CallContext, NormalizedTransaction


class AccountPort(Protocol):
    async def get_balances(self, customer_id: str, context: CallContext) -> list[AccountBalance]: ...

    async def get_transactions(
        self,
        customer_id: str,
        start_date: date | None,
        end_date: date | None,
        limit: int,
        context: CallContext,
    ) -> list[NormalizedTransaction]: ...


class AccountPortError(Exception):
    code = "DOWNSTREAM_ERROR"
    safe_message = "Account data is temporarily unavailable"
    retryable = False


class CustomerNotFound(AccountPortError):
    code = "CUSTOMER_NOT_FOUND"
    safe_message = "Customer not found"


class DownstreamUnavailable(AccountPortError):
    code = "CORE_BANKING_UNAVAILABLE"
    retryable = True


class DownstreamTimeout(AccountPortError):
    code = "CORE_BANKING_TIMEOUT"
    safe_message = "Account data request timed out"
    retryable = True


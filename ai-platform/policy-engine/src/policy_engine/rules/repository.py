from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CapabilityRule:
    capability: str
    required_scope: str
    customer_scoped: bool
    reason_code: str
    description: str


class RuleRepository:
    """Static, reviewable rules; deliberately not a general-purpose rule language."""

    _RULES = (
        CapabilityRule("account.balance.read", "account:read", True, "ALLOW_CUSTOMER_READ", "Read balances owned by the authenticated customer."),
        CapabilityRule("account.transactions.read", "account:read", True, "ALLOW_CUSTOMER_READ", "Read transactions owned by the authenticated customer."),
        CapabilityRule("card.info.read", "card:read", True, "ALLOW_CUSTOMER_READ", "Read card information owned by the authenticated customer."),
        CapabilityRule("transfer.status.read", "transfer:read", True, "ALLOW_CUSTOMER_READ", "Read transfer status owned by the authenticated customer."),
        CapabilityRule("customer.info.read", "customer:read", True, "ALLOW_CUSTOMER_READ", "Read the authenticated customer's profile."),
        CapabilityRule("knowledge.search", "knowledge:search", False, "ALLOW_KNOWLEDGE_SEARCH", "Search the governed knowledge corpus without a customer resource."),
        CapabilityRule("account.opening.start", "account:open", True, "ALLOW_ACCOUNT_OPENING", "Start account opening for the authenticated customer."),
        CapabilityRule("account.opening.status", "account:open", True, "ALLOW_ACCOUNT_OPENING", "Read account-opening status for the authenticated customer."),
    )

    def __init__(self) -> None:
        self._by_capability = {rule.capability: rule for rule in self._RULES}

    def get(self, capability: str) -> CapabilityRule | None:
        return self._by_capability.get(capability)

    def all(self) -> tuple[CapabilityRule, ...]:
        return self._RULES


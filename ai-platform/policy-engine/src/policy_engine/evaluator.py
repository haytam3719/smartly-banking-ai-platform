from __future__ import annotations

from typing import Protocol

from policy_engine.domain.models import (
    AuthenticatedPrincipal,
    AuthorizationRequest,
    Channel,
    PolicyDecision,
    Role,
)
from policy_engine.rules.repository import RuleRepository


class PolicyEvaluator(Protocol):
    """Adapter seam for a future OPA/Rego-backed evaluator."""

    async def evaluate(self, request: AuthorizationRequest, principal: AuthenticatedPrincipal) -> PolicyDecision: ...


class InProcessPolicyEvaluator:
    def __init__(self, rules: RuleRepository) -> None:
        self._rules = rules

    async def evaluate(self, request: AuthorizationRequest, principal: AuthenticatedPrincipal) -> PolicyDecision:
        rule = self._rules.get(request.capability)
        if rule is None:
            return _deny("DENY_UNKNOWN_CAPABILITY")
        if request.subject is None or principal.subject_id is None:
            return _deny("DENY_MISSING_SUBJECT")
        if request.subject.id != principal.subject_id:
            return _deny("DENY_SUBJECT_MISMATCH")
        if Role.CUSTOMER not in request.subject.roles:
            return _deny("DENY_ROLE_NOT_ALLOWED")
        if not _valid_context(request.context):
            return _deny("DENY_MALFORMED_CONTEXT")
        if rule.required_scope not in request.subject.scopes:
            return _deny("DENY_MISSING_SCOPE")
        if rule.customer_scoped:
            if request.customer_id is None or principal.customer_id is None:
                return _deny("DENY_MISSING_CUSTOMER_CONTEXT")
            if request.customer_id != principal.customer_id:
                return _deny("DENY_CUSTOMER_MISMATCH")
        return PolicyDecision(allowed=True, reason_code=rule.reason_code)


def _valid_context(context: dict[str, object] | None) -> bool:
    if context is None or set(context) != {"channel"}:
        return False
    try:
        Channel(context["channel"])
    except (ValueError, TypeError):
        return False
    return True


def _deny(reason_code: str) -> PolicyDecision:
    return PolicyDecision(allowed=False, reason_code=reason_code)


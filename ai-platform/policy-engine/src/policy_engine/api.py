from __future__ import annotations

import logging
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, Header

from policy_engine.audit import AuditAdapter, StructuredLogAuditAdapter
from policy_engine.domain.models import AuthenticatedPrincipal, AuthorizationRequest, AuthorizationResponse
from policy_engine.evaluator import InProcessPolicyEvaluator, PolicyEvaluator
from policy_engine.rules.repository import RuleRepository

router = APIRouter()
logger = logging.getLogger(__name__)
_evaluator: PolicyEvaluator = InProcessPolicyEvaluator(RuleRepository())
_audit: AuditAdapter = StructuredLogAuditAdapter()


def get_evaluator() -> PolicyEvaluator:
    return _evaluator


def get_audit_adapter() -> AuditAdapter:
    return _audit


async def trusted_principal(
    subject_id: Annotated[str | None, Header(alias="X-Authenticated-Subject-Id")] = None,
    customer_id: Annotated[str | None, Header(alias="X-Authenticated-Customer-Id")] = None,
) -> AuthenticatedPrincipal:
    return AuthenticatedPrincipal(subject_id=subject_id, customer_id=customer_id)


@router.post("/internal/v1/authorize", response_model=AuthorizationResponse)
async def authorize(
    request: AuthorizationRequest,
    principal: Annotated[AuthenticatedPrincipal, Depends(trusted_principal)],
    evaluator: Annotated[PolicyEvaluator, Depends(get_evaluator)],
    audit: Annotated[AuditAdapter, Depends(get_audit_adapter)],
) -> AuthorizationResponse:
    decision_id = str(uuid4())
    try:
        result = await evaluator.evaluate(request, principal)
        response = AuthorizationResponse(
            allowed=result.allowed,
            decision_id=decision_id,
            reason_code=result.reason_code,
            obligations=result.obligations,
        )
    except Exception as exc:  # The authorization boundary must fail closed.
        logger.error("policy_evaluation_failed", extra={"decision_id": decision_id, "exception_type": type(exc).__name__})
        response = AuthorizationResponse(
            allowed=False,
            decision_id=decision_id,
            reason_code="DENY_POLICY_EVALUATION_ERROR",
            obligations=[],
        )
    try:
        await audit.record(request, response)
    except Exception as exc:  # Audit availability must not accidentally grant access or leak internals.
        logger.error("policy_audit_failed", extra={"decision_id": decision_id, "exception_type": type(exc).__name__})
        if response.allowed:
            response = AuthorizationResponse(
                allowed=False,
                decision_id=decision_id,
                reason_code="DENY_AUDIT_FAILURE",
                obligations=[],
            )
    return response


@router.get("/health", include_in_schema=False)
async def health() -> dict[str, str]:
    return {"status": "UP"}


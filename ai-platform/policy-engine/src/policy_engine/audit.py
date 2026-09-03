from __future__ import annotations

import hashlib
import logging
from typing import Protocol

from policy_engine.domain.models import AuthorizationRequest, AuthorizationResponse


class AuditAdapter(Protocol):
    async def record(self, request: AuthorizationRequest, response: AuthorizationResponse) -> None: ...


class StructuredLogAuditAdapter:
    def __init__(self) -> None:
        self._logger = logging.getLogger("policy_engine.audit")

    async def record(self, request: AuthorizationRequest, response: AuthorizationResponse) -> None:
        subject_fingerprint = _fingerprint(request.subject.id) if request.subject else None
        self._logger.info(
            "policy_decision",
            extra={
                "event_type": "policy_decision",
                "decision_id": response.decision_id,
                "allowed": response.allowed,
                "reason_code": response.reason_code,
                "capability": request.capability,
                "subject_fingerprint": subject_fingerprint,
            },
        )


def _fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


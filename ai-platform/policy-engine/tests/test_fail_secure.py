from __future__ import annotations

from conftest import request_for
from policy_engine.api import get_evaluator
from policy_engine.main import app


class FailingEvaluator:
    async def evaluate(self, request, principal):
        raise RuntimeError("sensitive evaluator detail")


async def test_internal_evaluation_failure_denies_safely(client, customer_headers):
    app.dependency_overrides[get_evaluator] = lambda: FailingEvaluator()
    try:
        response = await client.post(
            "/internal/v1/authorize",
            headers=customer_headers,
            json=request_for("account.balance.read", ["account:read"]),
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["allowed"] is False
    assert response.json()["reason_code"] == "DENY_POLICY_EVALUATION_ERROR"
    assert "sensitive" not in response.text


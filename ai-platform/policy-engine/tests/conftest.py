from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from policy_engine.main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client


@pytest.fixture
def customer_headers() -> dict[str, str]:
    return {
        "X-Authenticated-Subject-Id": "user-123",
        "X-Authenticated-Customer-Id": "C1024",
        "X-Request-Id": "request-test-1",
        "X-Correlation-Id": "correlation-test-1",
    }


def request_for(capability: str, scopes: list[str], **changes):
    request = {
        "subject": {"id": "user-123", "roles": ["CUSTOMER"], "scopes": scopes},
        "customer_id": "C1024",
        "capability": capability,
        "resource": {},
        "context": {"channel": "MOBILE"},
    }
    request.update(changes)
    return request


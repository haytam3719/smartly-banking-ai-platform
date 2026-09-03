from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from account_agent.main import app


@pytest.fixture
async def client():
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
            yield test_client


def agent_request(capability: str, arguments: dict | None = None) -> dict:
    return {
        "request_id": "req-100",
        "correlation_id": "corr-100",
        "conversation_id": "conv-100",
        "subject": "user-123",
        "customer_id": "C1024",
        "capability": capability,
        "arguments": arguments or {},
        "locale": "fr-FR",
    }


TRUSTED_HEADERS = {"X-Authenticated-Customer-Id": "C1024"}


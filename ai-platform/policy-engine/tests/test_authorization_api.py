from __future__ import annotations

from conftest import request_for


async def test_valid_account_read(client, customer_headers):
    response = await client.post(
        "/internal/v1/authorize",
        headers=customer_headers,
        json=request_for("account.balance.read", ["account:read"]),
    )
    assert response.status_code == 200
    assert response.json()["allowed"] is True
    assert response.json()["reason_code"] == "ALLOW_CUSTOMER_READ"
    assert response.json()["decision_id"]
    assert response.headers["X-Request-Id"] == "request-test-1"


async def test_valid_transfer_read(client, customer_headers):
    request = request_for(
        "transfer.status.read",
        ["transfer:read"],
        resource={"transfer_id": "TR4587"},
    )
    response = await client.post("/internal/v1/authorize", headers=customer_headers, json=request)
    assert response.json() == {
        "allowed": True,
        "decision_id": response.json()["decision_id"],
        "reason_code": "ALLOW_CUSTOMER_READ",
        "obligations": [],
    }


async def test_missing_scope_is_denied(client, customer_headers):
    response = await client.post(
        "/internal/v1/authorize",
        headers=customer_headers,
        json=request_for("card.info.read", ["account:read"]),
    )
    assert response.json()["allowed"] is False
    assert response.json()["reason_code"] == "DENY_MISSING_SCOPE"


async def test_unknown_capability_is_denied(client, customer_headers):
    response = await client.post(
        "/internal/v1/authorize",
        headers=customer_headers,
        json=request_for("arbitrary.tool.execute", ["arbitrary:*"], context=None),
    )
    assert response.status_code == 200
    assert response.json()["reason_code"] == "DENY_UNKNOWN_CAPABILITY"


async def test_anonymous_customer_request_is_denied(client):
    response = await client.post(
        "/internal/v1/authorize",
        json=request_for("customer.info.read", ["customer:read"], subject=None),
    )
    assert response.json()["allowed"] is False
    assert response.json()["reason_code"] == "DENY_MISSING_SUBJECT"


async def test_knowledge_search_needs_authentication_but_not_customer_scope(client):
    request = request_for(
        "knowledge.search",
        ["knowledge:search"],
        customer_id=None,
        resource={"corpus": "public-help"},
        context={"channel": "WEB"},
    )
    response = await client.post(
        "/internal/v1/authorize",
        headers={"X-Authenticated-Subject-Id": "user-123"},
        json=request,
    )
    assert response.json()["allowed"] is True
    assert response.json()["reason_code"] == "ALLOW_KNOWLEDGE_SEARCH"


async def test_cross_subject_and_customer_attempts_are_denied(client, customer_headers):
    subject_mismatch = request_for(
        "account.transactions.read",
        ["account:read"],
        subject={"id": "attacker", "roles": ["CUSTOMER"], "scopes": ["account:read"]},
    )
    response = await client.post("/internal/v1/authorize", headers=customer_headers, json=subject_mismatch)
    assert response.json()["reason_code"] == "DENY_SUBJECT_MISMATCH"

    customer_mismatch = request_for("account.transactions.read", ["account:read"], customer_id="C2048")
    response = await client.post("/internal/v1/authorize", headers=customer_headers, json=customer_mismatch)
    assert response.json()["reason_code"] == "DENY_CUSTOMER_MISMATCH"


async def test_malformed_context_is_a_deterministic_deny(client, customer_headers):
    response = await client.post(
        "/internal/v1/authorize",
        headers=customer_headers,
        json=request_for("account.balance.read", ["account:read"], context={"channel": "TELEPATHY"}),
    )
    assert response.status_code == 200
    assert response.json()["reason_code"] == "DENY_MALFORMED_CONTEXT"


async def test_structurally_malformed_request_is_rejected(client, customer_headers):
    response = await client.post(
        "/internal/v1/authorize",
        headers=customer_headers,
        json={"subject": "not-an-object", "capability": 42},
    )
    assert response.status_code == 422


async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


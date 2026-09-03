from __future__ import annotations

import httpx
import respx

from conftest import TRUSTED_HEADERS, agent_request


@respx.mock
async def test_balance_success(client):
    respx.get("http://core-banking:8090/internal/v1/customers/C1024/accounts/balance").mock(return_value=httpx.Response(200, json={
        "customer_id": "C1024",
        "accounts": [{"account_id": "A1", "customer_id": "C1024", "type": "CHECKING", "currency": "EUR", "available_balance": 2450.75, "status": "ACTIVE"}],
    }))
    response = await client.post("/internal/v1/capabilities/account.balance.read", headers=TRUSTED_HEADERS, json=agent_request("account.balance.read"))
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["accounts"] == [{"available_balance": "2450.75", "currency": "EUR", "account_type": "CHECKING", "status": "ACTIVE"}]
    assert body["error"] is None


@respx.mock
async def test_transactions_success_and_date_filtering_propagation(client):
    route = respx.get("http://core-banking:8090/internal/v1/customers/C1024/transactions").mock(return_value=httpx.Response(200, json={
        "customer_id": "C1024", "transactions": [{
            "transaction_id": "TX1", "account_id": "A1", "type": "CARD_PAYMENT", "amount": -42.8,
            "currency": "EUR", "merchant": "Synthetic Merchant", "description": "Purchase",
            "occurred_at": "2026-08-20T08:15:00Z", "status": "BOOKED"
        }]
    }))
    request = agent_request("account.transactions.read", {"start_date": "2026-08-01", "end_date": "2026-08-31", "limit": 25})
    response = await client.post("/internal/v1/capabilities/account.transactions.read", headers=TRUSTED_HEADERS, json=request)
    assert response.json()["success"] is True
    assert response.json()["data"]["transactions"][0]["transaction_id"] == "TX1"
    assert dict(route.calls[0].request.url.params) == {"limit": "25", "start_date": "2026-08-01", "end_date": "2026-08-31"}


@respx.mock
async def test_limit_validation_applies_server_upper_bound(client):
    request = agent_request("account.transactions.read", {"limit": 101})
    response = await client.post("/internal/v1/capabilities/account.transactions.read", headers=TRUSTED_HEADERS, json=request)
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "INVALID_ARGUMENTS"
    assert len(respx.calls) == 0


@respx.mock
async def test_unknown_customer_is_not_retried(client):
    route = respx.get("http://core-banking:8090/internal/v1/customers/C1024/accounts/balance").mock(return_value=httpx.Response(404, json={"code": "CUSTOMER_NOT_FOUND"}))
    response = await client.post("/internal/v1/capabilities/account.balance.read", headers=TRUSTED_HEADERS, json=agent_request("account.balance.read"))
    assert response.json()["error"] == {"code": "CUSTOMER_NOT_FOUND", "message": "Customer not found", "request_id": "req-100", "retryable": False}
    assert route.call_count == 1


@respx.mock
async def test_core_banking_timeout_is_bounded_and_safe(client):
    route = respx.get("http://core-banking:8090/internal/v1/customers/C1024/accounts/balance").mock(side_effect=httpx.ReadTimeout("slow"))
    response = await client.post("/internal/v1/capabilities/account.balance.read", headers=TRUSTED_HEADERS, json=agent_request("account.balance.read"))
    assert response.json()["error"]["code"] == "CORE_BANKING_TIMEOUT"
    assert response.json()["error"]["retryable"] is True
    assert route.call_count == 3


@respx.mock
async def test_core_banking_500_is_retried_then_mapped_safely(client):
    route = respx.get("http://core-banking:8090/internal/v1/customers/C1024/accounts/balance").mock(return_value=httpx.Response(500, json={"internal": "do not leak"}))
    response = await client.post("/internal/v1/capabilities/account.balance.read", headers=TRUSTED_HEADERS, json=agent_request("account.balance.read"))
    assert response.json()["error"]["code"] == "CORE_BANKING_UNAVAILABLE"
    assert "internal" not in response.text
    assert route.call_count == 3


@respx.mock
async def test_unsupported_capability_never_calls_backend(client):
    response = await client.post("/internal/v1/capabilities/account.balance.read", headers=TRUSTED_HEADERS, json=agent_request("transfer.status.read"))
    assert response.json()["error"]["code"] == "UNSUPPORTED_CAPABILITY"
    assert len(respx.calls) == 0


@respx.mock
async def test_correlation_and_trace_headers_propagate(client):
    route = respx.get("http://core-banking:8090/internal/v1/customers/C1024/accounts/balance").mock(return_value=httpx.Response(200, json={"accounts": []}))
    await client.post("/internal/v1/capabilities/account.balance.read", headers={**TRUSTED_HEADERS, "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"}, json=agent_request("account.balance.read"))
    headers = route.calls[0].request.headers
    assert headers["X-Request-Id"] == "req-100"
    assert headers["X-Correlation-Id"] == "corr-100"
    assert headers["X-Conversation-Id"] == "conv-100"
    assert "traceparent" in headers


@respx.mock
async def test_untrusted_customer_id_is_rejected_before_backend(client):
    response = await client.post("/internal/v1/capabilities/account.balance.read", headers={"X-Authenticated-Customer-Id": "C2048"}, json=agent_request("account.balance.read"))
    assert response.json()["error"]["code"] == "CUSTOMER_CONTEXT_MISMATCH"
    assert len(respx.calls) == 0

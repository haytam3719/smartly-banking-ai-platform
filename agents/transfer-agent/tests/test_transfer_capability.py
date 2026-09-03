from datetime import datetime, timezone
from decimal import Decimal
import httpx, pytest, respx
from conftest import HEADERS, request
from transfer_agent.models import CallContext, TransferInfo
from transfer_agent.service import TransferCapabilityService

BACKEND = "http://core-banking:8090/internal/v1/customers/C1024/transfers"
def payload(transfer_id="TR4587", status="REJECTED", reason="PAYMENT_LIMIT_EXCEEDED"):
    return {"transfer_id":transfer_id, "customer_id":"C1024", "beneficiary":"Synthetic Beneficiary A", "amount":1000, "currency":"EUR", "created_at":"2026-08-22T09:30:00Z", "status":status, "rejection_reason":reason, "internal_note":"must not leak"}

@pytest.mark.parametrize(("transfer_id","status","reason"), [("TR4587","REJECTED","PAYMENT_LIMIT_EXCEEDED"), ("TR4588","COMPLETED",None), ("TR4589","PENDING",None)])
@respx.mock
async def test_statuses(client, transfer_id, status, reason):
    respx.get(f"{BACKEND}/{transfer_id}").mock(return_value=httpx.Response(200, json=payload(transfer_id,status,reason)))
    response = await client.post("/internal/v1/capabilities/transfer.status.read", json=request(transfer_id), headers=HEADERS)
    body = response.json(); assert body["success"] is True; assert body["data"]["status"] == status; assert body["data"]["rejection_reason"] == reason
    assert "customer_id" not in body["data"] and "internal_note" not in body["data"]

@pytest.mark.parametrize("path", ["UNKNOWN", "TR-FOREIGN"])
@respx.mock
async def test_unknown_and_cross_customer_are_indistinguishable(client, path):
    respx.get(f"{BACKEND}/{path}").mock(return_value=httpx.Response(404, json={"code":"TRANSFER_NOT_FOUND"}))
    body = (await client.post("/internal/v1/capabilities/transfer.status.read", json=request(path), headers=HEADERS)).json()
    assert body["success"] is False; assert body["error"]["code"] == "TRANSFER_NOT_FOUND"; assert body["error"]["message"] == "Transfer not found"

async def test_customer_context_mismatch_never_calls_backend(client):
    body = (await client.post("/internal/v1/capabilities/transfer.status.read", json=request(customer_id="C2048"), headers=HEADERS)).json()
    assert body["error"]["code"] == "CUSTOMER_CONTEXT_MISMATCH"

def test_policy_fact_minimization():
    transfer = TransferInfo(transfer_id="TR4587", amount=Decimal("1000"), currency="EUR", beneficiary="Private Name", created_at=datetime.now(timezone.utc), status="REJECTED", rejection_reason="PAYMENT_LIMIT_EXCEEDED")
    facts = TransferCapabilityService.policy_facts(transfer).model_dump()
    assert facts == {"status":"REJECTED", "rejection_reason":"PAYMENT_LIMIT_EXCEEDED"}
    assert not ({"amount", "beneficiary", "transfer_id", "currency"} & facts.keys())

@respx.mock
async def test_timeout_is_safe_and_retryable(client):
    route = respx.get(f"{BACKEND}/TR4587").mock(side_effect=httpx.ReadTimeout("slow"))
    body = (await client.post("/internal/v1/capabilities/transfer.status.read", json=request(), headers=HEADERS)).json()
    assert route.call_count == 3; assert body["data"] is None; assert body["error"]["code"] == "CORE_BANKING_TIMEOUT"; assert body["error"]["retryable"] is True

@respx.mock
async def test_downstream_error_is_safe(client):
    route = respx.get(f"{BACKEND}/TR4587").mock(return_value=httpx.Response(500))
    body = (await client.post("/internal/v1/capabilities/transfer.status.read", json=request(), headers=HEADERS)).json()
    assert route.call_count == 3; assert body["error"]["code"] == "CORE_BANKING_UNAVAILABLE"; assert body["data"] is None

async def test_unsupported_capability(client):
    body = (await client.post("/internal/v1/capabilities/transfer.status.read", json=request(capability="account.balance.read"), headers=HEADERS)).json()
    assert body["error"]["code"] == "UNSUPPORTED_CAPABILITY"

@respx.mock
async def test_customer_scoped_url_and_context_propagation(client):
    route = respx.get(f"{BACKEND}/TR4587").mock(return_value=httpx.Response(200, json=payload()))
    await client.post("/internal/v1/capabilities/transfer.status.read", json=request(), headers={**HEADERS,"X-Request-Id":"req-http","X-Correlation-Id":"corr-http","traceparent":"00-0123456789abcdef0123456789abcdef-0123456789abcdef-01"})
    sent = route.calls[0].request
    assert sent.headers["X-Request-Id"] == "req-transfer"; assert sent.headers["X-Correlation-Id"] == "corr-transfer"; assert "traceparent" in sent.headers

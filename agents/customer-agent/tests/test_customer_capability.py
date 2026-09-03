import httpx, pytest, respx
from conftest import HEADERS, request
BACKEND="http://core-banking:8090/internal/v1/customers/C1024"
def payload():
    return {"customer_id":"C1024","first_name":"Alice","last_name":"Example","segment":"RETAIL","kyc_status":"VERIFIED","country":"MA","password":"secret","credentials":{"token":"bad"},"internal_risk_notes":"private","address":"private"}
@respx.mock
async def test_customer_success_and_pii_minimization(client):
    respx.get(BACKEND).mock(return_value=httpx.Response(200,json=payload()))
    body=(await client.post("/internal/v1/capabilities/customer.info.read",json=request(),headers=HEADERS)).json()
    assert body["success"] is True
    assert body["data"]=={"customer_id":"C1024","segment":"RETAIL","kyc_status":"VERIFIED","country":"MA"}
    serialized=str(body); assert not any(value in serialized for value in ["Alice","Example","secret","token","internal_risk_notes","address"])
@respx.mock
async def test_unknown_customer(client):
    respx.get(BACKEND).mock(return_value=httpx.Response(404,json={"code":"CUSTOMER_NOT_FOUND"}))
    body=(await client.post("/internal/v1/capabilities/customer.info.read",json=request(),headers=HEADERS)).json()
    assert body["error"]["code"]=="CUSTOMER_NOT_FOUND"; assert body["data"] is None
@respx.mock
async def test_downstream_timeout(client):
    route=respx.get(BACKEND).mock(side_effect=httpx.ReadTimeout("slow"))
    body=(await client.post("/internal/v1/capabilities/customer.info.read",json=request(),headers=HEADERS)).json()
    assert route.call_count==3; assert body["error"]["code"]=="CORE_BANKING_TIMEOUT"; assert body["error"]["retryable"] is True
@respx.mock
async def test_downstream_500(client):
    route=respx.get(BACKEND).mock(return_value=httpx.Response(500))
    body=(await client.post("/internal/v1/capabilities/customer.info.read",json=request(),headers=HEADERS)).json()
    assert route.call_count==3; assert body["error"]["code"]=="CORE_BANKING_UNAVAILABLE"; assert body["data"] is None
@respx.mock
async def test_request_context_propagation(client):
    route=respx.get(BACKEND).mock(return_value=httpx.Response(200,json=payload()))
    await client.post("/internal/v1/capabilities/customer.info.read",json=request(),headers={**HEADERS,"traceparent":"00-0123456789abcdef0123456789abcdef-0123456789abcdef-01"})
    headers=route.calls[0].request.headers
    assert headers["X-Request-Id"]=="req-customer"; assert headers["X-Correlation-Id"]=="corr-customer"; assert headers["X-Conversation-Id"]=="conv-customer"; assert headers["traceparent"]=="00-0123456789abcdef0123456789abcdef-0123456789abcdef-01"
async def test_context_mismatch_does_not_call_backend(client):
    body=(await client.post("/internal/v1/capabilities/customer.info.read",json=request(customer_id="C2048"),headers=HEADERS)).json()
    assert body["error"]["code"]=="CUSTOMER_CONTEXT_MISMATCH"
async def test_unsupported_capability(client):
    body=(await client.post("/internal/v1/capabilities/customer.info.read",json=request("card.info.read"),headers=HEADERS)).json()
    assert body["error"]["code"]=="UNSUPPORTED_CAPABILITY"

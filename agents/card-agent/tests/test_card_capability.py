import httpx,respx
from conftest import HEADERS,request
URL="http://core-banking:8090/internal/v1/customers/C1024/cards/primary"
def backend(**changes):
    value={"card_id":"SECRET-ID","customer_id":"C1024","type":"GOLD","status":"ACTIVE","expiration_date":"2028-05-31","payment_limit":2500,"amount_used":1800,"currency":"EUR"};value.update(changes);return value
@respx.mock
async def test_active_card(client):
    respx.get(URL).mock(return_value=httpx.Response(200,json=backend()))
    response=await client.post("/internal/v1/capabilities/card.info.read",headers=HEADERS,json=request());body=response.json()
    assert body["success"] is True
    assert body["data"]=={"card_type":"GOLD","status":"ACTIVE","expiration_date":"2028-05","payment_limit":"2500","amount_used":"1800","available_limit":"700","currency":"EUR"}
@respx.mock
async def test_blocked_card_is_reported_without_mutation(client):
    respx.get(URL).mock(return_value=httpx.Response(200,json=backend(status="BLOCKED")))
    body=(await client.post("/internal/v1/capabilities/card.info.read",headers=HEADERS,json=request())).json()
    assert body["success"] is True and body["data"]["status"]=="BLOCKED"
@respx.mock
async def test_available_limit_never_goes_below_zero(client):
    respx.get(URL).mock(return_value=httpx.Response(200,json=backend(payment_limit="1000.00",amount_used="1200.00")))
    body=(await client.post("/internal/v1/capabilities/card.info.read",headers=HEADERS,json=request())).json()
    assert body["data"]["available_limit"]=="0"
@respx.mock
async def test_unavailable_customer_is_safe_and_not_retried(client):
    route=respx.get(URL).mock(return_value=httpx.Response(404,json={"code":"CUSTOMER_NOT_FOUND"}))
    body=(await client.post("/internal/v1/capabilities/card.info.read",headers=HEADERS,json=request())).json()
    assert body["error"]["code"]=="CARD_NOT_FOUND" and route.call_count==1
@respx.mock
async def test_downstream_timeout_is_bounded(client):
    route=respx.get(URL).mock(side_effect=httpx.ReadTimeout("slow"))
    body=(await client.post("/internal/v1/capabilities/card.info.read",headers=HEADERS,json=request())).json()
    assert body["error"]["code"]=="CORE_BANKING_TIMEOUT" and route.call_count==3
@respx.mock
async def test_downstream_500_is_bounded_and_safe(client):
    route=respx.get(URL).mock(return_value=httpx.Response(500,json={"secret":"internal"}))
    response=await client.post("/internal/v1/capabilities/card.info.read",headers=HEADERS,json=request())
    assert response.json()["error"]["code"]=="CORE_BANKING_UNAVAILABLE" and route.call_count==3 and "secret" not in response.text
@respx.mock
async def test_sensitive_backend_fields_never_returned(client):
    respx.get(URL).mock(return_value=httpx.Response(200,json=backend(pan="4111111111111111",cvv="123",cardholder_name="Sensitive Name")))
    response=await client.post("/internal/v1/capabilities/card.info.read",headers=HEADERS,json=request())
    assert all(value not in response.text for value in ["4111111111111111","123","Sensitive Name","SECRET-ID"])
@respx.mock
async def test_unsupported_capability_does_not_call_backend(client):
    body=(await client.post("/internal/v1/capabilities/card.info.read",headers=HEADERS,json=request("account.balance.read"))).json()
    assert body["error"]["code"]=="UNSUPPORTED_CAPABILITY" and len(respx.calls)==0
@respx.mock
async def test_context_and_trace_propagation(client):
    route=respx.get(URL).mock(return_value=httpx.Response(200,json=backend()))
    await client.post("/internal/v1/capabilities/card.info.read",headers={**HEADERS,"traceparent":"00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"},json=request())
    headers=route.calls[0].request.headers
    assert headers["X-Request-Id"]=="req-card" and headers["X-Correlation-Id"]=="corr-card" and "traceparent" in headers


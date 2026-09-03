import pytest
from httpx import ASGITransport, AsyncClient
from customer_agent.main import app
@pytest.fixture
async def client():
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as value: yield value
def request(capability="customer.info.read",customer_id="C1024"):
    return {"request_id":"req-customer","correlation_id":"corr-customer","conversation_id":"conv-customer","subject":"user-123","customer_id":customer_id,"capability":capability,"arguments":{},"locale":"fr-FR"}
HEADERS={"X-Authenticated-Customer-Id":"C1024"}

import pytest
from httpx import ASGITransport,AsyncClient
from card_agent.main import app
@pytest.fixture
async def client():
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as value:yield value
def request(capability="card.info.read"):
    return {"request_id":"req-card","correlation_id":"corr-card","conversation_id":"conv-card","subject":"user-123","customer_id":"C1024","capability":capability,"arguments":{},"locale":"fr-FR"}
HEADERS={"X-Authenticated-Customer-Id":"C1024"}


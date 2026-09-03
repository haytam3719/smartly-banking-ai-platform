import pytest
from httpx import ASGITransport, AsyncClient
from transfer_agent.main import app

@pytest.fixture
async def client():
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as value: yield value

def request(transfer_id="TR4587", capability="transfer.status.read", customer_id="C1024"):
    return {"request_id":"req-transfer", "correlation_id":"corr-transfer", "conversation_id":"conv-transfer", "subject":"user-123", "customer_id":customer_id, "capability":capability, "arguments":{"transfer_id":transfer_id}, "locale":"fr-FR"}

HEADERS = {"X-Authenticated-Customer-Id":"C1024"}

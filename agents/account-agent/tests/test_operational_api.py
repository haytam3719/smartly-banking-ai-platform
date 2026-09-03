from __future__ import annotations


async def test_capability_listing_and_health(client):
    capabilities = await client.get("/internal/v1/capabilities")
    assert capabilities.json() == {"capabilities": ["account.balance.read", "account.transactions.read"]}
    health = await client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "UP"}


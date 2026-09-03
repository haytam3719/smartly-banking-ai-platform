async def test_operational_endpoints(client):
    capabilities = await client.get("/internal/v1/capabilities")
    assert capabilities.json() == {"capabilities":["transfer.status.read"]}
    assert (await client.get("/health")).json() == {"status":"UP"}
    assert (await client.get("/metrics")).status_code == 200

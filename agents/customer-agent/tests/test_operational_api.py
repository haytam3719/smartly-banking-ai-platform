async def test_operational_endpoints(client):
    assert (await client.get("/internal/v1/capabilities")).json()=={"capabilities":["customer.info.read"]}
    assert (await client.get("/health")).json()=={"status":"UP"}
    assert (await client.get("/metrics")).status_code==200

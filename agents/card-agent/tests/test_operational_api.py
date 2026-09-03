async def test_capabilities_and_health(client):
    assert (await client.get("/internal/v1/capabilities")).json()=={"capabilities":["card.info.read"]}
    assert (await client.get("/health")).json()=={"status":"UP"}


from httpx import AsyncClient


async def test_rate_limit_triggers(client: AsyncClient):
    for _ in range(60):
        await client.get("/health")

    response = await client.get("/health")
    assert response.status_code == 429

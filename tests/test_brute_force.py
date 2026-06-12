from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import UserFactory


async def test_brute_force_lockout(client: AsyncClient, db_session: AsyncSession):
    UserFactory._meta.sqlalchemy_session = db_session  # type: ignore
    user = UserFactory()

    for _ in range(5):
        await client.post(
            "/auth/login",
            json={
                "email": user.email,
                "password": "wrongpassword",
            },
        )

    response = await client.post(
        "/auth/login",
        json={
            "email": user.email,
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 429
    assert "locked" in response.json()["detail"].lower()


async def test_successful_login_clears_failures(
    client: AsyncClient, db_session: AsyncSession
):
    UserFactory._meta.sqlalchemy_session = db_session  # type: ignore
    user = UserFactory()

    for _ in range(4):
        await client.post(
            "/auth/login",
            json={
                "email": user.email,
                "password": "wrongpassword",
            },
        )

    response = await client.post(
        "/auth/login",
        json={
            "email": user.email,
            "password": "testpass123",
        },
    )
    assert response.status_code == 200

    for _ in range(5):
        await client.post(
            "/auth/login",
            json={
                "email": user.email,
                "password": "wrongpassword",
            },
        )

    response = await client.post(
        "/auth/login",
        json={
            "email": user.email,
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 429

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import UserFactory


@pytest.fixture
async def auth_headers(client: AsyncClient, db_session: AsyncSession):
    UserFactory._meta.sqlalchemy_session = db_session  # type: ignore
    await db_session.flush()

    response = await client.post(
        "/auth/register",
        json={
            "email": "me@example.com",
            "password": "testpass123",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201

    login = await client.post(
        "/auth/login",
        json={
            "email": "me@example.com",
            "password": "testpass123",
        },
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_get_me(client: AsyncClient, auth_headers: dict):
    response = await client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


async def test_update_me(client: AsyncClient, auth_headers: dict):
    response = await client.put(
        "/users/me",
        headers=auth_headers,
        json={
            "full_name": "Updated Name",
        },
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"


async def test_me_requires_auth(client: AsyncClient):
    response = await client.get("/users/me")
    assert response.status_code == 401


async def test_register_weak_password(client: AsyncClient):
    response = await client.post(
        "/auth/register",
        json={"email": "weak@example.com", "password": "abc"},
    )
    assert response.status_code == 422

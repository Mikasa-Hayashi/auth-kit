import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import UserFactory


@pytest.fixture
async def existing_user(db_session: AsyncSession):
    UserFactory._meta.sqlalchemy_session = db_session  # type: ignore
    return UserFactory()


async def test_register_success(client: AsyncClient):
    response = await client.post(
        "/auth/register",
        json={
            "email": "new@example.com",
            "password": "strongpass1",
            "full_name": "New User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert "id" in data
    assert "hashed_password" not in data


async def test_register_duplicate_email(client: AsyncClient, existing_user):
    response = await client.post(
        "/auth/register",
        json={
            "email": existing_user.email,
            "password": "whatever",
        },
    )
    assert response.status_code == 409


async def test_login_success(client: AsyncClient, existing_user):
    response = await client.post(
        "/auth/login",
        json={
            "email": existing_user.email,
            "password": "testpass123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


async def test_login_wrong_password(client: AsyncClient, existing_user):
    response = await client.post(
        "/auth/login",
        json={
            "email": existing_user.email,
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401


async def test_refresh_token_rotation(client: AsyncClient, existing_user):
    login = await client.post(
        "/auth/login",
        json={
            "email": existing_user.email,
            "password": "testpass123",
        },
    )
    refresh_token = login.json()["refresh_token"]

    response = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    new_tokens = response.json()
    assert new_tokens["refresh_token"] != refresh_token

    response = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 401


async def test_logout_invalidates_refresh_token(client: AsyncClient, existing_user):
    login = await client.post(
        "/auth/login",
        json={
            "email": existing_user.email,
            "password": "testpass123",
        },
    )
    refresh_token = login.json()["refresh_token"]

    await client.post("/auth/logout", json={"refresh_token": refresh_token})

    response = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 401

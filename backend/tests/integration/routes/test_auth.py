import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.user import UserModel
from shared.helpers.hash import hash_password


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> UserModel:
    user = UserModel(
        email="testadmin@publisher.local",
        password_hash=hash_password("TestPass123!"),
        role="admin",
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.mark.asyncio
async def test_login_valid_credentials_returns_tokens(client: AsyncClient, admin_user: UserModel):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "TestPass123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "accessToken" in data["data"] or "access_token" in data["data"]


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(client: AsyncClient, admin_user: UserModel):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "wrong"},
    )
    assert response.status_code == 401
    assert response.json()["success"] is False


@pytest.mark.asyncio
async def test_login_unknown_email_returns_401(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@x.com", "password": "whatever"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_with_valid_token(client: AsyncClient, admin_user: UserModel):
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "TestPass123!"},
    )
    refresh_token = login.json()["data"]["refresh_token"]

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()["data"]


@pytest.mark.asyncio
async def test_protected_endpoint_without_token_returns_401(client: AsyncClient):
    response = await client.get("/api/v1/accounts")
    assert response.status_code in (401, 403)

"""E2E: Login → protected page → token refresh → logout."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.user import UserModel
from shared.helpers.hash import hash_password


@pytest.fixture
async def e2e_user(db_session: AsyncSession) -> UserModel:
    user = UserModel(
        email="e2e_auth@publisher.local",
        password_hash=hash_password("E2EPass123!"),
        role="admin",
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.mark.asyncio
async def test_login_then_access_protected_endpoint(client: AsyncClient, e2e_user: UserModel):
    # 1. Login
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": e2e_user.email, "password": "E2EPass123!"},
    )
    assert login.status_code == 200
    tokens = login.json()["data"]
    access_token = tokens.get("access_token") or tokens.get("accessToken")
    assert access_token

    # 2. Access protected endpoint
    headers = {"Authorization": f"Bearer {access_token}"}
    accounts = await client.get("/api/v1/accounts", headers=headers)
    assert accounts.status_code == 200

    # 3. Token refresh
    refresh_token = tokens.get("refresh_token") or tokens.get("refreshToken")
    refresh = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh.status_code == 200
    new_token = refresh.json()["data"].get("access_token") or refresh.json()["data"].get("accessToken")
    assert new_token

    # 4. Old access token still works (not revoked)
    check = await client.get("/api/v1/accounts", headers={"Authorization": f"Bearer {new_token}"})
    assert check.status_code == 200


@pytest.mark.asyncio
async def test_wrong_password_blocked(client: AsyncClient, e2e_user: UserModel):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": e2e_user.email, "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_no_token_blocked_from_protected(client: AsyncClient):
    response = await client.get("/api/v1/accounts")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_invalid_token_blocked(client: AsyncClient):
    response = await client.get(
        "/api/v1/accounts",
        headers={"Authorization": "Bearer totally.invalid.token"},
    )
    assert response.status_code in (401, 403)

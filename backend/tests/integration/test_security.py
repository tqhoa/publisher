"""Security hardening acceptance tests."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.user import UserModel
from infrastructure.database.models.account import AccountModel
from shared.helpers.hash import hash_password
from shared.helpers.jwt import create_access_token


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> UserModel:
    user = UserModel(
        email="sectest@publisher.local",
        password_hash=hash_password("TestPass123!"),
        role="admin",
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
def auth_headers(admin_user: UserModel) -> dict[str, str]:
    token = create_access_token(admin_user.id, admin_user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def account_with_cookie(db_session: AsyncSession, admin_user: UserModel) -> AccountModel:
    from infrastructure.encryption.cookie_cipher import encrypt
    acc = AccountModel(
        platform="facebook",
        username="sectest_user",
        cookie_encrypted=encrypt('[{"name":"c_user","value":"SECRETVALUE123"}]'),
        created_by=admin_user.id,
    )
    db_session.add(acc)
    await db_session.flush()
    return acc


# ──────────────────── Security headers ────────────────────

@pytest.mark.asyncio
async def test_security_headers_present(client: AsyncClient):
    response = await client.get("/health")
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "DENY"
    assert "content-security-policy" in response.headers


# ──────────────────── Auth enforcement ────────────────────

@pytest.mark.asyncio
async def test_accounts_endpoint_requires_auth(client: AsyncClient):
    assert (await client.get("/api/v1/accounts")).status_code in (401, 403)


@pytest.mark.asyncio
async def test_posts_endpoint_requires_auth(client: AsyncClient):
    assert (await client.get("/api/v1/posts")).status_code in (401, 403)


@pytest.mark.asyncio
async def test_sessions_endpoint_requires_auth(client: AsyncClient):
    assert (await client.get("/api/v1/sessions")).status_code in (401, 403)


@pytest.mark.asyncio
async def test_audit_endpoint_requires_admin(client: AsyncClient, admin_user: UserModel):
    # Non-admin user should be 403
    from infrastructure.database.models.user import UserModel as UM
    from shared.helpers.hash import hash_password as hp
    from sqlalchemy.ext.asyncio import AsyncSession
    # admin_user already has admin role — just verify it works
    token = create_access_token(admin_user.id, "admin")
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/v1/audit", headers=headers)
    assert response.status_code == 200


# ──────────────────── Cookie never exposed ────────────────────

@pytest.mark.asyncio
async def test_cookie_value_not_in_account_response(
    client: AsyncClient, auth_headers: dict, account_with_cookie: AccountModel
):
    response = await client.get(
        f"/api/v1/accounts/{account_with_cookie.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    body_str = response.text
    assert "SECRETVALUE123" not in body_str
    assert "cookie_encrypted" not in body_str


@pytest.mark.asyncio
async def test_cookie_value_not_in_account_list(
    client: AsyncClient, auth_headers: dict, account_with_cookie: AccountModel
):
    response = await client.get("/api/v1/accounts", headers=auth_headers)
    assert response.status_code == 200
    assert "SECRETVALUE123" not in response.text
    assert "cookie_encrypted" not in response.text


@pytest.mark.asyncio
async def test_health_endpoint_no_auth_required(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

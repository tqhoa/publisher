import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.user import UserModel
from shared.helpers.hash import hash_password
from shared.helpers.jwt import create_access_token


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> UserModel:
    user = UserModel(
        email="accounttest@publisher.local",
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


# ──────────────────────────── List ────────────────────────────

@pytest.mark.asyncio
async def test_list_accounts_returns_200(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/accounts", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert "pagination" in body


@pytest.mark.asyncio
async def test_list_accounts_no_auth_returns_401(client: AsyncClient):
    response = await client.get("/api/v1/accounts")
    assert response.status_code in (401, 403)


# ──────────────────────────── Create ────────────────────────────

@pytest.mark.asyncio
async def test_create_account_returns_201(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/v1/accounts",
        json={"platform": "facebook", "username": "test_user"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["data"]["platform"] == "facebook"
    assert body["data"]["username"] == "test_user"


@pytest.mark.asyncio
async def test_create_account_no_auth_returns_401(client: AsyncClient):
    response = await client.post(
        "/api/v1/accounts",
        json={"platform": "facebook", "username": "x"},
    )
    assert response.status_code in (401, 403)


# ──────────────────────────── Get by ID ────────────────────────────

@pytest.mark.asyncio
async def test_get_account_returns_200(client: AsyncClient, auth_headers: dict):
    create = await client.post(
        "/api/v1/accounts",
        json={"platform": "tiktok", "username": "tiktok_user"},
        headers=auth_headers,
    )
    account_id = create.json()["data"]["id"]

    response = await client.get(f"/api/v1/accounts/{account_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["data"]["id"] == account_id


@pytest.mark.asyncio
async def test_get_nonexistent_account_returns_404(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/accounts/nonexistent-id", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "ACCOUNT_NOT_FOUND"


# ──────────────────────────── Update ────────────────────────────

@pytest.mark.asyncio
async def test_patch_account_returns_200(client: AsyncClient, auth_headers: dict):
    create = await client.post(
        "/api/v1/accounts",
        json={"platform": "facebook", "username": "old_name"},
        headers=auth_headers,
    )
    account_id = create.json()["data"]["id"]

    response = await client.patch(
        f"/api/v1/accounts/{account_id}",
        json={"username": "new_name"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"]["username"] == "new_name"


# ──────────────────────────── Delete ────────────────────────────

@pytest.mark.asyncio
async def test_delete_account_returns_204(client: AsyncClient, auth_headers: dict):
    create = await client.post(
        "/api/v1/accounts",
        json={"platform": "facebook", "username": "to_delete"},
        headers=auth_headers,
    )
    account_id = create.json()["data"]["id"]

    response = await client.delete(f"/api/v1/accounts/{account_id}", headers=auth_headers)
    assert response.status_code == 204

    # Soft-delete: subsequent GET returns 404
    get = await client.get(f"/api/v1/accounts/{account_id}", headers=auth_headers)
    assert get.status_code == 404


# ──────────────────────────── Cookie Import (Task 3.2) ────────────────────────────

@pytest.mark.asyncio
async def test_import_cookie_returns_200(client: AsyncClient, auth_headers: dict):
    create = await client.post(
        "/api/v1/accounts",
        json={"platform": "facebook", "username": "cookie_user"},
        headers=auth_headers,
    )
    account_id = create.json()["data"]["id"]

    response = await client.post(
        f"/api/v1/accounts/{account_id}/cookie",
        json={"cookie_json": '[{"name":"c_user","value":"123"}]'},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    # Raw cookie value must NOT be returned
    assert "cookie_json" not in str(body)
    assert "c_user" not in str(body)


@pytest.mark.asyncio
async def test_health_check_no_cookie_returns_unhealthy(client: AsyncClient, auth_headers: dict):
    create = await client.post(
        "/api/v1/accounts",
        json={"platform": "facebook", "username": "nocookie"},
        headers=auth_headers,
    )
    account_id = create.json()["data"]["id"]

    response = await client.get(f"/api/v1/accounts/{account_id}/health", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["data"]["healthy"] is False


@pytest.mark.asyncio
async def test_health_check_with_cookie_returns_healthy(client: AsyncClient, auth_headers: dict):
    create = await client.post(
        "/api/v1/accounts",
        json={"platform": "facebook", "username": "withcookie"},
        headers=auth_headers,
    )
    account_id = create.json()["data"]["id"]

    await client.post(
        f"/api/v1/accounts/{account_id}/cookie",
        json={"cookie_json": '[{"name":"c_user","value":"456"}]'},
        headers=auth_headers,
    )

    response = await client.get(f"/api/v1/accounts/{account_id}/health", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["data"]["healthy"] is True

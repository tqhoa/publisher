"""E2E: Create account → import cookie → health check."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.user import UserModel
from shared.helpers.hash import hash_password
from shared.helpers.jwt import create_access_token


@pytest.fixture
async def e2e_user(db_session: AsyncSession) -> UserModel:
    user = UserModel(
        email="e2e_account@publisher.local",
        password_hash=hash_password("E2EPass123!"),
        role="admin",
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
def auth_headers(e2e_user: UserModel) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(e2e_user.id, e2e_user.role)}"}


@pytest.mark.asyncio
async def test_full_account_lifecycle(client: AsyncClient, auth_headers: dict):
    # 1. Create account
    create = await client.post(
        "/api/v1/accounts",
        json={"platform": "facebook", "username": "e2e_fb_user"},
        headers=auth_headers,
    )
    assert create.status_code == 201
    account_id = create.json()["data"]["id"]

    # 2. Verify it appears in list
    listing = await client.get("/api/v1/accounts", headers=auth_headers)
    assert listing.status_code == 200
    ids = [a["id"] for a in listing.json()["data"]]
    assert account_id in ids

    # 3. Import cookie
    cookie = await client.post(
        f"/api/v1/accounts/{account_id}/cookie",
        json={"cookie_json": '[{"name":"c_user","value":"e2e_test_123","domain":".facebook.com"}]'},
        headers=auth_headers,
    )
    assert cookie.status_code == 200
    # Raw cookie NEVER returned
    assert "e2e_test_123" not in cookie.text

    # 4. Health check (stub returns healthy when cookie exists)
    health = await client.get(f"/api/v1/accounts/{account_id}/health", headers=auth_headers)
    assert health.status_code == 200
    assert health.json()["data"]["healthy"] is True

    # 5. Delete (soft)
    delete = await client.delete(f"/api/v1/accounts/{account_id}", headers=auth_headers)
    assert delete.status_code == 204

    # 6. After soft-delete, GET returns 404
    gone = await client.get(f"/api/v1/accounts/{account_id}", headers=auth_headers)
    assert gone.status_code == 404

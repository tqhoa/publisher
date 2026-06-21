import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch

from infrastructure.database.models.user import UserModel
from infrastructure.database.models.account import AccountModel
from shared.helpers.hash import hash_password
from shared.helpers.jwt import create_access_token


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> UserModel:
    user = UserModel(
        email="postsadmin@publisher.info",
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
async def account(db_session: AsyncSession, admin_user: UserModel) -> AccountModel:
    acc = AccountModel(
        platform="facebook",
        username="test_account",
        created_by=admin_user.id,
    )
    db_session.add(acc)
    await db_session.flush()
    return acc


def _post_payload(account_id: str, **overrides: object) -> dict:
    return {
        "account_id": account_id,
        "platform": "facebook",
        "content_type": "text",
        "caption": "Hello world",
        **overrides,  # type: ignore[arg-type]
    }


# ──────────────────────────── Create ────────────────────────────


@pytest.mark.asyncio
async def test_create_post_returns_201_status_queued(
    client: AsyncClient, auth_headers: dict, account: AccountModel
):
    with patch("domain.services.post_service.PostService._enqueue"):
        response = await client.post(
            "/api/v1/posts",
            json=_post_payload(account.id),
            headers=auth_headers,
        )
    assert response.status_code == 201
    body = response.json()
    assert body["data"]["status"] == "queued"
    assert body["data"]["account_id"] == account.id


@pytest.mark.asyncio
async def test_create_post_with_scheduled_at_status_pending(
    client: AsyncClient, auth_headers: dict, account: AccountModel
):
    with patch("domain.services.post_service.PostService._enqueue"):
        response = await client.post(
            "/api/v1/posts",
            json=_post_payload(account.id, scheduled_at="2030-01-01T00:00:00Z"),
            headers=auth_headers,
        )
    assert response.status_code == 201
    assert response.json()["data"]["status"] == "pending"


@pytest.mark.asyncio
async def test_create_post_no_auth_returns_401(
    client: AsyncClient, account: AccountModel
):
    response = await client.post("/api/v1/posts", json=_post_payload(account.id))
    assert response.status_code in (401, 403)


# ──────────────────────────── List ────────────────────────────


@pytest.mark.asyncio
async def test_list_posts_returns_200(
    client: AsyncClient, auth_headers: dict, account: AccountModel
):
    with patch("domain.services.post_service.PostService._enqueue"):
        await client.post(
            "/api/v1/posts",
            json=_post_payload(account.id),
            headers=auth_headers,
        )
    response = await client.get("/api/v1/posts", headers=auth_headers)
    assert response.status_code == 200
    assert "data" in response.json()
    assert "pagination" in response.json()


@pytest.mark.asyncio
async def test_list_posts_filter_by_status(
    client: AsyncClient, auth_headers: dict, account: AccountModel
):
    with patch("domain.services.post_service.PostService._enqueue"):
        await client.post(
            "/api/v1/posts",
            json=_post_payload(account.id),
            headers=auth_headers,
        )
    response = await client.get("/api/v1/posts?status=queued", headers=auth_headers)
    assert response.status_code == 200
    for post in response.json()["data"]:
        assert post["status"] == "queued"


# ──────────────────────────── Get ────────────────────────────


@pytest.mark.asyncio
async def test_get_post_returns_200(
    client: AsyncClient, auth_headers: dict, account: AccountModel
):
    with patch("domain.services.post_service.PostService._enqueue"):
        create = await client.post(
            "/api/v1/posts",
            json=_post_payload(account.id),
            headers=auth_headers,
        )
    post_id = create.json()["data"]["id"]
    response = await client.get(f"/api/v1/posts/{post_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["data"]["id"] == post_id


@pytest.mark.asyncio
async def test_get_nonexistent_post_returns_404(
    client: AsyncClient, auth_headers: dict
):
    response = await client.get("/api/v1/posts/nonexistent", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "POST_NOT_FOUND"


# ──────────────────────────── Publish-now ────────────────────────────


@pytest.mark.asyncio
async def test_publish_now_queues_pending_post(
    client: AsyncClient, auth_headers: dict, account: AccountModel
):
    with patch("domain.services.post_service.PostService._enqueue"):
        create = await client.post(
            "/api/v1/posts",
            json=_post_payload(account.id, scheduled_at="2030-01-01T00:00:00Z"),
            headers=auth_headers,
        )
        post_id = create.json()["data"]["id"]
        assert create.json()["data"]["status"] == "pending"

        response = await client.post(
            f"/api/v1/posts/{post_id}/publish-now", headers=auth_headers
        )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "queued"

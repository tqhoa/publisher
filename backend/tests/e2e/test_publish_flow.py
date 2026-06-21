"""E2E: Create post → publish-now → verify status=queued (mocked broker)."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch

from infrastructure.database.models.user import UserModel
from infrastructure.database.models.account import AccountModel
from shared.helpers.hash import hash_password
from shared.helpers.jwt import create_access_token


@pytest.fixture
async def e2e_user(db_session: AsyncSession) -> UserModel:
    user = UserModel(
        email="e2e_publish@publisher.local",
        password_hash=hash_password("E2EPass123!"),
        role="admin",
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def e2e_account(db_session: AsyncSession, e2e_user: UserModel) -> AccountModel:
    acc = AccountModel(
        platform="facebook",
        username="e2e_publish_user",
        created_by=e2e_user.id,
    )
    db_session.add(acc)
    await db_session.flush()
    return acc


@pytest.fixture
def auth_headers(e2e_user: UserModel) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(e2e_user.id, e2e_user.role)}"}


@pytest.mark.asyncio
async def test_create_post_and_publish_now(
    client: AsyncClient, auth_headers: dict, e2e_account: AccountModel
):
    with patch("domain.services.post_service.PostService._enqueue"):
        # 1. Create pending post (scheduled)
        create = await client.post(
            "/api/v1/posts",
            json={
                "account_id": e2e_account.id,
                "platform": "facebook",
                "content_type": "text",
                "caption": "E2E test post",
                "scheduled_at": "2030-12-31T00:00:00Z",
            },
            headers=auth_headers,
        )
        assert create.status_code == 201
        post_id = create.json()["data"]["id"]
        assert create.json()["data"]["status"] == "pending"

        # 2. Publish now → status becomes queued
        publish = await client.post(
            f"/api/v1/posts/{post_id}/publish-now",
            headers=auth_headers,
        )
        assert publish.status_code == 200
        assert publish.json()["data"]["status"] == "queued"

    # 3. Get post → confirm queued
    get = await client.get(f"/api/v1/posts/{post_id}", headers=auth_headers)
    assert get.status_code == 200
    assert get.json()["data"]["status"] == "queued"


@pytest.mark.asyncio
async def test_immediate_post_starts_queued(
    client: AsyncClient, auth_headers: dict, e2e_account: AccountModel
):
    with patch("domain.services.post_service.PostService._enqueue"):
        create = await client.post(
            "/api/v1/posts",
            json={
                "account_id": e2e_account.id,
                "platform": "facebook",
                "content_type": "text",
                "caption": "Immediate publish",
            },
            headers=auth_headers,
        )
    assert create.status_code == 201
    assert create.json()["data"]["status"] == "queued"


@pytest.mark.asyncio
async def test_retry_failed_post(
    client: AsyncClient, auth_headers: dict, e2e_account: AccountModel, db_session: AsyncSession
):
    with patch("domain.services.post_service.PostService._enqueue"):
        create = await client.post(
            "/api/v1/posts",
            json={
                "account_id": e2e_account.id,
                "platform": "facebook",
                "content_type": "text",
                "caption": "Will fail",
            },
            headers=auth_headers,
        )
        post_id = create.json()["data"]["id"]

    # Manually set to failed via DB
    from domain.repositories.post_repository import PostRepository
    repo = PostRepository(db_session)
    post = await repo.find_by_id(post_id)
    assert post is not None
    await repo.update(post, status="failed", error_message="Playwright timeout")
    await db_session.flush()

    with patch("domain.services.post_service.PostService._enqueue"):
        retry = await client.post(f"/api/v1/posts/{post_id}/retry", headers=auth_headers)
    assert retry.status_code == 200
    assert retry.json()["data"]["status"] == "queued"
    assert retry.json()["data"]["retry_count"] == 1

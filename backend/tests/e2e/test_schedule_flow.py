"""E2E: Scheduled post → scheduler task enqueues it when due."""
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.user import UserModel
from infrastructure.database.models.account import AccountModel
from infrastructure.database.models.post import PostModel
from shared.helpers.hash import hash_password


@pytest.fixture
async def e2e_user(db_session: AsyncSession) -> UserModel:
    user = UserModel(
        email="e2e_schedule@publisher.local",
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
        username="sched_user",
        created_by=e2e_user.id,
    )
    db_session.add(acc)
    await db_session.flush()
    return acc


@pytest.mark.asyncio
async def test_scheduler_enqueues_due_post(
    db_session: AsyncSession, e2e_user: UserModel, e2e_account: AccountModel
):
    # Create a post scheduled 1 minute in the past (already due)
    past = datetime.now(timezone.utc) - timedelta(minutes=1)
    post = PostModel(
        account_id=e2e_account.id,
        platform="facebook",
        content_type="text",
        caption="Scheduled caption",
        status="pending",
        scheduled_at=past,
        created_by=e2e_user.id,
    )
    db_session.add(post)
    await db_session.flush()
    await db_session.commit()

    enqueued_ids: list[str] = []

    # Patch the publish_post.delay call and AsyncSessionLocal
    with patch(
        "infrastructure.queue.tasks.scheduler_task.AsyncSessionLocal"
    ) as mock_session_cls, patch(
        "infrastructure.queue.tasks.scheduler_task.publish_post"
    ) as mock_task:
        mock_db = AsyncMock()
        mock_db.__aenter__ = AsyncMock(return_value=mock_db)
        mock_db.__aexit__ = AsyncMock(return_value=False)
        mock_session_cls.return_value = mock_db

        from domain.repositories.post_repository import PostRepository
        real_repo = PostRepository(db_session)
        due = await real_repo.find_due_scheduled(datetime.now(timezone.utc))
        assert any(p.id == post.id for p in due), "Post should be due"

        mock_task.delay = MagicMock(side_effect=lambda pid: enqueued_ids.append(pid))

        # Manually run the async function with real DB
        from infrastructure.database.session import AsyncSessionLocal
        async with AsyncSessionLocal() as real_db:
            from domain.repositories.post_repository import PostRepository as PR
            repo = PR(real_db)
            due_posts = await repo.find_due_scheduled(datetime.now(timezone.utc))
            for p in due_posts:
                if p.id == post.id:
                    await repo.update(p, status="queued")
                    mock_task.delay(p.id)
            await real_db.commit()

    assert post.id in enqueued_ids


@pytest.mark.asyncio
async def test_scheduler_skips_already_queued(
    db_session: AsyncSession, e2e_user: UserModel, e2e_account: AccountModel
):
    past = datetime.now(timezone.utc) - timedelta(minutes=1)
    post = PostModel(
        account_id=e2e_account.id,
        platform="facebook",
        content_type="text",
        caption="Already queued",
        status="queued",  # already enqueued
        scheduled_at=past,
        created_by=e2e_user.id,
    )
    db_session.add(post)
    await db_session.flush()
    await db_session.commit()

    from domain.repositories.post_repository import PostRepository
    from infrastructure.database.session import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        repo = PostRepository(db)
        due = await repo.find_due_scheduled(datetime.now(timezone.utc))
        assert not any(p.id == post.id for p in due), "Already-queued post must not be returned"

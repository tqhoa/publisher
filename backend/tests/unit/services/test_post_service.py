import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from domain.services.post_service import PostService
from infrastructure.database.models.post import PostModel
from shared.exceptions import AppError


def _mock_post(**kwargs) -> MagicMock:
    post = MagicMock(spec=PostModel)
    post.id = kwargs.get("id", "post-1")
    post.account_id = kwargs.get("account_id", "acc-1")
    post.platform = kwargs.get("platform", "facebook")
    post.content_type = kwargs.get("content_type", "text")
    post.caption = kwargs.get("caption", "Hello")
    post.hashtags = kwargs.get("hashtags", None)
    post.media_urls = kwargs.get("media_urls", None)
    post.status = kwargs.get("status", "pending")
    post.scheduled_at = kwargs.get("scheduled_at", None)
    post.published_at = kwargs.get("published_at", None)
    post.error_message = kwargs.get("error_message", None)
    post.retry_count = kwargs.get("retry_count", 0)
    post.created_at = kwargs.get("created_at", None)
    return post


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def service(mock_db):
    svc = PostService(mock_db)
    svc._repo = AsyncMock()
    return svc


@pytest.mark.asyncio
async def test_get_not_found_raises_404(service):
    service._repo.find_by_id.return_value = None
    with pytest.raises(AppError) as exc:
        await service.get("nonexistent")
    assert exc.value.status_code == 404
    assert exc.value.code == "POST_NOT_FOUND"


@pytest.mark.asyncio
async def test_publish_now_pending_post(service):
    post = _mock_post(status="pending")
    service._repo.find_by_id.return_value = post
    service._repo.update.return_value = _mock_post(status="queued")

    with patch.object(service, "_enqueue"):
        result = await service.publish_now("post-1")

    assert result.status == "queued"


@pytest.mark.asyncio
async def test_publish_now_already_published_raises_409(service):
    post = _mock_post(status="published")
    service._repo.find_by_id.return_value = post

    with pytest.raises(AppError) as exc:
        await service.publish_now("post-1")
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_retry_failed_post(service):
    post = _mock_post(status="failed", retry_count=1)
    service._repo.find_by_id.return_value = post
    service._repo.update.return_value = _mock_post(status="queued", retry_count=2)

    with patch.object(service, "_enqueue"):
        result = await service.retry("post-1")

    assert result.status == "queued"


@pytest.mark.asyncio
async def test_retry_non_failed_raises_409(service):
    post = _mock_post(status="pending")
    service._repo.find_by_id.return_value = post

    with pytest.raises(AppError) as exc:
        await service.retry("post-1")
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_delete_publishing_raises_409(service):
    post = _mock_post(status="publishing")
    service._repo.find_by_id.return_value = post

    with pytest.raises(AppError) as exc:
        await service.delete("post-1")
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_mark_published_sets_timestamp(service):
    from datetime import datetime
    post = _mock_post(status="publishing")
    updated = _mock_post(status="published")
    updated.published_at = datetime.now()
    service._repo.find_by_id.return_value = post
    service._repo.update.return_value = updated

    result = await service.mark_published("post-1")
    assert result.status == "published"
    assert result.published_at is not None


@pytest.mark.asyncio
async def test_mark_failed_sets_error_message(service):
    post = _mock_post(status="publishing")
    updated = _mock_post(status="failed", error_message="timeout")
    service._repo.find_by_id.return_value = post
    service._repo.update.return_value = updated

    result = await service.mark_failed("post-1", "timeout")
    assert result.status == "failed"
    assert result.error_message == "timeout"

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from domain.repositories.post_repository import PostRepository
from infrastructure.database.models.post import PostModel
from schemas.common import PaginatedResponse, PaginationMeta
from schemas.post import PostCreate, PostResponse
from shared.exceptions import AppError


class PostService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = PostRepository(db)

    async def create(self, data: PostCreate, created_by: str) -> PostResponse:
        status = "pending" if data.scheduled_at else "queued"
        post = await self._repo.create(
            account_id=data.account_id,
            platform=data.platform,
            content_type=data.content_type,
            caption=data.caption,
            hashtags=data.hashtags,
            media_urls=data.media_urls,
            scheduled_at=data.scheduled_at,
            status=status,
            created_by=created_by,
        )
        if status == "queued":
            self._enqueue(post.id)
        return PostResponse.model_validate(post)

    async def get(self, post_id: str) -> PostResponse:
        post = await self._get_or_404(post_id)
        return PostResponse.model_validate(post)

    async def list(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        status: str | None = None,
        platform: str | None = None,
        account_id: str | None = None,
    ) -> PaginatedResponse[PostResponse]:
        items, total = await self._repo.list(
            page=page, limit=limit, status=status, platform=platform, account_id=account_id
        )
        return PaginatedResponse(
            data=[PostResponse.model_validate(p) for p in items],
            pagination=PaginationMeta(
                page=page,
                limit=limit,
                total=total,
                total_pages=(total + limit - 1) // limit,
            ),
        )

    async def delete(self, post_id: str) -> None:
        post = await self._get_or_404(post_id)
        if post.status in ("publishing",):
            raise AppError("Cannot delete post currently being published", 409, "POST_PUBLISHING")
        await self._repo.update(post, status="cancelled")

    async def publish_now(self, post_id: str) -> PostResponse:
        post = await self._get_or_404(post_id)
        if post.status not in ("pending", "failed"):
            raise AppError("Post cannot be published in current state", 409, "INVALID_STATUS")
        post = await self._repo.update(post, status="queued")
        self._enqueue(post.id)
        return PostResponse.model_validate(post)

    async def retry(self, post_id: str) -> PostResponse:
        post = await self._get_or_404(post_id)
        if post.status != "failed":
            raise AppError("Only failed posts can be retried", 409, "INVALID_STATUS")
        post = await self._repo.update(
            post, status="queued", error_message=None, retry_count=post.retry_count + 1
        )
        self._enqueue(post.id)
        return PostResponse.model_validate(post)

    async def mark_publishing(self, post_id: str) -> PostModel:
        post = await self._get_or_404(post_id)
        return await self._repo.update(post, status="publishing")

    async def mark_published(self, post_id: str) -> PostModel:
        post = await self._get_or_404(post_id)
        return await self._repo.update(post, status="published", published_at=datetime.now(timezone.utc))

    async def mark_failed(self, post_id: str, error_message: str) -> PostModel:
        post = await self._get_or_404(post_id)
        return await self._repo.update(post, status="failed", error_message=error_message)

    async def _get_or_404(self, post_id: str) -> PostModel:
        post = await self._repo.find_by_id(post_id)
        if not post:
            raise AppError("Post not found", 404, "POST_NOT_FOUND")
        return post

    def _enqueue(self, post_id: str) -> None:
        from infrastructure.queue.tasks.publish_task import publish_post
        publish_post.delay(post_id)

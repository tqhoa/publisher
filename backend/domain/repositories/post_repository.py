from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.post import PostModel


class PostRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, post_id: str) -> PostModel | None:
        result = await self._db.execute(select(PostModel).where(PostModel.id == post_id))
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        status: str | None = None,
        platform: str | None = None,
        account_id: str | None = None,
    ) -> tuple[list[PostModel], int]:
        from sqlalchemy import func
        query = select(PostModel).order_by(PostModel.created_at.desc())
        if status:
            query = query.where(PostModel.status == status)
        if platform:
            query = query.where(PostModel.platform == platform)
        if account_id:
            query = query.where(PostModel.account_id == account_id)

        count_result = await self._db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar_one()
        result = await self._db.execute(query.offset((page - 1) * limit).limit(limit))
        return list(result.scalars().all()), total

    async def create(self, **kwargs: object) -> PostModel:
        post = PostModel(**kwargs)
        self._db.add(post)
        await self._db.flush()
        await self._db.refresh(post)
        return post

    async def update(self, post: PostModel, **fields: object) -> PostModel:
        for key, value in fields.items():
            setattr(post, key, value)
        await self._db.flush()
        await self._db.refresh(post)
        return post

    async def find_due_scheduled(self, now: datetime) -> list[PostModel]:
        result = await self._db.execute(
            select(PostModel).where(
                PostModel.status == "pending",
                PostModel.scheduled_at <= now,
            )
        )
        return list(result.scalars().all())

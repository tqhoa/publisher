from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.audit_log import AuditLogModel


class AuditLogRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        *,
        action: str,
        user_id: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        metadata: dict | None = None,  # type: ignore[type-arg]
        ip_address: str | None = None,
    ) -> AuditLogModel:
        log = AuditLogModel(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            log_data=metadata,
            ip_address=ip_address,
        )
        self._db.add(log)
        await self._db.flush()
        return log

    async def list(
        self,
        *,
        page: int = 1,
        limit: int = 50,
        user_id: str | None = None,
        action: str | None = None,
    ) -> tuple[list[AuditLogModel], int]:
        query = select(AuditLogModel).order_by(AuditLogModel.created_at.desc())
        if user_id:
            query = query.where(AuditLogModel.user_id == user_id)
        if action:
            query = query.where(AuditLogModel.action == action)

        from sqlalchemy import func, select as sa_select
        count_result = await self._db.execute(
            sa_select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar_one()

        result = await self._db.execute(query.offset((page - 1) * limit).limit(limit))
        return list(result.scalars().all()), total

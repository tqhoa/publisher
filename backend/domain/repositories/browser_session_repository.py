from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.browser_session import BrowserSessionModel


class BrowserSessionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def upsert(
        self,
        *,
        account_id: str,
        status: str,
        node_id: str = "local",
    ) -> BrowserSessionModel:
        result = await self._db.execute(
            select(BrowserSessionModel).where(BrowserSessionModel.account_id == account_id)
        )
        record = result.scalar_one_or_none()
        if record:
            record.status = status
            record.last_activity_at = datetime.now(timezone.utc)
        else:
            record = BrowserSessionModel(
                account_id=account_id,
                status=status,
                node_id=node_id,
            )
            self._db.add(record)
        await self._db.flush()
        return record

    async def update_status(self, account_id: str, status: str) -> BrowserSessionModel | None:
        result = await self._db.execute(
            select(BrowserSessionModel).where(BrowserSessionModel.account_id == account_id)
        )
        record = result.scalar_one_or_none()
        if record:
            record.status = status
            record.last_activity_at = datetime.now(timezone.utc)
            await self._db.flush()
        return record

    async def list_all(self) -> list[BrowserSessionModel]:
        result = await self._db.execute(
            select(BrowserSessionModel).order_by(BrowserSessionModel.last_activity_at.desc())
        )
        return list(result.scalars().all())

    async def find_by_account(self, account_id: str) -> BrowserSessionModel | None:
        result = await self._db.execute(
            select(BrowserSessionModel).where(BrowserSessionModel.account_id == account_id)
        )
        return result.scalar_one_or_none()

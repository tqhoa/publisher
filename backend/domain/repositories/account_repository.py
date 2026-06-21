from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.account import AccountModel


class AccountRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, account_id: str) -> AccountModel | None:
        result = await self._db.execute(select(AccountModel).where(AccountModel.id == account_id))
        return result.scalar_one_or_none()

    async def list(
        self, *, page: int = 1, limit: int = 20, platform: str | None = None
    ) -> tuple[list[AccountModel], int]:
        from sqlalchemy import func
        query = select(AccountModel).where(AccountModel.status != "deleted")
        if platform:
            query = query.where(AccountModel.platform == platform)
        query = query.order_by(AccountModel.created_at.desc())

        count_result = await self._db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar_one()
        result = await self._db.execute(query.offset((page - 1) * limit).limit(limit))
        return list(result.scalars().all()), total

    async def create(self, *, platform: str, username: str, created_by: str) -> AccountModel:
        account = AccountModel(platform=platform, username=username, created_by=created_by)
        self._db.add(account)
        await self._db.flush()
        await self._db.refresh(account)
        return account

    async def update(self, account: AccountModel, **fields: object) -> AccountModel:
        for key, value in fields.items():
            setattr(account, key, value)
        await self._db.flush()
        await self._db.refresh(account)
        return account

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.user import UserModel


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_email(self, email: str) -> UserModel | None:
        result = await self._db.execute(select(UserModel).where(UserModel.email == email))
        return result.scalar_one_or_none()

    async def find_by_id(self, user_id: str) -> UserModel | None:
        result = await self._db.execute(select(UserModel).where(UserModel.id == user_id))
        return result.scalar_one_or_none()

    async def create(self, *, email: str, password_hash: str, role: str = "operator") -> UserModel:
        user = UserModel(email=email, password_hash=password_hash, role=role)
        self._db.add(user)
        await self._db.flush()
        await self._db.refresh(user)
        return user

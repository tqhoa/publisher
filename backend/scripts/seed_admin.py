"""Create the initial admin user. Run once on first deployment."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.database.session import AsyncSessionLocal
from infrastructure.database.models.user import UserModel
from shared.config import settings
from shared.helpers.hash import hash_password
from sqlalchemy import select


async def seed_admin() -> None:
    email = settings.seed_admin_email
    password = settings.seed_admin_password

    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(UserModel).where(UserModel.email == email))
        if existing.scalar_one_or_none():
            print(f"Admin user {email} already exists.")
            return

        admin = UserModel(
            email=email,
            password_hash=hash_password(password),
            role="admin",
        )
        db.add(admin)
        await db.commit()
        print(f"Admin user created: {email}")


if __name__ == "__main__":
    asyncio.run(seed_admin())

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from domain.services.auth_service import AuthService
from infrastructure.database.models.user import UserModel
from infrastructure.database.session import get_db
from shared.exceptions import AppError
from sqlalchemy.ext.asyncio import AsyncSession

_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(_bearer),
    db: AsyncSession = Depends(get_db),
) -> UserModel:
    service = AuthService(db)
    return await service.get_current_user(credentials.credentials)


async def require_admin(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    if current_user.role != "admin":
        raise AppError("Admin role required", 403, "FORBIDDEN")
    return current_user

from sqlalchemy.ext.asyncio import AsyncSession

from domain.repositories.user_repository import UserRepository
from infrastructure.database.models.user import UserModel
from schemas.auth import LoginRequest, LoginResponse, TokenRefreshResponse
from shared.exceptions import AppError
from shared.helpers.hash import verify_password
from shared.helpers.jwt import create_access_token, create_refresh_token, decode_token


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = UserRepository(db)

    async def login(self, request: LoginRequest) -> LoginResponse:
        user = await self._repo.find_by_email(request.email)
        if not user or not verify_password(request.password, user.password_hash):
            raise AppError("Invalid email or password", 401, "INVALID_CREDENTIALS")

        return LoginResponse(
            access_token=create_access_token(user.id, user.role),
            refresh_token=create_refresh_token(user.id),
            role=user.role,
        )

    async def refresh(self, refresh_token: str) -> TokenRefreshResponse:
        payload = decode_token(refresh_token, expected_type="refresh")
        user = await self._repo.find_by_id(payload["sub"])
        if not user:
            raise AppError("User not found", 401, "INVALID_TOKEN")

        return TokenRefreshResponse(
            access_token=create_access_token(user.id, user.role),
        )

    async def get_current_user(self, token: str) -> UserModel:
        payload = decode_token(token, expected_type="access")
        user = await self._repo.find_by_id(payload["sub"])
        if not user:
            raise AppError("User not found", 401, "INVALID_TOKEN")
        return user

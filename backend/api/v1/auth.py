from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from domain.services.auth_service import AuthService
from infrastructure.database.session import get_db
from schemas.auth import LoginRequest, LoginResponse, TokenRefreshRequest, TokenRefreshResponse
from schemas.common import ApiResponse

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/login", response_model=ApiResponse[LoginResponse])
@limiter.limit("5/15minutes")
async def login(
    request: Request,
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[LoginResponse]:
    service = AuthService(db)
    result = await service.login(body)
    return ApiResponse(data=result)


@router.post("/refresh", response_model=ApiResponse[TokenRefreshResponse])
async def refresh_token(
    body: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TokenRefreshResponse]:
    service = AuthService(db)
    result = await service.refresh(body.refresh_token)
    return ApiResponse(data=result)


@router.post("/logout", response_model=ApiResponse[dict])  # type: ignore[type-arg]
async def logout() -> ApiResponse[dict]:  # type: ignore[type-arg]
    # Stateless JWT — client drops the token. Future: add token blocklist via Redis.
    return ApiResponse(data={}, message="Logged out successfully")

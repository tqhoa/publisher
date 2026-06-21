from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_user
from domain.services.account_service import AccountService
from infrastructure.database.models.user import UserModel
from infrastructure.database.session import get_db
from schemas.account import (
    AccountCreate,
    AccountResponse,
    AccountUpdate,
    CookieImportRequest,
    HealthCheckResponse,
)
from schemas.common import ApiResponse, PaginatedResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse[AccountResponse])
async def list_accounts(
    page: int = 1,
    limit: int = 20,
    platform: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user),
) -> PaginatedResponse[AccountResponse]:
    service = AccountService(db)
    return await service.list(page=page, limit=limit, platform=platform)


@router.post("", response_model=ApiResponse[AccountResponse], status_code=201)
async def create_account(
    body: AccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> ApiResponse[AccountResponse]:
    service = AccountService(db)
    result = await service.create(body, created_by=current_user.id)
    return ApiResponse(data=result)


@router.get("/{account_id}", response_model=ApiResponse[AccountResponse])
async def get_account(
    account_id: str,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user),
) -> ApiResponse[AccountResponse]:
    service = AccountService(db)
    return ApiResponse(data=await service.get(account_id))


@router.patch("/{account_id}", response_model=ApiResponse[AccountResponse])
async def update_account(
    account_id: str,
    body: AccountUpdate,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user),
) -> ApiResponse[AccountResponse]:
    service = AccountService(db)
    return ApiResponse(data=await service.update(account_id, body))


@router.delete("/{account_id}", status_code=204)
async def delete_account(
    account_id: str,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user),
) -> None:
    service = AccountService(db)
    await service.delete(account_id)


@router.post("/{account_id}/cookie", response_model=ApiResponse[AccountResponse])
async def import_cookie(
    account_id: str,
    body: CookieImportRequest,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user),
) -> ApiResponse[AccountResponse]:
    service = AccountService(db)
    return ApiResponse(data=await service.import_cookie(account_id, body))


@router.get("/{account_id}/health", response_model=ApiResponse[HealthCheckResponse])
async def health_check(
    account_id: str,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user),
) -> ApiResponse[HealthCheckResponse]:
    service = AccountService(db)
    return ApiResponse(data=await service.check_health(account_id))

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from domain.repositories.account_repository import AccountRepository
from infrastructure.database.models.account import AccountModel
from infrastructure.encryption.cookie_cipher import decrypt, encrypt
from schemas.account import (
    AccountCreate,
    AccountResponse,
    AccountUpdate,
    CookieImportRequest,
    HealthCheckResponse,
)
from schemas.common import PaginatedResponse, PaginationMeta
from shared.exceptions import AppError


class AccountService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = AccountRepository(db)

    async def create(self, data: AccountCreate, created_by: str) -> AccountResponse:
        account = await self._repo.create(
            platform=data.platform,
            username=data.username,
            created_by=created_by,
        )
        return AccountResponse.model_validate(account)

    async def get(self, account_id: str) -> AccountResponse:
        account = await self._get_or_404(account_id)
        return AccountResponse.model_validate(account)

    async def list(
        self, *, page: int = 1, limit: int = 20, platform: str | None = None
    ) -> PaginatedResponse[AccountResponse]:
        items, total = await self._repo.list(page=page, limit=limit, platform=platform)
        return PaginatedResponse(
            data=[AccountResponse.model_validate(a) for a in items],
            pagination=PaginationMeta(
                page=page,
                limit=limit,
                total=total,
                total_pages=(total + limit - 1) // limit,
            ),
        )

    async def update(self, account_id: str, data: AccountUpdate) -> AccountResponse:
        account = await self._get_or_404(account_id)
        updates = data.model_dump(exclude_none=True)
        if updates:
            account = await self._repo.update(account, **updates)
        return AccountResponse.model_validate(account)

    async def delete(self, account_id: str) -> None:
        account = await self._get_or_404(account_id)
        await self._repo.update(account, status="inactive")

    async def import_cookie(self, account_id: str, data: CookieImportRequest) -> AccountResponse:
        account = await self._get_or_404(account_id)
        encrypted = encrypt(data.cookie_json)
        account = await self._repo.update(
            account,
            cookie_encrypted=encrypted,
            cookie_updated_at=datetime.now(timezone.utc),
            health_status=None,
        )
        return AccountResponse.model_validate(account)

    async def check_health(self, account_id: str) -> HealthCheckResponse:
        account = await self._get_or_404(account_id)
        if not account.cookie_encrypted:
            return HealthCheckResponse(
                account_id=account_id,
                healthy=False,
                checked_at=datetime.now(timezone.utc),
                message="No cookie imported",
            )
        # Actual Playwright check delegated to infrastructure layer (injected in Phase 4)
        # For now: return healthy if cookie exists
        checked_at = datetime.now(timezone.utc)
        await self._repo.update(
            account,
            last_health_check_at=checked_at,
            health_status="healthy",
        )
        return HealthCheckResponse(
            account_id=account_id,
            healthy=True,
            checked_at=checked_at,
        )

    async def _get_or_404(self, account_id: str) -> AccountModel:
        account = await self._repo.find_by_id(account_id)
        if not account or account.status == "deleted":
            raise AppError("Account not found", 404, "ACCOUNT_NOT_FOUND")
        return account

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_user
from domain.repositories.browser_session_repository import BrowserSessionRepository
from infrastructure.database.models.user import UserModel
from infrastructure.database.session import get_db
from schemas.common import ApiResponse
from schemas.session import BrowserSessionResponse

router = APIRouter()


@router.get("", response_model=ApiResponse[list[BrowserSessionResponse]])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user),
) -> ApiResponse[list[BrowserSessionResponse]]:
    repo = BrowserSessionRepository(db)
    sessions = await repo.list_all()
    return ApiResponse(data=[BrowserSessionResponse.model_validate(s) for s in sessions])


@router.get("/{account_id}", response_model=ApiResponse[BrowserSessionResponse])
async def get_session(
    account_id: str,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user),
) -> ApiResponse[BrowserSessionResponse]:
    from shared.exceptions import AppError

    repo = BrowserSessionRepository(db)
    session = await repo.find_by_account(account_id)
    if not session:
        raise AppError("Session not found", 404, "SESSION_NOT_FOUND")
    return ApiResponse(data=BrowserSessionResponse.model_validate(session))

from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_user, require_admin
from domain.repositories.audit_log_repository import AuditLogRepository
from infrastructure.database.models.user import UserModel
from infrastructure.database.session import get_db
from schemas.common import PaginatedResponse, PaginationMeta

router = APIRouter()


class AuditLogResponse(BaseModel):
    id: str
    user_id: str | None
    action: str
    resource_type: str | None
    resource_id: str | None
    ip_address: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("", response_model=PaginatedResponse[AuditLogResponse])
async def list_audit_logs(
    page: int = 1,
    limit: int = 50,
    action: str | None = None,
    user_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(require_admin),
) -> PaginatedResponse[AuditLogResponse]:
    repo = AuditLogRepository(db)
    items, total = await repo.list(page=page, limit=limit, user_id=user_id, action=action)
    return PaginatedResponse(
        data=[AuditLogResponse.model_validate(item) for item in items],
        pagination=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=(total + limit - 1) // limit,
        ),
    )

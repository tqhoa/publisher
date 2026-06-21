from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_user
from domain.services.post_service import PostService
from infrastructure.database.models.user import UserModel
from infrastructure.database.session import get_db
from schemas.common import ApiResponse, PaginatedResponse
from schemas.post import PostCreate, PostResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse[PostResponse])
async def list_posts(
    page: int = 1,
    limit: int = 20,
    status: str | None = None,
    platform: str | None = None,
    account_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user),
) -> PaginatedResponse[PostResponse]:
    svc = PostService(db)
    return await svc.list(page=page, limit=limit, status=status, platform=platform, account_id=account_id)


@router.post("", response_model=ApiResponse[PostResponse], status_code=201)
async def create_post(
    body: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> ApiResponse[PostResponse]:
    svc = PostService(db)
    return ApiResponse(data=await svc.create(body, created_by=current_user.id))


@router.get("/{post_id}", response_model=ApiResponse[PostResponse])
async def get_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user),
) -> ApiResponse[PostResponse]:
    svc = PostService(db)
    return ApiResponse(data=await svc.get(post_id))


@router.delete("/{post_id}", status_code=204)
async def delete_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user),
) -> None:
    svc = PostService(db)
    await svc.delete(post_id)


@router.post("/{post_id}/publish-now", response_model=ApiResponse[PostResponse])
async def publish_now(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user),
) -> ApiResponse[PostResponse]:
    svc = PostService(db)
    return ApiResponse(data=await svc.publish_now(post_id))


@router.post("/{post_id}/retry", response_model=ApiResponse[PostResponse])
async def retry_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user),
) -> ApiResponse[PostResponse]:
    svc = PostService(db)
    return ApiResponse(data=await svc.retry(post_id))

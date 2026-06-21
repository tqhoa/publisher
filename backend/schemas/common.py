from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    message: str | None = None


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    data: list[T]
    pagination: PaginationMeta


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[dict] | None = None  # type: ignore[type-arg]


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail

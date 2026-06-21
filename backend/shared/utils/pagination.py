from dataclasses import dataclass
from typing import TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


@dataclass
class PaginationParams:
    page: int = 1
    limit: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


@dataclass
class PaginatedResult[T]:
    items: list[T]
    total: int
    page: int
    limit: int

    @property
    def total_pages(self) -> int:
        return (self.total + self.limit - 1) // self.limit


async def paginate(
    db: AsyncSession,
    query: Select,  # type: ignore[type-arg]
    params: PaginationParams,
    model: type,
) -> PaginatedResult:  # type: ignore[type-arg]
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    result = await db.execute(query.offset(params.offset).limit(params.limit))
    items = list(result.scalars().all())

    return PaginatedResult(items=items, total=total, page=params.page, limit=params.limit)

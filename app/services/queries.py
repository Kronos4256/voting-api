from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base
from app.core.errors import NotFoundError
from app.schemas.common import PageParams


@dataclass(frozen=True, slots=True)
class PageResult[T]:
    items: Sequence[T]
    total: int
    page: int
    size: int


async def paginate[T](
    session: AsyncSession, statement: Select[tuple[T]], params: PageParams
) -> PageResult[T]:
    total = await session.scalar(select(func.count()).select_from(statement.subquery()))
    items = await session.scalars(statement.limit(params.size).offset(params.offset))
    return PageResult(items=items.all(), total=total or 0, page=params.page, size=params.size)


async def get_or_raise[M: Base](session: AsyncSession, model: type[M], entity_id: int) -> M:
    entity = await session.get(model, entity_id)
    if entity is None:
        raise NotFoundError.for_entity(model.__name__, entity_id)
    return entity

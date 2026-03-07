from sqlalchemy.sql.expression import Select

from config import settings


__all__ = [
    'pagination'
]


def pagination(stmt: Select, page: int = 1, limit: int = settings.ITEM_LIMIT_PER_PAGE) -> Select:
    return (
        stmt
        .limit(limit)
        .offset(page - 1)
    )

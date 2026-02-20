from sqlalchemy import select, asc
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import Insert, Select, Update, Delete

from config import settings


Base = declarative_base()


def pagination(stmt: Insert | Select | Update | Delete, page: int = 1, limit: int = settings.ITEMS_LIMIT_PER_PAGE):
    return (
        stmt
        .limit(limit)
        .offset(page - 1)
    )


def pagination2(db: Session, obj: Base, page: int = 1, limit: int = settings.ITEMS_LIMIT_PER_PAGE):
    stmt = (
        select(obj)
        .limit(limit)
        .offset(page - 1)
        .order_by(asc(obj.id))
    )

    return db.scalars(stmt).all()

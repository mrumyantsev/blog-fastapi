from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, update

from models import PaginationQuery, Tag, TagCreateRequest, ReturnIdResponse
from database import SessionDep
from utils import CurrentUserDep, make_slug, pagination


router = APIRouter(prefix='/api/tags', tags=['tags'])


@router.get('')
def get_all_tags(query: PaginationQuery, db: SessionDep):
    stmt = select(Tag)

    stmt = pagination(stmt, query.page, query.limit)

    tags = db.scalars(stmt.order_by(Tag.id)).all()

    return tags


@router.get('/{slug}')
def get_tag(slug: str, db: SessionDep):
    tag = db.query(Tag).filter(Tag.slug == slug).first()

    return tag


@router.post('')
def create_tag(req: TagCreateRequest, current_user: CurrentUserDep, db: SessionDep):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='login required')

    tag = Tag(
        name=req.name,
        slug=make_slug(req.name),
    )

    db.add(tag)
    db.commit()
    db.refresh(tag)

    return ReturnIdResponse(id=tag.id)


@router.put('/{slug}')
def update_tag(slug: str, req: TagCreateRequest, current_user: CurrentUserDep, db: SessionDep):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='login required')

    tag = db.query(Tag).filter(Tag.slug == slug).first()

    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='tag not found')

    stmt = (
        update(Tag)
        .where(Tag.slug == slug)
        .values(
            name=req.name,
            slug=make_slug(req.title)
        )
    )

    db.execute(stmt)
    db.commit()

    return ReturnIdResponse(id=tag.id)


@router.delete('/{slug}')
def delete_tag(slug: str, current_user: CurrentUserDep, db: SessionDep):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='login required')

    tag = db.query(Tag).filter(Tag.slug == slug).first()

    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='tag not found')

    db.delete(tag)
    db.commit()

    return ReturnIdResponse(id=tag.id)

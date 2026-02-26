from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from database import SessionDep
from models import User, Post, PaginationQuery
from utils.pagination import pagination


router = APIRouter(prefix='/api/users', tags=['users'])


@router.get('')
def get_all_users(query: PaginationQuery, db: SessionDep):
    stmt = select(User)

    stmt = pagination(stmt, query.page, query.limit)

    users = db.scalars(stmt.order_by(User.id)).all()

    return users


@router.get('/{username}')
def get_user_by_username(username: str, db: SessionDep):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')

    return user


@router.get('/{username}/posts')
def get_user_posts(username: str, query: PaginationQuery, db: SessionDep):
    stmt = (
        select(Post, User)
        .join(User, User.id == Post.author)
        .where(User.username == username)
    )

    stmt = pagination(stmt, query.page, query.limit)

    posts = db.scalars(stmt.order_by(Post.id)).all()

    return posts

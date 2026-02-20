from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from database import get_db
from utils.pagination import pagination
from models import User, Post
from config import settings


router = APIRouter(prefix='/api/users', tags=['users'])


@router.get('')
def get_all_users(page: int = 1, limit: int = settings.ITEMS_LIMIT_PER_PAGE, db=Depends(get_db)):
    stmt = pagination(select(User), page, limit)

    users = db.scalars(stmt).all()

    return users


@router.get('/{username}')
def get_user_by_username(username: str, db=Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')

    return user


@router.get('/{username}/posts')
def get_user_posts(username: str, page: int = 1, limit: int = settings.ITEMS_LIMIT_PER_PAGE, db=Depends(get_db)):
    stmt = (
        select(Post, User)
        .join(User, User.id == Post.author)
        .where(User.username == username)
    )

    stmt = pagination(stmt, page, limit)

    posts = db.scalars(stmt).all()

    return posts

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update, func

from models import User, Post, Tag, PostTag, PostCreateRequest, ReturnIdResponse
from database import get_db
from utils.jwt_token import get_current_user
from utils.pagination import pagination
from utils.utils import make_slug
from config import settings


router = APIRouter(prefix='/api/posts', tags=['posts'])


@router.get('')
def get_all_posts(page: int = 1, limit: int = settings.ITEMS_LIMIT_PER_PAGE, tag: str = '', author: str = '', db=Depends(get_db)):
    stmt = select(Post)

    if author != '' and tag == '':
        stmt = select(Post, User).join(User, User.id == Post.author)
    elif tag != '' and author == '':
        stmt = select(Post, PostTag, Tag).join(PostTag, PostTag.post == Post.id)
    elif tag != '' and author != '':
        stmt = (
            select(Post, User, PostTag, Tag)
            .join(PostTag, PostTag.post == Post.id)
            .join(Tag, Tag.id == PostTag.tag)
        )

    if tag != '':
        stmt = stmt.where(Tag.name == tag)

    if author != '':
        stmt = stmt.where(User.username == author)

    stmt = pagination(stmt, page, limit)

    posts = db.scalars(stmt).all()

    for post in posts:
        post.content = post.content[:settings.POST_MAX_PREVIEW_CHARACTERS]

    return posts


@router.get('/{slug}')
def get_post(slug: str, db=Depends(get_db)):
    post = db.query(Post).filter(Post.slug == slug).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')

    stmt = update(Post).where(Post.id == post.id).values(view_count=post.view_count + 1)

    db.execute(stmt)
    db.commit()
    db.refresh(post)
    
    return post


@router.post('')
def create_post(req: PostCreateRequest, current_user: Annotated[User, Depends(get_current_user)], db=Depends(get_db)):
    if len(req.content) < settings.POST_MIN_CHARACTERS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'content length is less than {settings.POST_MIN_CHARACTERS} characters')

    post = Post(
        title=req.title,
        slug=make_slug(req.title),
        content=req.content,
        author=current_user.id
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return ReturnIdResponse(id=post.id)


@router.put('/{slug}')
def update_post(req: PostCreateRequest, slug: str, current_user: Annotated[User, Depends(get_current_user)], db=Depends(get_db)):
    if len(req.content) < settings.POST_MIN_CHARACTERS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'content length is less than {settings.POST_MIN_CHARACTERS} characters')

    post = db.query(Post).filter(Post.slug == slug).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')

    stmt = (
        update(Post)
        .where(Post.slug == slug)
        .values(
            title=req.title,
            slug=make_slug(req.title),
            content=req.content,
            author=current_user.id,
            updated_at=func.now()
        )
    )

    db.execute(stmt)
    db.commit()

    return ReturnIdResponse(id=post.id)


@router.delete('/{slug}')
def delete_post(slug: str, current_user: Annotated[User, Depends(get_current_user)], db=Depends(get_db)):
    post = db.query(Post).filter(Post.slug == slug).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')

    db.delete(post)
    db.commit()

    return ReturnIdResponse(id=post.id)

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
import bleach

from models import User, Post, Comment, CommentCreateRequest, ReturnIdResponse
from database import get_db
from utils.jwt_token import get_current_user
from utils.pagination import pagination
from config import settings


router = APIRouter(prefix='/api', tags=['comments'])


@router.get('/posts/{slug}/comments')
def get_post_comments(slug: str, page: int = 1, limit: int = settings.ITEMS_LIMIT_PER_PAGE, db=Depends(get_db)):
    stmt = (
        select(Comment, Post)
        .join(Post, Post.id == Comment.post)
        .where(Post.slug == slug)
    )

    stmt = pagination(stmt, page, limit)

    comments = db.scalars(stmt).all()

    return comments


@router.post('/posts/{slug}/comments', response_model=ReturnIdResponse)
def create_post_comment(req: CommentCreateRequest, slug: str, current_user: Annotated[User, Depends(get_current_user)], db=Depends(get_db)):
    post = db.query(Post).filter(Post.slug == slug).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')

    if req.parent is not None:
        parent_comment = db.query(Comment).filter(Comment.id == req.parent).first()

        if not parent_comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='parent comment not found')

    comment = Comment(
        post=post.id,
        author=current_user.id,
        text=bleach.clean(req.text),
        parent=req.parent
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return ReturnIdResponse(id=comment.id)


@router.delete('/comments/{id}', response_model=ReturnIdResponse)
def delete_comment(id: int, current_user: Annotated[User, Depends(get_current_user)], db=Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == id).first()

    db.delete(comment)
    db.commit()

    return ReturnIdResponse(id=id)

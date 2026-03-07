from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
import bleach

from models import PaginationQuery, Post, Comment, CommentCreateRequest, ReturnIdResponse
from database import SessionDep
from utils import CurrentUserDep, pagination


router = APIRouter(prefix='/api', tags=['comments'])


@router.get('/posts/{slug}/comments')
def get_post_comments(slug: str, query: PaginationQuery, db: SessionDep):
    stmt = (
        select(Comment, Post)
        .join(Post, Post.id == Comment.post)
        .where(Post.slug == slug)
    )

    stmt = pagination(stmt, query.page, query.limit)

    comments = db.scalars(stmt.order_by(Comment.id)).all()

    return comments


@router.post('/posts/{slug}/comments', response_model=ReturnIdResponse)
def create_post_comment(slug: str, req: CommentCreateRequest, current_user: CurrentUserDep, db: SessionDep):
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
def delete_comment(id: int, current_user: CurrentUserDep, db: SessionDep):
    comment = db.query(Comment).filter(Comment.id == id).first()

    if comment.author != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='you are not the author of the comment')

    db.delete(comment)
    db.commit()

    return ReturnIdResponse(id=id)

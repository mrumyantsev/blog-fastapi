from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, update, and_, func
from sqlalchemy.sql.expression import Select

from models import TagAuthorPaginationQuery, User, Post, Tag, PostTag, PostCreateRequest, ReturnIdResponse
from database import SessionDep
from utils import CurrentUserDep, make_slug, pagination
from config import settings


router = APIRouter(prefix='/api/posts', tags=['posts'])


@router.get('')
def get_all_posts(query: TagAuthorPaginationQuery, db: SessionDep):
    stmt: Select = None

    if query.author != '' and query.tag == '':
        stmt = (
            select(Post, User)
            .join(User, User.id == Post.author)
            .where(User.username == query.author)
        )
    elif query.tag != '' and query.author == '':
        stmt = (
            select(Post, PostTag, Tag)
            .join(PostTag, PostTag.post == Post.id)
            .join(Tag, Tag.id == PostTag.tag)
            .where(Tag.name == query.tag)
        )
    elif query.author != '' and query.tag != '':
        stmt = (
            select(Post, User, PostTag, Tag)
            .join(User, User.id == Post.author)
            .join(PostTag, PostTag.post == Post.id)
            .join(Tag, Tag.id == PostTag.tag)
            .where(and_(User.username == query.author, Tag.name == query.tag))
        )
    else:
        stmt = select(Post)

    stmt = pagination(stmt, query.page, query.limit)

    posts = db.scalars(stmt.order_by(Post.id)).all()

    for post in posts:
        post.content = post.content[:settings.POST_MAX_PREVIEW_CHARACTERS]

    return posts


@router.get('/{slug}')
def get_post(slug: str, db: SessionDep):
    post = db.query(Post).filter(Post.slug == slug).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')

    stmt = update(Post).where(Post.id == post.id).values(view_count=post.view_count + 1)

    db.execute(stmt)
    db.commit()
    db.refresh(post)
    
    return post


@router.post('')
def create_post(req: PostCreateRequest, current_user: CurrentUserDep, db: SessionDep):
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
def update_post(slug: str, req: PostCreateRequest, current_user: CurrentUserDep, db: SessionDep):
    if len(req.content) < settings.POST_MIN_CHARACTERS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'content length is less than {settings.POST_MIN_CHARACTERS} characters')

    post = db.query(Post).filter(Post.slug == slug).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')

    if post.author != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='you are not the author of the post')

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
def delete_post(slug: str, current_user: CurrentUserDep, db: SessionDep):
    post = db.query(Post).filter(Post.slug == slug).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')

    if post.author != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='you are not the author of the post')

    db.delete(post)
    db.commit()

    return ReturnIdResponse(id=post.id)

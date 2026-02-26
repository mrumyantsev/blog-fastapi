from typing import Annotated

from fastapi import Query
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel, Field

from config import settings


Base = declarative_base()


class Pagination(BaseModel):
    page: int = Field(1, ge=1, description='Page offset.')
    limit: int = Field(settings.ITEM_LIMIT_PER_PAGE, ge=0, le=100, description='Item limit per page.')


PaginationQuery = Annotated[Pagination, Query()]


class TagAuthorPagination(Pagination, BaseModel):
    tag: str = Field('', description='Search by exact tag name.')
    author: str = Field('', description='Search by exact post author username.')


TagAuthorPaginationQuery = Annotated[TagAuthorPagination, Query()]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class ReturnIdResponse(BaseModel):
    id: int


class UserCreateRequest(BaseModel):
    username: str
    password: str
    email: str


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    date_joined = Column(DateTime, default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class PostCreateRequest(BaseModel):
    title: str
    content: str


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    content = Column(String, nullable=False)
    author = Column(Integer, ForeignKey(User.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), nullable=False)
    status = Column(Integer, default=1, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)


class CommentCreateRequest(BaseModel):
    text: str
    parent: int | None = Field(default=None, description="parent comment id (optional)")


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    post = Column(Integer, ForeignKey(Post.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    author = Column(Integer, ForeignKey(User.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    parent = Column(Integer, ForeignKey('comments.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)


class TagCreateRequest(BaseModel):
    name: str


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=True, nullable=False)


class PostTag(Base):
    __tablename__ = 'posts_tags'

    id = Column(Integer, primary_key=True)
    post = Column(Integer, nullable=False)
    tag = Column(Integer, nullable=False)

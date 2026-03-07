from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from models import User, UserCreateRequest, ReturnIdResponse, TokenResponse
from database import SessionDep
from utils import is_email_valid, is_password_verified, get_password_hash, create_access_token


router = APIRouter(prefix='/api/auth', tags=['auth'])
OAuth2PasswordRequest = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/register', response_model=ReturnIdResponse)
def register(req: UserCreateRequest, db: SessionDep):
    if not is_email_valid(req.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='email is invalid')

    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='user already exists')

    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='email is used')

    user = User(
        username=req.username,
        password=get_password_hash(req.password),
        email=req.email
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return ReturnIdResponse(id=user.id)


@router.post('/login', response_model=TokenResponse)
def login(req: OAuth2PasswordRequest, db: SessionDep):
    user = db.query(User).filter(User.username == req.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='user not exists')

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='inactive user')

    if not is_password_verified(req.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='incorrect password')

    return TokenResponse(
        access_token=create_access_token(req.username),
        token_type='bearer',
    )

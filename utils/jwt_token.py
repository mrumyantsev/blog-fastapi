from typing import Annotated

from datetime import datetime, timedelta
from typing import Any, Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError

from config import settings
from database import SessionDep
from models import User


__all__ = [
    'create_access_token', 'create_refresh_token',
    'CurrentUserDep'
]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.TOKEN_URL)


def create_access_token(subject: str) -> str:
    """
    Creates JWT access token.
    """

    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        'sub': str(subject),
        'exp': expire,
        'iat': datetime.utcnow(),
    }

    encoded_jwt = jwt.encode(
        claims=payload,
        key=settings.TOKEN_SECRET_KEY,
        algorithm=settings.TOKEN_ENCRYPTING_ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(subject: str) -> str:
    """
    Creates JWT refresh token.
    """

    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        'sub': str(subject),
        'exp': expire,
        'iat': datetime.utcnow(),
        'token_type': 'refresh'
    }

    encoded_jwt = jwt.encode(
        claims=payload,
        key=settings.TOKEN_SECRET_KEY,
        algorithm=settings.TOKEN_ENCRYPTING_ALGORITHM
    )

    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decodes JWT token.
    """

    payload = jwt.decode(
        token=token,
        key=settings.TOKEN_SECRET_KEY,
        algorithms=[settings.TOKEN_ENCRYPTING_ALGORITHM]
    )

    return payload


def get_current_user(db: SessionDep, token: str = Depends(oauth2_scheme)) -> User:
    """
    Validates token and returns the user DB record model.
    """

    try:
        payload = decode_token(token)
        username = payload.get('sub')
        user = db.query(User).filter(User.username == username).first()

        if user and not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='inactive user',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        return user
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='token expired',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )


CurrentUserDep = Annotated[User, Depends(get_current_user)]

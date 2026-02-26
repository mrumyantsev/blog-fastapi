from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def is_password_verified(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies plain password against hashed password.
    """

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generates password hash from plain password.
    """

    return pwd_context.hash(password)

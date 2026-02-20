import os

import secrets
from pydantic_settings import BaseSettings


db_scheme = os.getenv('DB_SCHEME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_database = os.getenv('DB_DATABASE')


class Settings(BaseSettings):
    # General.
    APP_NAME: str = os.getenv('APP_NAME')
    TOKEN_URL: str = os.getenv('TOKEN_URL')
    ITEMS_LIMIT_PER_PAGE: int = int(os.getenv('ITEMS_LIMIT_PER_PAGE'))
    POST_MIN_CHARACTERS: int = int(os.getenv('POST_MIN_CHARACTERS'))
    POST_MAX_PREVIEW_CHARACTERS: int = int(os.getenv('POST_MAX_PREVIEW_CHARACTERS'))

    # Database.
    DATABASE_URL: str = f'{db_scheme}://{db_user}:{db_password}@localhost/{db_database}'

    # Security.
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS'))
    TOKEN_ENCRYPTING_ALGORITHM: str = os.getenv('ALGORITHM')


settings = Settings()

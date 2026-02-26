from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='./.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    # General.
    APP_NAME: str = 'Blog'
    APP_VERSION: str
    TOKEN_URL: str
    ITEM_LIMIT_PER_PAGE: int = 20
    POST_MIN_CHARACTERS: int = 100
    POST_MAX_PREVIEW_CHARACTERS: int = 200

    # Database.
    DB_DRIVER: str
    DB_USER: str
    DB_PASSWORD: str
    DB_DATABASE: str

    # Security.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10
    REFRESH_TOKEN_EXPIRE_DAYS: int = 1
    TOKEN_ENCRYPTING_ALGORITHM: str
    TOKEN_SECRET_KEY: str

    @property
    def database_url(self) -> str:
        """
        Generates the full database connection string.
        """

        return (
            f'{self.DB_DRIVER}://'
            f'{self.DB_USER}:'
            f'{self.DB_PASSWORD}@localhost/'
            f'{self.DB_DATABASE}'
        )


settings = Settings()

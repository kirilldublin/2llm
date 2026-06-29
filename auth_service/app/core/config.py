from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment / .env file.

    This module is configuration only: it never opens a DB connection
    or starts the app, it just exposes a single ``settings`` object.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "auth-service"
    ENV: str = "local"

    # JWT
    JWT_SECRET: str = "change_me_super_secret"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    SQLITE_PATH: str = "./auth.db"
    DATABASE_URL: str | None = None

    @property
    def database_url(self) -> str:
        """Build the async SQLAlchemy connection string.

        Prefers an explicit DATABASE_URL (e.g. Postgres) and otherwise
        falls back to an async SQLite database at SQLITE_PATH.
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"sqlite+aiosqlite:///{self.SQLITE_PATH}"


settings = Settings()

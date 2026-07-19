from pathlib import Path
from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

from app.core.cors import default_cors, CORSSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    db_user: str = "identity_service_user"
    db_password: str = "identity_service_password"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "identity_service"

    @computed_field
    @property
    def database_url(self) -> URL:
        """Async-capable postgresql URL."""
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )

    secret_key: str = "supersecretkey"
    debug: bool = False
    log_level: str = "INFO"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    @computed_field
    @property
    def redis_url(self) -> str:
        """Redis URL."""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    allowed_origins: str = ""

    @property
    def prepare_cors_origins(self) -> tuple[list[str], bool]:
        """
        Parse and prepare CORS origins from ALLOWED_ORIGINS.
        """
        raw = self.allowed_origins.strip()
        if not raw:
            return ["*"], False
        origins = [o.strip() for o in raw.split(",") if o.strip()]

        return origins, True

    @property
    def cors_settings(self) -> CORSSettings:
        """Return CORS settings based on ALLOWED_ORIGINS."""
        origins, allow_credentials = self.prepare_cors_origins
        default_cors.allow_origins = origins
        default_cors.allow_credentials = allow_credentials

        return default_cors

    sentry_dsn: str = ""

    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    smtp_from_email: str = "no-reply@identity-service.local"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()


JWT_ALGORITHM = "HS256"
JWT_ACCESS_EXPIRE_MINUTES = 10
JWT_REFRESH_EXPIRE_DAYS = 7

BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOG_DIR = BASE_DIR / "logs"
ROTATING_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ROTATING_LOG_FILE_BACKUPS = 5

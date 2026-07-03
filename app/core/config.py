"""
Core configuration management.
Handles environment variables, settings, and application constants.
"""
from enum import Enum
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Environment(str, Enum):
    """Application environment."""

    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"
    TEST = "test"


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Use .env file for local development.
    """

    # ── Application ──────────────────────────────────────────────────────
    APP_NAME: str = "PneumoIA Backend"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: Environment = Environment.DEV
    DEBUG: bool = False

    # ── Database ──────────────────────────────────────────────────────────
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 0
    DB_POOL_PRE_PING: bool = True  # Verify connections before use

    # ── JWT & Security ────────────────────────────────────────────────────
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── CORS & Frontend ───────────────────────────────────────────────────
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8000"
    ALLOWED_ORIGINS: list[str] = Field(default_factory=list)

    # ── File Upload ───────────────────────────────────────────────────────
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 50

    # ── Email (SMTP) ──────────────────────────────────────────────────────
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    FROM_EMAIL: str
    SMTP_TLS: bool = True

    # ── SMS (Twilio) ──────────────────────────────────────────────────────
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    ADMIN_PHONE: Optional[str] = None

    # ── Admin & Seeds ─────────────────────────────────────────────────────
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    # ── AWS S3 ────────────────────────────────────────────────────────────
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    AWS_S3_REGION: str = "us-east-1"

    # ── ML Models ─────────────────────────────────────────────────────────
    MODEL_BASE_PATH: str = "app/ml_models/model_base.pkl"
    MODEL_EQUIPE_PATH: str = "app/ml_models/model_equipe.pkl"
    MODEL_METADATA_PATH: str = "app/ml_models/metadata.json"

    # ── Celery (Async Tasks) ──────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    CELERY_TASK_TIME_LIMIT: int = 300  # 5 minutes
    CELERY_TASK_SOFT_TIME_LIMIT: int = 280

    # ── Redis ─────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/2"
    REDIS_CACHE_TTL: int = 3600  # 1 hour

    # ── Logging ───────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # "json" or "text"
    LOG_FILE: Optional[str] = None

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT == Environment.PROD

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.ENVIRONMENT == Environment.DEV


# Load settings from environment
settings = Settings()

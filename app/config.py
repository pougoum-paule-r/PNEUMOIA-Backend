from pydantic_settings import BaseSettings
from pathlib import Path

# Chemin absolu vers le .env — fonctionne peu importe d'où tu lances uvicorn
ENV_FILE = Path(__file__).parent.parent / ".env"

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ── Email SMTP ────────────────────────────────────────────
    SMTP_HOST:     str = "smtp-relay.brevo.com"
    SMTP_PORT:     int = 587
    SMTP_USER:     str
    SMTP_PASSWORD: str
    FROM_EMAIL:    str

    # ── Twilio ────────────────────────────────────────────────
    TWILIO_ACCOUNT_SID:  str
    TWILIO_AUTH_TOKEN:   str
    TWILIO_PHONE_NUMBER: str

    # ── URLs ──────────────────────────────────────────────────
    FRONTEND_URL: str
    BACKEND_URL:  str = "http://localhost:8000"
    UPLOAD_DIR:   str = "./uploads"

    # ── Admin initial ─────────────────────────────────────────
    ADMIN_EMAIL:    str
    ADMIN_PASSWORD: str

    class Config:
        env_file = str(ENV_FILE)
        extra = "ignore"

settings = Settings()
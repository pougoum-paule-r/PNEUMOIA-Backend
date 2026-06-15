from pydantic_settings import BaseSettings
from pathlib import Path

# Chemin absolu vers le .env — fonctionne peu importe d'où tu lances uvicorn
ENV_FILE = Path(__file__).parent.parent / ".env"

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

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

    # ── Admin initial (optionnel — seulement pour init_db) ───
    ADMIN_EMAIL:    str | None = None
    ADMIN_PASSWORD: str | None = None

    # ── Téléphone admin (fallback si non enregistré en BDD) ──
    ADMIN_PHONE: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
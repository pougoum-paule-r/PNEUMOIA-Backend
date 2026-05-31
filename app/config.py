from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ── Email SMTP (Brevo / SendGrid / Mailtrap) ──────────────
    SMTP_HOST:     str = "smtp-relay.brevo.com"   # Brevo par défaut
    SMTP_PORT:     int = 587
    SMTP_USER:     str                             # ton email de connexion Brevo
    SMTP_PASSWORD: str                             # clé SMTP générée par Brevo
    FROM_EMAIL:    str                             # adresse expéditeur vérifiée

    # ── SMS (Twilio) ──────────────────────────────────────────
    TWILIO_ACCOUNT_SID:  str
    TWILIO_AUTH_TOKEN:   str
    TWILIO_PHONE_NUMBER: str
    ADMIN_PHONE:         str

    # ── URLs ──────────────────────────────────────────────────
    FRONTEND_URL: str
    BACKEND_URL:  str = "http://localhost:8000"
    UPLOAD_DIR:   str = "./uploads"

    class Config:
        env_file = ".env"

settings = Settings()

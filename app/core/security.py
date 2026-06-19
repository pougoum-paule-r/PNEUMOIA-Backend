import secrets, random, string, bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db

bearer = HTTPBearer()


# ── Mots de passe ─────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ── JWT ───────────────────────────────────────────────────────────
def create_access_token(data: dict, expires_minutes: int = None) -> str:
    payload = data.copy()
    expire  = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload["exp"] = expire
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


# ── Dépendance FastAPI — médecin connecté ─────────────────────────
async def get_current_medecin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
):
    """
    Injecté via Depends() dans tous les routers protégés.
    Vérifie le JWT et retourne l'objet Medecin depuis la BDD.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(credentials.credentials)
        medecin_id: str = payload.get("sub")
        if not medecin_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Import ici pour éviter les imports circulaires
    from app.models.medecin import Medecin
    medecin = await db.get(Medecin, medecin_id)

    if not medecin:
        raise HTTPException(status_code=404, detail="Médecin introuvable")

    if medecin.statut != "valide":
        raise HTTPException(
            status_code=403,
            detail=f"Compte non autorisé (statut : {medecin.statut})"
        )

    return medecin


# ── Dépendance FastAPI — admin connecté ──────────────────────────
async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(credentials.credentials)
        admin_id: str = payload.get("sub")
        role: str = payload.get("role", "")
        if not admin_id or role != "admin":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    from app.models.admin import Admin
    admin = await db.get(Admin, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin introuvable")

    return admin


# ── Tokens divers ─────────────────────────────────────────────────
def generate_activation_token() -> str:
    return secrets.token_urlsafe(32)

def generate_otp() -> str:
    return ''.join(random.choices(string.digits, k=6))
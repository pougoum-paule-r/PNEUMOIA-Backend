from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError

from app.database import get_db
from app.core.security import decode_token
from app.models.medecin import Medecin
from app.models.admin import Admin

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_medecin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Medecin:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not credentials:
        raise exc
    try:
        payload  = decode_token(credentials.credentials)
        medecin_id: str = payload.get("sub")
        role: str       = payload.get("role")
        if medecin_id is None or role != "medecin":
            raise exc
    except JWTError:
        raise exc

    result  = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
    medecin = result.scalar_one_or_none()
    if medecin is None:
        raise exc
    return medecin


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Admin:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not credentials:
        raise exc
    try:
        payload  = decode_token(credentials.credentials)
        admin_id: str = payload.get("sub")
        role: str     = payload.get("role")
        if admin_id is None or role != "admin":
            raise exc
    except JWTError:
        raise exc

    result = await db.execute(select(Admin).where(Admin.id == admin_id))
    admin  = result.scalar_one_or_none()
    if admin is None:
        raise exc
    return admin

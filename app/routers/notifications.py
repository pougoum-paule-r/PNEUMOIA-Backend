# app/routers/notifications.py
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from pydantic import BaseModel

from app.database import get_db
from app.models.notification import Notification
from app.core.security import decode_token, get_current_medecin
from jose import JWTError

router = APIRouter(prefix="/notifications", tags=["Notifications"])
bearer = HTTPBearer()

# ── Helpers ────────────────────────────────────────────────────────
async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
):
    """Retourne (user_id, type_dest) depuis le JWT — supporte medecin et aide_soignant."""
    try:
        payload = decode_token(credentials.credentials)
        role    = payload.get("role", "")
        uid     = payload.get("sub")
        if not uid:
            raise HTTPException(401, "Token invalide")
        if role == "medecin":
            return uid, "medecin"
        elif role == "aide_soignant":
            return uid, "aide_soignant"
        elif role == "admin":
            return uid, "admin"
        raise HTTPException(403, "Rôle non supporté")
    except JWTError:
        raise HTTPException(401, "Token invalide")


# ── GET /notifications — lire mes notifications ───────────────────
@router.get("")
async def get_notifications(
    non_lues_seulement: bool = False,
    limite: int = 50,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
):
    uid, type_dest = await get_current_user_info(credentials)

    q = select(Notification).where(
        Notification.destinataire_id == uid,
        Notification.type_dest == type_dest,
    )
    if non_lues_seulement:
        q = q.where(Notification.lu == False)  # noqa: E712
    q = q.order_by(Notification.created_at.desc()).limit(limite)

    result = await db.execute(q)
    notifs = result.scalars().all()
    return [_serialize(n) for n in notifs]


# ── GET /notifications/count — nombre de non lues ─────────────────
@router.get("/count")
async def count_non_lues(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
):
    uid, type_dest = await get_current_user_info(credentials)
    r = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.destinataire_id == uid,
            Notification.type_dest == type_dest,
            Notification.lu == False,  # noqa: E712
        )
    )
    return {"count": r.scalar_one() or 0}


# ── PATCH /notifications/{id}/lire — marquer comme lue ───────────
@router.patch("/{notif_id}/lire")
async def marquer_lue(
    notif_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
):
    uid, type_dest = await get_current_user_info(credentials)
    notif = await db.get(Notification, notif_id)
    if not notif or notif.destinataire_id != uid:
        raise HTTPException(404, "Notification introuvable")
    notif.lu = True
    await db.commit()
    return {"message": "Marquée comme lue"}


# ── PATCH /notifications/tout-lire — tout marquer comme lu ───────
@router.patch("/tout-lire")
async def tout_marquer_lu(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
):
    uid, type_dest = await get_current_user_info(credentials)
    await db.execute(
        update(Notification)
        .where(Notification.destinataire_id == uid, Notification.type_dest == type_dest)
        .values(lu=True)
    )
    await db.commit()
    return {"message": "Toutes les notifications marquées comme lues"}


# ── DELETE /notifications/{id} — supprimer ────────────────────────
@router.delete("/{notif_id}")
async def supprimer_notification(
    notif_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
):
    uid, _ = await get_current_user_info(credentials)
    notif  = await db.get(Notification, notif_id)
    if not notif or notif.destinataire_id != uid:
        raise HTTPException(404, "Notification introuvable")
    await db.delete(notif)
    await db.commit()
    return {"message": "Notification supprimée"}


# ── DELETE /notifications — supprimer toutes les lues ────────────
@router.delete("")
async def supprimer_toutes_lues(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
):
    uid, type_dest = await get_current_user_info(credentials)
    result = await db.execute(
        select(Notification).where(
            Notification.destinataire_id == uid,
            Notification.type_dest == type_dest,
            Notification.lu == True,  # noqa: E712
        )
    )
    for n in result.scalars().all():
        await db.delete(n)
    await db.commit()
    return {"message": "Notifications lues supprimées"}


def _serialize(n: Notification) -> dict:
    return {
        "id":             n.id,
        "type_notif":     n.type_notif,
        "titre":          n.titre,
        "message":        n.message,
        "meta":           n.meta or {},
        "lu":             n.lu,
        "created_at":     n.created_at.isoformat(),
    }

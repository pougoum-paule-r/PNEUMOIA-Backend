# app/routers/questions_admin.py
"""
Questions posées par les médecins à l'administrateur.
Un médecin peut soumettre une question et consulter ses questions passées.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import Optional
from jose import JWTError

from app.database import get_db
from app.core.security import decode_token
from app.models.medecin import Medecin
from app.models.question_admin import QuestionAdmin

router = APIRouter(prefix="/questions-admin", tags=["Questions Admin"])
bearer = HTTPBearer()


async def _get_medecin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> Medecin:
    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        raise HTTPException(401, "Token invalide")
    if payload.get("role") != "medecin":
        raise HTTPException(403, "Réservé aux médecins")
    m = await db.get(Medecin, payload.get("sub"))
    if not m or m.statut != "valide":
        raise HTTPException(403, "Compte médecin non autorisé")
    return m


class QuestionCreate(BaseModel):
    titre:   str
    message: str


# ── GET /questions-admin/mes-questions ───────────────────────────
@router.get("/mes-questions")
async def mes_questions(
    medecin: Medecin     = Depends(_get_medecin),
    db:      AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(QuestionAdmin)
        .where(QuestionAdmin.medecin_id == medecin.id)
        .order_by(desc(QuestionAdmin.created_at))
    )
    questions = result.scalars().all()
    return [_serialize(q) for q in questions]


# ── POST /questions-admin ─────────────────────────────────────────
@router.post("", status_code=201)
async def poser_question(
    body:    QuestionCreate,
    medecin: Medecin       = Depends(_get_medecin),
    db:      AsyncSession  = Depends(get_db),
):
    if not body.titre.strip() or not body.message.strip():
        raise HTTPException(422, "Titre et message requis")

    q = QuestionAdmin(
        medecin_id = medecin.id,
        titre      = body.titre.strip(),
        message    = body.message.strip(),
    )
    db.add(q)
    await db.commit()
    await db.refresh(q)
    return _serialize(q)


# ── Sérialisation ─────────────────────────────────────────────────
def _serialize(q: QuestionAdmin) -> dict:
    return {
        "id":      q.id,
        "titre":   q.titre,
        "message": q.message,
        "statut":  q.statut,
        "reponse": q.reponse,
        "date":    q.created_at.strftime("%Y-%m-%d"),
    }

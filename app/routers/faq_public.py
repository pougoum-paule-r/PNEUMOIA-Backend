"""
faq_public.py — Endpoint public (sans authentification) pour la landing page.
Retourne les FAQ publiées par l'admin, accessible à tous sans token.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models.faqPubliee import FAQPubliee

router = APIRouter(prefix="/faq-public", tags=["FAQ Public"])


@router.get("")
async def get_faq_public(db: AsyncSession = Depends(get_db)):
    """
    Retourne toutes les FAQ publiées — pas d'authentification requise.
    Utilisé par la landing page /apropos.
    GET /api/v1/faq-public
    """
    result = await db.execute(
        select(FAQPubliee)
        .where(FAQPubliee.publie == True)
        .order_by(desc(FAQPubliee.created_at))
    )
    faqs = result.scalars().all()
    return [
        {
            "id":        f.id,
            "question":  f.question,
            "reponse":   f.reponse,
            "categorie": f.categorie,
        }
        for f in faqs
    ]

# app/routers/communautes.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.core.security import get_current_medecin
from app.models.communaute import Communaute

router_communautes = APIRouter(prefix="/api/v1/communautes", tags=["Communautés"])


@router_communautes.get("")
async def liste_communautes(
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    """Liste des communautés publiques disponibles pour le partage."""
    result = await db.execute(
        select(Communaute)
        .where(Communaute.type == "publique")
        .order_by(Communaute.nb_membres.desc())
        .limit(50)
    )
    return [
        {
            "id":          c.id,
            "nom":         c.nom,
            "description": c.description,
            "specialite":  c.specialite,
            "nb_membres":  c.nb_membres,
        }
        for c in result.scalars().all()
    ]

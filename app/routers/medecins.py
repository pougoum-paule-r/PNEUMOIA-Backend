# app/routers/medecins.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.core.security import get_current_medecin
from app.models.medecin import Medecin

router_medecins = APIRouter(prefix="/api/v1/medecins", tags=["Médecins"])


@router_medecins.get("/liste")
async def liste_medecins(
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    """Liste des médecins validés pour le partage inter-médecins (hors soi-même)."""
    result = await db.execute(
        select(Medecin)
        .where(
            Medecin.statut == "valide",
            Medecin.id != medecin.id,
        )
        .order_by(Medecin.nom)
        .limit(100)
    )
    return [
        {
            "id":         m.id,
            "nom":        m.nom,
            "prenom":     m.prenom,
            "specialite": m.specialite,
            "photo_url":  m.photo_url,
        }
        for m in result.scalars().all()
    ]

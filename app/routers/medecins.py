# app/routers/medecins.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case

from app.database import get_db
from app.core.security import get_current_medecin
from app.models.medecin import Medecin
from app.models.patient import Patient
from app.models.consultation import Consultation
from app.models.diagnostic_ia import DiagnosticIA
from app.models.feedback_ia import FeedbackIA

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


@router_medecins.get("/mon-rang")
async def mon_rang(
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    """Rang du médecin connecté basé sur nb patients + consultations terminées."""
    mid = medecin.id

    # Compter patients de ce médecin
    r = await db.execute(
        select(func.count(Patient.id))
        .where(Patient.created_by == mid, Patient.deleted_at.is_(None))
    )
    nb_patients = r.scalar_one() or 0

    # Compter toutes les consultations de ce médecin
    r = await db.execute(
        select(func.count(Consultation.id))
        .where(Consultation.medecin_id == mid)
    )
    nb_consultations = r.scalar_one() or 0

    # Cas partagés
    r = await db.execute(
        select(func.count(Consultation.id))
        .where(Consultation.medecin_id == mid)
        .where(Consultation.partage["actif"].astext == "true")
    )
    nb_partages = r.scalar_one() or 0

    # Concordance IA/médecin (taux)
    conc_float = case((FeedbackIA.concordance == True, 1.0), else_=0.0)  # noqa: E712
    r = await db.execute(
        select(func.avg(conc_float))
        .join(DiagnosticIA, FeedbackIA.diagnostic_id == DiagnosticIA.id)
        .join(Consultation, DiagnosticIA.consultation_id == Consultation.id)
        .where(Consultation.medecin_id == mid)
        .where(FeedbackIA.concordance.isnot(None))
    )
    raw_conc = r.scalar_one()
    concordance = round(float(raw_conc) * 100, 1) if raw_conc is not None else 0.0

    # Score = patients*2 + consultations*3 + partagés*1
    mon_score = nb_patients * 2 + nb_consultations * 3 + nb_partages

    # Calculer le score de tous les médecins validés
    r_all = await db.execute(
        select(Medecin.id)
        .where(Medecin.statut == "valide")
    )
    all_ids = [row[0] for row in r_all.fetchall()]
    total = len(all_ids)

    scores = {}
    for mid_other in all_ids:
        rp = await db.execute(
            select(func.count(Patient.id))
            .where(Patient.created_by == mid_other, Patient.deleted_at.is_(None))
        )
        rp2 = await db.execute(
            select(func.count(Consultation.id))
            .where(Consultation.medecin_id == mid_other, Consultation.statut == "terminee")
        )
        rp3 = await db.execute(
            select(func.count(Consultation.id))
            .where(Consultation.medecin_id == mid_other)
            .where(Consultation.partage["actif"].astext == "true")
        )
        scores[mid_other] = (rp.scalar_one() or 0) * 2 + (rp2.scalar_one() or 0) * 3 + (rp3.scalar_one() or 0)

    position = sum(1 for s in scores.values() if s > mon_score) + 1

    return {
        "position":       position,
        "total":          max(total, 1),
        "score_ia":       concordance,
        "nb_patients":    nb_patients,
        "nb_consultations": nb_consultations,
        "nb_partages":    nb_partages,
    }

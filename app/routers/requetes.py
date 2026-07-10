"""
Requêtes médecins — signalements de bugs et demandes d'assistance.

Routes médecin (prefix /api/v1/requetes) :
  POST  /              → soumettre une requête
  GET   /mes-requetes  → liste propre au médecin connecté
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.core.security import get_current_medecin
from app.models.requete_medecin import RequeteMedecin
from app.models.medecin import Medecin
from app.models.admin import Admin
from app.models.notification import Notification

router = APIRouter(prefix="/requetes", tags=["Requêtes Médecins"])

CATEGORIES_VALIDES = {"bug_technique", "probleme_acces", "erreur_ia", "lenteur", "interface", "autre"}


@router.post("")
async def soumettre_requete(
    body:    dict,
    medecin: Medecin      = Depends(get_current_medecin),
    db:      AsyncSession = Depends(get_db),
):
    titre       = (body.get("titre") or "").strip()
    description = (body.get("description") or "").strip()
    categorie   = body.get("categorie", "autre")

    if not titre:
        raise HTTPException(400, "Le titre est obligatoire.")
    if not description:
        raise HTTPException(400, "La description est obligatoire.")
    if categorie not in CATEGORIES_VALIDES:
        categorie = "autre"

    req = RequeteMedecin(
        medecin_id    = medecin.id,
        nom_medecin   = f"{medecin.civilite or 'Dr.'} {medecin.prenom} {medecin.nom}",
        email_medecin = medecin.email,
        titre         = titre[:300],
        categorie     = categorie,
        description   = description,
    )
    db.add(req)
    await db.flush()

    admins = (await db.execute(select(Admin))).scalars().all()
    for adm in admins:
        db.add(Notification(
            destinataire_id = adm.id,
            type_dest       = "admin",
            type_notif      = "nouvelle_requete_medecin",
            titre           = f"Nouvelle requête — {titre[:80]}",
            message         = (
                f"Dr. {medecin.prenom} {medecin.nom} a soumis une requête : {titre}"
            ),
            meta = {
                "lien":       "/administrateur/requetes",
                "requete_id": req.id,
                "medecin_id": medecin.id,
            },
        ))

    await db.commit()
    return {"id": req.id, "message": "Requête soumise avec succès."}


@router.get("/mes-requetes")
async def mes_requetes(
    medecin: Medecin      = Depends(get_current_medecin),
    db:      AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RequeteMedecin)
        .where(RequeteMedecin.medecin_id == medecin.id)
        .order_by(desc(RequeteMedecin.created_at))
    )
    rows = result.scalars().all()
    return [
        {
            "id":            r.id,
            "titre":         r.titre,
            "categorie":     r.categorie,
            "description":   r.description,
            "statut":        r.statut,
            "action_admin":  r.action_admin,
            "reponse_admin": r.reponse_admin,
            "repondu_le":    r.repondu_le.isoformat() if r.repondu_le else None,
            "created_at":    r.created_at.isoformat(),
        }
        for r in rows
    ]

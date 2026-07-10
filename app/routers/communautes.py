# app/routers/communautes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime

from app.database import get_db
from app.core.security import get_current_medecin
from app.models.communaute import Communaute
from app.models.membre_communaute import MembreCommunaute
from app.models.cas_clinique_public import CasCliniquPublic
from app.models.notification import Notification

router_communautes = APIRouter(prefix="/api/v1/communautes", tags=["Communautés"])


# ── Helpers ──────────────────────────────────────────────────────────
async def _mon_statut(db, communaute_id: str, medecin_id: str) -> str | None:
    """Retourne le statut du médecin dans une communauté (None si absent)."""
    r = await db.execute(
        select(MembreCommunaute).where(
            MembreCommunaute.communaute_id == communaute_id,
            MembreCommunaute.medecin_id    == medecin_id,
        ).limit(1)
    )
    m = r.scalar_one_or_none()
    return m.statut if m else None


async def _creer_notif(db, destinataire_id: str, type_notif: str,
                       titre: str, message: str, meta: dict):
    notif = Notification(
        destinataire_id = destinataire_id,
        type_dest       = "medecin",
        type_notif      = type_notif,
        titre           = titre,
        message         = message,
        meta            = meta,
    )
    db.add(notif)


@router_communautes.get("")
async def liste_communautes(
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    """Liste toutes les communautés avec le statut du médecin connecté."""
    from app.models.medecin import Medecin

    result = await db.execute(
        select(Communaute)
        .order_by(Communaute.nb_membres.desc())
        .limit(100)
    )
    communautes = result.scalars().all()
    data = []
    for c in communautes:
        createur = await db.get(Medecin, c.createur_id)
        mon_statut = await _mon_statut(db, c.id, medecin.id)
        est_createur = c.createur_id == medecin.id

        # Demandes en attente (visible seulement pour le créateur)
        nb_attente = 0
        if est_createur:
            r2 = await db.execute(
                select(func.count()).select_from(MembreCommunaute).where(
                    MembreCommunaute.communaute_id == c.id,
                    MembreCommunaute.statut        == "en_attente",
                )
            )
            nb_attente = r2.scalar() or 0

        data.append({
            "id":           c.id,
            "nom":          c.nom,
            "description":  c.description,
            "specialite":   c.specialite,
            "type":         c.type,
            "nb_membres":   c.nb_membres,
            "created_at":   c.created_at.isoformat() if c.created_at else None,
            "createur":     f"Dr. {createur.prenom} {createur.nom}" if createur else None,
            "est_createur": est_createur,
            "mon_statut":   mon_statut,   # None | 'en_attente' | 'accepte' | 'refuse'
            "nb_attente":   nb_attente,
        })
    return data


# ── POST /communautes/:id/rejoindre — Demander l'accès ────────────
@router_communautes.post("/{communaute_id}/rejoindre", status_code=201)
async def rejoindre_communaute(
    communaute_id: str,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    from app.models.medecin import Medecin

    communaute = await db.get(Communaute, communaute_id)
    if not communaute:
        raise HTTPException(404, "Communauté introuvable")
    if communaute.createur_id == medecin.id:
        raise HTTPException(400, "Vous êtes le créateur de ce groupe")

    existing = await db.execute(
        select(MembreCommunaute).where(
            MembreCommunaute.communaute_id == communaute_id,
            MembreCommunaute.medecin_id    == medecin.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(409, "Vous avez déjà une demande en cours ou êtes déjà membre")

    # Pour les communautés publiques : accès direct ; privées : en_attente
    statut_initial = "accepte" if communaute.type == "publique" else "en_attente"

    membre = MembreCommunaute(
        communaute_id = communaute_id,
        medecin_id    = medecin.id,
        role          = "membre",
        statut        = statut_initial,
    )
    db.add(membre)

    if statut_initial == "accepte":
        # Mettre à jour le compteur
        communaute.nb_membres += 1
    else:
        # Notifier le créateur d'une nouvelle demande
        demandeur = await db.get(Medecin, medecin.id)
        await _creer_notif(
            db,
            destinataire_id = communaute.createur_id,
            type_notif      = "demande_groupe",
            titre           = "Nouvelle demande d'adhésion",
            message         = f"Dr. {demandeur.prenom} {demandeur.nom} souhaite rejoindre « {communaute.nom} »",
            meta            = {"communaute_id": communaute_id, "medecin_id": medecin.id},
        )

    await db.commit()
    return {"statut": statut_initial, "message": "ok"}


# ── POST /communautes/:id/membres/:medecin_id/accepter ────────────
@router_communautes.post("/{communaute_id}/membres/{demandeur_id}/accepter")
async def accepter_membre(
    communaute_id: str,
    demandeur_id:  str,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    communaute = await db.get(Communaute, communaute_id)
    if not communaute:
        raise HTTPException(404, "Communauté introuvable")
    if communaute.createur_id != medecin.id:
        raise HTTPException(403, "Seul le créateur peut gérer les membres")

    r = await db.execute(
        select(MembreCommunaute).where(
            MembreCommunaute.communaute_id == communaute_id,
            MembreCommunaute.medecin_id    == demandeur_id,
        )
    )
    membre = r.scalar_one_or_none()
    if not membre:
        raise HTTPException(404, "Demande introuvable")

    membre.statut = "accepte"
    communaute.nb_membres += 1

    # Notifier le demandeur
    from app.models.medecin import Medecin
    await _creer_notif(
        db,
        destinataire_id = demandeur_id,
        type_notif      = "groupe_accepte",
        titre           = "Accès accordé",
        message         = f"Votre demande pour rejoindre « {communaute.nom} » a été acceptée",
        meta            = {"communaute_id": communaute_id, "communaute_nom": communaute.nom,
                           "lien": "/medecin/messagerie"},
    )
    await db.commit()
    return {"message": "Membre accepté"}


# ── POST /communautes/:id/membres/:medecin_id/refuser ─────────────
@router_communautes.post("/{communaute_id}/membres/{demandeur_id}/refuser")
async def refuser_membre(
    communaute_id: str,
    demandeur_id:  str,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    communaute = await db.get(Communaute, communaute_id)
    if not communaute:
        raise HTTPException(404, "Communauté introuvable")
    if communaute.createur_id != medecin.id:
        raise HTTPException(403, "Seul le créateur peut gérer les membres")

    r = await db.execute(
        select(MembreCommunaute).where(
            MembreCommunaute.communaute_id == communaute_id,
            MembreCommunaute.medecin_id    == demandeur_id,
        )
    )
    membre = r.scalar_one_or_none()
    if not membre:
        raise HTTPException(404, "Demande introuvable")

    membre.statut = "refuse"
    await db.commit()
    return {"message": "Demande refusée"}


# ── GET /communautes/:id/membres — Liste membres / demandes ───────
@router_communautes.get("/{communaute_id}/membres")
async def liste_membres(
    communaute_id: str,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    from app.models.medecin import Medecin

    communaute = await db.get(Communaute, communaute_id)
    if not communaute:
        raise HTTPException(404, "Communauté introuvable")
    if communaute.createur_id != medecin.id:
        raise HTTPException(403, "Réservé au créateur")

    r = await db.execute(
        select(MembreCommunaute).where(
            MembreCommunaute.communaute_id == communaute_id,
        ).order_by(MembreCommunaute.joined_at.asc())
    )
    membres = r.scalars().all()
    data = []
    for m in membres:
        med = await db.get(Medecin, m.medecin_id)
        if med:
            data.append({
                "medecin_id": med.id,
                "nom":        med.nom,
                "prenom":     med.prenom,
                "specialite": getattr(med, "specialite", None),
                "statut":     m.statut,
                "joined_at":  m.joined_at.isoformat() if m.joined_at else None,
            })
    return data


# ── GET /communautes/cas-cliniques — Cas cliniques publics ───────
@router_communautes.get("/cas-cliniques")
async def liste_cas_cliniques(
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    from app.models.medecin import Medecin

    result = await db.execute(
        select(CasCliniquPublic)
        .order_by(CasCliniquPublic.created_at.desc())
        .limit(50)
    )
    cas = result.scalars().all()

    data = []
    for c in cas:
        auteur = None
        if c.auteur_id and not c.anonymise:
            auteur = await db.get(Medecin, c.auteur_id)

        data.append({
            "id":          c.id,
            "titre":       c.titre,
            "diagnostic":  c.pathologie,
            "description": c.description,
            "tags":        c.tags or [],
            "anonymise":   c.anonymise,
            "nb_vues":     c.nb_vues,
            "pdf_url":     c.pdf_url,
            "created_at":  c.created_at.isoformat() if c.created_at else None,
            "likes":       0,
            "liked":       False,
            "auteur": f"Dr. {auteur.prenom} {auteur.nom}" if auteur else "Médecin anonyme",
        })
    return data


# ── POST /communautes/cas-cliniques/:id/like — Liker un cas ──────
@router_communautes.post("/cas-cliniques/{cas_id}/like")
async def liker_cas_clinique(
    cas_id: str,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    cas = await db.get(CasCliniquPublic, cas_id)
    if not cas:
        raise HTTPException(404, "Cas clinique introuvable")
    # Le compteur de likes est géré côté frontend (toggle optimiste)
    return {"message": "ok", "cas_id": cas_id}

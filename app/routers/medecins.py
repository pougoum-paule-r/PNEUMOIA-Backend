# app/routers/medecins.py
from datetime import datetime, timezone
import calendar as _calendar
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.core.security import get_current_medecin
from app.config import settings
from app.models.medecin import Medecin
from app.models.patient import Patient
from app.models.consultation import Consultation
from app.models.diagnostic_ia import DiagnosticIA
from app.models.feedback_ia import FeedbackIA
from app.models.avis import Avis

router_medecins = APIRouter(prefix="/api/v1/medecins", tags=["Médecins"])

_PREFS_MEDECIN_DEFAULTS = {
    "emailNotifications":       True,
    "smsNotifications":         False,
    "newsletter":               True,
    "rappelsConsultations":     True,
    "rappelsSuivi":             True,
    "notifNouvellesConsultations": True,
    "notifMessagesRecus":       True,
    "notifCommentairesCas":     True,
    "notifPartagesRecus":       True,
    "notifRappelsSysteme":      True,
    "notifMisesAJour":          True,
    "notifEvenements":          False,
    "langue":                   "fr",
    "timezone":                 "Africa/Douala",
    "compactView":              False,
    "showThumbnails":           True,
    "defaultView":              "cards",
    "itemsPerPage":             10,
    "sortBy":                   "date",
    "sortOrder":                "desc",
    "profilPublic":             True,
    "visibleDansAnnuaire":      True,
    "anonymisationCas":         True,
    "accepteDemandes":          True,
}

class AvisIn(BaseModel):
    note: int
    commentaire: str
    ville: Optional[str] = None


class PreferencesMedecinRequest(BaseModel):
    emailNotifications:           Optional[bool] = None
    smsNotifications:             Optional[bool] = None
    newsletter:                   Optional[bool] = None
    rappelsConsultations:         Optional[bool] = None
    rappelsSuivi:                 Optional[bool] = None
    notifNouvellesConsultations:  Optional[bool] = None
    notifMessagesRecus:           Optional[bool] = None
    notifCommentairesCas:         Optional[bool] = None
    notifPartagesRecus:           Optional[bool] = None
    notifRappelsSysteme:          Optional[bool] = None
    notifMisesAJour:              Optional[bool] = None
    notifEvenements:              Optional[bool] = None
    langue:                       Optional[str]  = None
    timezone:                     Optional[str]  = None
    compactView:                  Optional[bool] = None
    showThumbnails:               Optional[bool] = None
    defaultView:                  Optional[str]  = None
    itemsPerPage:                 Optional[int]  = None
    sortBy:                       Optional[str]  = None
    sortOrder:                    Optional[str]  = None
    profilPublic:                 Optional[bool] = None
    visibleDansAnnuaire:          Optional[bool] = None
    anonymisationCas:             Optional[bool] = None
    accepteDemandes:              Optional[bool] = None


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
    """Rang du médecin connecté — même formule que le classement admin (avg pct IA du mois courant)."""
    mid = medecin.id
    now   = datetime.now(timezone.utc).replace(tzinfo=None)
    debut = datetime(now.year, now.month, 1)
    fin   = datetime(now.year, now.month, _calendar.monthrange(now.year, now.month)[1], 23, 59, 59)

    # ── Infos générales de ce médecin ──────────────────────────────────
    r = await db.execute(
        select(func.count(Patient.id))
        .where(Patient.created_by == mid, Patient.deleted_at.is_(None))
    )
    nb_patients = r.scalar_one() or 0

    r = await db.execute(
        select(func.count(Consultation.id)).where(Consultation.medecin_id == mid)
    )
    nb_consultations = r.scalar_one() or 0

    r = await db.execute(
        select(func.count(Consultation.id))
        .where(Consultation.medecin_id == mid)
        .where(Consultation.partage["actif"].astext == "true")
    )
    nb_partages = r.scalar_one() or 0

    # ── Concordance IA (taux feedback) — pour le Score IA affiché ──────
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

    # ── Classement : même formule que admin (avg pct IA du mois) ───────
    result = await db.execute(
        select(Medecin)
        .where(Medecin.statut == "valide")
        .options(selectinload(Medecin.consultations).selectinload(Consultation.diagnostic))
    )
    all_medecins = result.scalars().all()
    total = len(all_medecins)

    scores_mois: dict[str, float] = {}
    for md in all_medecins:
        cons_mois = [
            c for c in (md.consultations or [])
            if c.created_at and debut <= c.created_at <= fin
        ]
        pcts = []
        for c in cons_mois:
            if c.diagnostic and isinstance(c.diagnostic.maladies, list) and c.diagnostic.maladies:
                pct = c.diagnostic.maladies[0].get("pct")
                if pct is not None:
                    pcts.append(float(pct))
        if pcts:
            scores_mois[md.id] = sum(pcts) / len(pcts)

    mon_score_mois = scores_mois.get(mid, 0.0)
    position = sum(1 for s in scores_mois.values() if s > mon_score_mois) + 1

    return {
        "position":         position,
        "total":            max(total, 1),
        "score_ia":         concordance,
        "nb_patients":      nb_patients,
        "nb_consultations": nb_consultations,
        "nb_partages":      nb_partages,
    }


@router_medecins.get("/me/preferences")
async def get_preferences_medecin(
    db: AsyncSession = Depends(get_db),
    medecin: Medecin = Depends(get_current_medecin),
):
    stored = medecin.preferences or {}
    return {**_PREFS_MEDECIN_DEFAULTS, **stored}


@router_medecins.patch("/me/preferences")
async def update_preferences_medecin(
    body: PreferencesMedecinRequest,
    db: AsyncSession = Depends(get_db),
    medecin: Medecin = Depends(get_current_medecin),
):
    current = dict(medecin.preferences or {})
    current.update(body.model_dump(exclude_none=True))
    medecin.preferences = current
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(medecin, "preferences")
    await db.commit()
    return {**_PREFS_MEDECIN_DEFAULTS, **current}


@router_medecins.get("/public/stats", tags=["Public"])
async def public_stats(db: AsyncSession = Depends(get_db)):
    """Statistiques publiques de la plateforme."""
    r_med = await db.execute(select(func.count(Medecin.id)).where(Medecin.statut == "valide"))
    nb_medecins = r_med.scalar_one() or 0

    r_cons = await db.execute(select(func.count(Consultation.id)))
    nb_consultations = r_cons.scalar_one() or 0

    conc_float = case((FeedbackIA.concordance == True, 1.0), else_=0.0)  # noqa: E712
    r_conc = await db.execute(select(func.avg(conc_float)).where(FeedbackIA.concordance.isnot(None)))
    raw_c = r_conc.scalar_one()
    concordance = round(float(raw_c) * 100, 1) if raw_c is not None else 0.0

    return {
        "nb_medecins":      nb_medecins,
        "nb_consultations": nb_consultations,
        "precision_ia":     concordance,
    }


def _photo_url(raw: str | None) -> str | None:
    if not raw:
        return None
    if raw.startswith("http"):
        return raw
    if raw.startswith("/"):
        return f"{settings.BACKEND_URL}{raw}"
    return f"{settings.BACKEND_URL}/{raw.replace(chr(92), '/').lstrip('./')}"


@router_medecins.get("/public/top4", tags=["Public"])
async def top4_medecins(db: AsyncSession = Depends(get_db)):
    """Top 4 médecins validés par score (patients×2 + consultations×3 + cas partagés) — public."""
    r = await db.execute(
        select(Medecin).where(Medecin.statut == "valide")
    )
    medecins = r.scalars().all()

    scores = []
    for m in medecins:
        rp = await db.execute(select(func.count(Patient.id)).where(Patient.created_by == m.id, Patient.deleted_at.is_(None)))
        rc = await db.execute(select(func.count(Consultation.id)).where(Consultation.medecin_id == m.id, Consultation.statut == "terminee"))
        rs = await db.execute(select(func.count(Consultation.id)).where(Consultation.medecin_id == m.id, Consultation.partage["actif"].astext == "true"))
        score = (rp.scalar_one() or 0) * 2 + (rc.scalar_one() or 0) * 3 + (rs.scalar_one() or 0)

        # Concordance IA
        conc_float = case((FeedbackIA.concordance == True, 1.0), else_=0.0)  # noqa: E712
        rf = await db.execute(
            select(func.avg(conc_float))
            .join(DiagnosticIA, FeedbackIA.diagnostic_id == DiagnosticIA.id)
            .join(Consultation, DiagnosticIA.consultation_id == Consultation.id)
            .where(Consultation.medecin_id == m.id)
            .where(FeedbackIA.concordance.isnot(None))
        )
        raw_c = rf.scalar_one()
        concordance = round(float(raw_c) * 100, 1) if raw_c is not None else 0.0

        scores.append({
            "id":         m.id,
            "nom":        m.nom,
            "prenom":     m.prenom,
            "specialite": m.specialite or "Pneumologue",
            "hopital":    m.etablissement or "",
            "photo_url":  _photo_url(m.photo_url),
            "concordance": concordance,
            "score":      score,
        })

    scores.sort(key=lambda x: x["score"], reverse=True)
    return scores[:4]


# ── GET /mes-avis — liste de tous mes témoignages ─────────────────
@router_medecins.get("/mes-avis", tags=["Médecins"])
async def get_mes_avis(
    medecin: Medecin      = Depends(get_current_medecin),
    db:      AsyncSession = Depends(get_db),
):
    """Retourne tous les témoignages soumis par le médecin connecté."""
    r = await db.execute(
        select(Avis)
        .where(Avis.medecin_id == medecin.id)
        .order_by(Avis.created_at.desc())
    )
    avis_list = r.scalars().all()
    return [
        {
            "id":          a.id,
            "note":        a.note,
            "commentaire": a.commentaire,
            "ville":       a.ville or "",
            "statut":      "publie",
            "date":        a.created_at.strftime("%Y-%m-%d"),
        }
        for a in avis_list
    ]


# ── POST /mon-avis — créer un nouveau témoignage ──────────────────
@router_medecins.post("/mon-avis", tags=["Médecins"])
async def creer_avis(
    body:    AvisIn,
    medecin: Medecin      = Depends(get_current_medecin),
    db:      AsyncSession = Depends(get_db),
):
    """Crée un nouveau témoignage (un médecin peut en soumettre plusieurs)."""
    if not 1 <= body.note <= 5:
        raise HTTPException(422, "Note doit être entre 1 et 5")
    if not body.commentaire.strip():
        raise HTTPException(422, "Commentaire requis")

    nouveau = Avis(
        medecin_id    = medecin.id,
        prenom        = medecin.prenom,
        nom           = medecin.nom,
        civilite      = getattr(medecin, "civilite", None),
        specialite    = medecin.specialite or "Pneumologue",
        etablissement = medecin.etablissement or "",
        ville         = (body.ville or "").strip(),
        photo_url     = _photo_url(medecin.photo_url),
        note          = body.note,
        commentaire   = body.commentaire.strip(),
        statut        = "publie",
    )
    db.add(nouveau)
    await db.commit()
    await db.refresh(nouveau)
    return {
        "id":          nouveau.id,
        "note":        nouveau.note,
        "commentaire": nouveau.commentaire,
        "ville":       nouveau.ville or "",
        "statut":      "publie",
        "date":        nouveau.created_at.strftime("%Y-%m-%d"),
    }


@router_medecins.get("/public/temoignages", tags=["Public"])
async def public_temoignages(db: AsyncSession = Depends(get_db)):
    """Retourne les témoignages soumis par les médecins (table Avis uniquement)."""
    r = await db.execute(
        select(Avis, Medecin)
        .join(Medecin, Avis.medecin_id == Medecin.id)
        .where(Medecin.statut == "valide", Avis.statut == "publie")
        .order_by(Avis.created_at.desc())
        .limit(6)
    )
    rows = r.all()

    seen = set()
    results = []
    for avis, medecin in rows:
        if medecin.id not in seen:
            seen.add(medecin.id)
            results.append({
                "nom":        medecin.nom,
                "prenom":     medecin.prenom,
                "specialite": medecin.specialite or "Pneumologue",
                "hopital":    medecin.etablissement or "",
                "photo_url":  _photo_url(medecin.photo_url),
                "texte":      avis.commentaire,
                "note":       avis.note,
                "ville":      avis.ville or "",
                "date":       avis.created_at.strftime("%d.%m.%Y"),
            })

    return results


@router_medecins.get("/public/repartition", tags=["Public"])
async def repartition_pathologies(db: AsyncSession = Depends(get_db)):
    """Répartition publique des diagnostics principaux par pathologie."""
    from sqlalchemy import text as sa_text
    r = await db.execute(
        sa_text("""
            SELECT
                (maladies->0->>'nom') AS nom,
                COUNT(*)::int         AS total
            FROM diagnostics_ia
            WHERE maladies IS NOT NULL
              AND jsonb_array_length(maladies) > 0
            GROUP BY nom
            ORDER BY total DESC
            LIMIT 10
        """)
    )
    rows = r.fetchall()
    grand_total = sum(row.total for row in rows) or 1
    colors = [
        "bg-blue-500", "bg-indigo-500", "bg-purple-500",
        "bg-pink-500",  "bg-orange-500", "bg-red-500",
        "bg-teal-500",  "bg-cyan-500",   "bg-amber-500", "bg-emerald-500",
    ]
    return [
        {
            "name":       row.nom or "Inconnu",
            "count":      row.total,
            "percentage": round(row.total / grand_total * 100, 1),
            "color":      colors[i % len(colors)],
        }
        for i, row in enumerate(rows)
    ]

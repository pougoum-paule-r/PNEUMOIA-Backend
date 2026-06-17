# app/routers/medecins.py
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
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


class AvisRequest(BaseModel):
    note:   int
    contenu: str


@router_medecins.get("/avis/mon-avis")
async def get_mon_avis(
    db:      AsyncSession = Depends(get_db),
    medecin: Medecin      = Depends(get_current_medecin),
):
    """Retourne l'avis de la plateforme soumis par le médecin connecté, ou null."""
    from app.models.avis import Avis
    r = await db.execute(select(Avis).where(Avis.medecin_id == medecin.id))
    a = r.scalar_one_or_none()
    if not a:
        return None
    return {
        "id":         a.id,
        "note":       a.note,
        "contenu":    a.contenu,
        "vu":         a.vu,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


@router_medecins.post("/avis")
async def publier_mon_avis(
    body:    AvisRequest,
    db:      AsyncSession = Depends(get_db),
    medecin: Medecin      = Depends(get_current_medecin),
):
    """Crée ou met à jour le témoignage du médecin connecté sur la plateforme."""
    from app.models.avis import Avis
    from datetime import datetime

    if not (1 <= body.note <= 5):
        from fastapi import HTTPException
        raise HTTPException(422, "La note doit être comprise entre 1 et 5.")
    if not body.contenu.strip():
        from fastapi import HTTPException
        raise HTTPException(422, "Le contenu du témoignage est requis.")

    r = await db.execute(select(Avis).where(Avis.medecin_id == medecin.id))
    a = r.scalar_one_or_none()

    if a:
        a.note    = body.note
        a.contenu = body.contenu.strip()
        a.vu      = False
    else:
        a = Avis(
            medecin_id = medecin.id,
            note       = body.note,
            contenu    = body.contenu.strip(),
            vu         = False,
            created_at = datetime.utcnow(),
        )
        db.add(a)

    await db.commit()
    await db.refresh(a)
    return {
        "id":         a.id,
        "note":       a.note,
        "contenu":    a.contenu,
        "vu":         a.vu,
        "created_at": a.created_at.isoformat() if a.created_at else None,
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
        .where(Medecin.statut == "valide")
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

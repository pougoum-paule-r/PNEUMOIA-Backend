# app/routers/consultations.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.core.security import get_current_medecin
from app.models.consultation import Consultation
from app.models.patient import Patient
from app.models.acces_patient import AccesPatient
from app.models.diagnostic_ia import DiagnosticIA
from app.schemas.consultation import (
    ConsultationCreate, ConsultationOut,
    AntecedentsIn, SymptomesIn, OpinionIn,
)
from pydantic import BaseModel
from typing import Literal

class StatutCliniqueIn(BaseModel):
    statut_clinique: Literal["stable", "surveille", "urgent", "critique"]

router = APIRouter(prefix="/api/v1/consultations", tags=["Consultations"])


# ── Helpers ──────────────────────────────────────────────────────

async def verifier_acces_patient(patient_id: str, medecin_id: str, db: AsyncSession) -> Patient:
    from app.models.aide_soignant import AideSoignant

    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient introuvable")
    if patient.created_by == medecin_id:
        return patient

    # Patient créé par un aide soignant qui appartient à ce médecin
    aide_id = patient.aide_id or patient.created_by_aide
    if aide_id:
        aide = await db.get(AideSoignant, aide_id)
        if aide and aide.medecin_id == medecin_id:
            return patient

    acces = await db.execute(
        select(AccesPatient).where(
            AccesPatient.patient_id           == patient_id,
            AccesPatient.medecin_demandeur_id == medecin_id,
            AccesPatient.statut              == "accorde",
        )
    )
    if not acces.scalar_one_or_none():
        raise HTTPException(403, "Accès refusé — demandez l'accès au médecin propriétaire")
    return patient


async def get_ma_consultation(consultation_id: str, medecin_id: str, db: AsyncSession) -> Consultation:
    c = await db.get(Consultation, consultation_id)
    if not c:
        raise HTTPException(404, "Consultation introuvable")
    if c.medecin_id != medecin_id:
        raise HTTPException(403, "Accès refusé")
    return c


# ── POST /consultations — Ouvrir une consultation ────────────────
@router.post("", response_model=ConsultationOut, status_code=201)
async def creer_consultation(
    payload: ConsultationCreate,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    await verifier_acces_patient(payload.patient_id, medecin.id, db)

    c = Consultation(
        patient_id    = payload.patient_id,
        medecin_id    = medecin.id,
        symptomes     = {},
        prescriptions = {},
        partage       = {},
        statut        = "en_attente",
    )
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return c


# ── GET /consultations/search?q=terme — Recherche consultations ─
@router.get("/search")
async def rechercher_consultations(
    q: str,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    from sqlalchemy.orm import selectinload
    from sqlalchemy import or_, cast, String
    from app.models.diagnostic_ia import DiagnosticIA

    terme = f"%{q.strip()}%"
    result = await db.execute(
        select(Consultation)
        .join(Patient, Consultation.patient_id == Patient.id)
        .outerjoin(DiagnosticIA, DiagnosticIA.consultation_id == Consultation.id)
        .where(Consultation.medecin_id == medecin.id)
        .where(
            or_(
                Patient.nom.ilike(terme),
                Patient.prenom.ilike(terme),
                cast(DiagnosticIA.maladies, String).ilike(terme),
            )
        )
        .options(
            selectinload(Consultation.patient),
            selectinload(Consultation.diagnostic),
        )
        .order_by(Consultation.created_at.desc())
        .limit(30)
    )
    consultations = result.scalars().unique().all()

    from datetime import date as _date
    data = []
    for c in consultations:
        pat = c.patient
        diag = c.diagnostic
        age = None
        if pat and pat.date_naissance:
            today = _date.today()
            age = today.year - pat.date_naissance.year - (
                (today.month, today.day) < (pat.date_naissance.month, pat.date_naissance.day)
            )
        principale = (diag.maladies or [])[0] if diag and diag.maladies else None
        data.append({
            "id":         c.id,
            "patient_id": c.patient_id,
            "patient":    f"{pat.prenom} {pat.nom}" if pat else "—",
            "age":        age,
            "pathology":  principale.get("nom") if principale else "—",
            "status":     c.statut,
            "date":       c.created_at.strftime("%Y-%m-%d") if c.created_at else None,
            "time":       c.created_at.strftime("%H:%M") if c.created_at else None,
            "doctor":     f"Dr. {medecin.prenom} {medecin.nom}",
        })
    return data


# ── GET /consultations/cas-graves — Cas urgents / critiques ─────
@router.get("/cas-graves")
async def cas_graves(
    db:      AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    from sqlalchemy.orm import selectinload
    from datetime import date

    result = await db.execute(
        select(Consultation)
        .options(
            selectinload(Consultation.patient),
            selectinload(Consultation.diagnostic),
        )
        .where(Consultation.medecin_id == medecin.id)
        .order_by(Consultation.created_at.desc())
    )
    all_c = result.scalars().all()

    graves = [
        c for c in all_c
        if c.statut_clinique in ("urgent", "critique")
        or (c.diagnostic and c.diagnostic.etat_patient in ("urgent", "critique"))
    ]

    data = []
    for c in graves:
        p    = c.patient
        diag = c.diagnostic
        symp = c.symptomes or {}

        age = None
        if p and p.date_naissance:
            today = date.today()
            age   = today.year - p.date_naissance.year - (
                (today.month, today.day) < (p.date_naissance.month, p.date_naissance.day)
            )

        # Pathologie principale (premier résultat IA)
        maladies = diag.maladies if diag else []
        principale = maladies[0] if maladies else None

        data.append({
            "consultation_id":       c.id,
            "patient_id":            p.id       if p else None,
            "patient_nom":           p.nom      if p else "—",
            "patient_prenom":        p.prenom   if p else "—",
            "patient_age":           age,
            "patient_sexe":          p.sexe     if p else None,
            "patient_groupe_sanguin": p.groupe_sanguin if p else None,
            "statut_clinique":       c.statut_clinique,
            "statut":                c.statut,
            "diagnostic": {
                "pathologie":  principale.get("nom") if principale else None,
                "confidence":  principale.get("pct") if principale else None,
                "etat_patient": diag.etat_patient if diag else None,
                "maladies":    maladies[:3],
            } if diag else None,
            "signes_vitaux": {
                "temperature":           symp.get("temperature") or symp.get("fievre_temperature"),
                "saturation_o2":         symp.get("saturation_o2"),
                "frequence_cardiaque":   symp.get("frequence_cardiaque"),
                "frequence_respiratoire": symp.get("frequence_respiratoire"),
                "tension_systolique":    symp.get("tension_systolique"),
                "tension_diastolique":   symp.get("tension_diastolique"),
            },
            "motif":          symp.get("motif"),
            "hospitalisation": (c.prescriptions or {}).get("hospitalisation", False),
            "suivi":          (c.prescriptions or {}).get("suivi"),
            "created_at":     c.created_at.isoformat() if c.created_at else None,
            "updated_at":     c.updated_at.isoformat() if c.updated_at else None,
        })

    return data


# ── PATCH /consultations/:id/antecedents — Étape 2 ───────────────
@router.patch("/{consultation_id}/antecedents", status_code=200)
async def sauvegarder_antecedents(
    consultation_id: str,
    payload: AntecedentsIn,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    c = await get_ma_consultation(consultation_id, medecin.id, db)
    ant = payload.model_dump()
    c.antecedents_consultation = ant

    # Mettre à jour aussi patient.antecedents (snapshot vivant)
    patient = await db.get(Patient, c.patient_id)
    if patient:
        patient.antecedents = ant

    await db.commit()
    return {"message": "Antécédents sauvegardés"}


# ── PATCH /consultations/:id/symptomes — Étape 3 ─────────────────
@router.patch("/{consultation_id}/symptomes", status_code=200)
async def sauvegarder_symptomes(
    consultation_id: str,
    payload: SymptomesIn,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    c = await get_ma_consultation(consultation_id, medecin.id, db)
    c.symptomes = payload.model_dump()
    await db.commit()
    return {"message": "Symptômes sauvegardés"}


# ── POST /consultations/:id/opinion — Étape 4 (avis médecin) ─────
#
# RÈGLE MÉTIER :
#   - Si le médecin soumet son avis → statut = "terminee"
#   - Si pas d'avis (consultation sauvegardée sans avis) → reste "en_attente"
#   - Le médecin peut partager avec un médecin OU une communauté
#   - Il peut envoyer le bilan par mail au patient
# ─────────────────────────────────────────────────────────────────
@router.post("/{consultation_id}/opinion", status_code=200)
async def sauvegarder_opinion(
    consultation_id: str,
    payload: OpinionIn,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    from sqlalchemy.orm import selectinload

    # Charger la consultation AVEC le diagnostic (évite le lazy-load interdit en async)
    result = await db.execute(
        select(Consultation)
        .where(Consultation.id == consultation_id)
        .options(selectinload(Consultation.diagnostic))
    )
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(404, "Consultation introuvable")
    if c.medecin_id != medecin.id:
        raise HTTPException(403, "Accès refusé")

    # Prescription
    c.prescriptions = {
        "medicaments":           payload.medicaments,
        "conseils_maison":       payload.conseils_maison,
        "recommandations":       payload.recommandations,
        "arret_travail":         payload.arret_travail,
        "duree_arret":           payload.duree_arret,
        "hospitalisation":       payload.hospitalisation,
        "motif_hospitalisation": payload.motif_hospitalisation,
        "suivi":                 payload.suivi,
    }
    c.avis_medecin    = payload.observations
    c.observations    = payload.observations
    c.recommandations = payload.recommandations

    # Partage
    c.partage = payload.partage.model_dump()

    # Statut avis médecin — on exclut recommandations (auto-rempli par l'IA)
    a_donne_avis = bool(
        payload.observations or payload.medicaments or payload.conseils_maison
    )
    c.statut = "terminee" if a_donne_avis else "en_attente"

    # Statut clinique depuis le diagnostic IA (déjà chargé via selectinload)
    if c.diagnostic and c.diagnostic.etat_patient:
        etat = c.diagnostic.etat_patient
        if etat in ("stable", "surveille", "urgent", "critique"):
            c.statut_clinique = etat

    await db.commit()

    # ── Partage avec un médecin ──────────────────────────────────
    if payload.partage.actif and payload.partage.type == "medecin" and payload.partage.destinataire_id:
        # TODO: créer une notification pour le médecin destinataire
        # await notifier_medecin(payload.partage.destinataire_id, consultation_id, db)
        pass

    # ── Partage avec une communauté ──────────────────────────────
    if payload.partage.actif and payload.partage.type == "communaute" and payload.partage.destinataire_id:
        # TODO: créer une Publication dans la communauté
        # await publier_dans_communaute(c, payload.partage, medecin, db)
        pass

    # ── Mail au patient ──────────────────────────────────────────
    if payload.partage.envoyer_mail_patient:
        patient = await db.get(Patient, c.patient_id)
        if patient and patient.email:
            # TODO: générer PDF + envoyer par email
            # await envoyer_bilan_patient(patient, c, db)
            pass

    return {
        "message":         "Consultation terminée" if a_donne_avis else "Consultation en attente",
        "statut":          c.statut,
        "consultation_id": consultation_id,
    }


# ── GET /consultations/:id/pdf — Télécharger le bilan ────────────
@router.get("/{consultation_id}/pdf")
async def telecharger_pdf(
    consultation_id: str,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    c = await get_ma_consultation(consultation_id, medecin.id, db)
    patient = await db.get(Patient, c.patient_id)

    # Charger le diagnostic explicitement — le lazy-load SQLAlchemy est interdit en async
    r_diag = await db.execute(
        select(DiagnosticIA).where(DiagnosticIA.consultation_id == c.id)
    )
    diag = r_diag.scalar_one_or_none()

    from app.services.pdf_service import generer_bilan_pdf
    pdf_bytes = await generer_bilan_pdf(consultation=c, patient=patient, diag=diag)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="bilan_{consultation_id}.pdf"'},
    )



# ── PATCH /consultations/:id/statut-clinique — Changer statut ────
# Permet au médecin de modifier manuellement le statut clinique
# (ex: passer urgent → stable après amélioration)
@router.patch("/{consultation_id}/statut-clinique", status_code=200)
async def changer_statut_clinique(
    consultation_id: str,
    payload: StatutCliniqueIn,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    c = await get_ma_consultation(consultation_id, medecin.id, db)
    c.statut_clinique = payload.statut_clinique
    await db.commit()
    return {
        "message":         f"Statut clinique mis à jour : {payload.statut_clinique}",
        "statut_clinique": c.statut_clinique,
        "consultation_id": consultation_id,
    }


# ── GET /consultations/historique — Historique enrichi ───────────
# Retourne toutes les consultations du médecin avec patient,
# diagnostic, feedback, prescription — pour la page Historique
@router.get("/historique")
async def historique_consultations(
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    from sqlalchemy.orm import selectinload
    from app.models.feedback_ia import FeedbackIA
    from app.models.medecin import Medecin

    result = await db.execute(
        select(Consultation)
        .where(
            Consultation.medecin_id == medecin.id,
            Consultation.statut == "terminee",
        )
        .options(
            selectinload(Consultation.diagnostic),
            selectinload(Consultation.patient),
        )
        .order_by(Consultation.created_at.desc())
        .limit(200)
    )
    consultations = result.scalars().unique().all()

    data = []
    for c in consultations:
        # Feedback
        feedback = None
        if c.diagnostic:
            fb = await db.execute(
                select(FeedbackIA)
                .where(FeedbackIA.diagnostic_id == c.diagnostic.id)
                .limit(1)
            )
            feedback = fb.scalar_one_or_none()

        # Médecin de la consultation
        med = await db.get(Medecin, c.medecin_id)

        # Patient (âge calculé)
        pat = c.patient
        age = None
        if pat and pat.date_naissance:
            from datetime import date
            today = date.today()
            age   = today.year - pat.date_naissance.year - (
                (today.month, today.day) < (pat.date_naissance.month, pat.date_naissance.day)
            )

        data.append({
            "id":              c.id,
            "statut":          c.statut,
            "statut_clinique": getattr(c, 'statut_clinique', 'stable'),
            "created_at":      c.created_at.isoformat(),
            "avis_medecin":    c.avis_medecin,
            "observations":    c.observations,
            "recommandations": c.recommandations,
            "prescriptions":   c.prescriptions or {},
            "symptomes":       c.symptomes or {},
            "antecedents_consultation": c.antecedents_consultation or {},
            "patient": {
                "id":                  pat.id,
                "nom":                 pat.nom,
                "prenom":              pat.prenom,
                "civilite":            pat.civilite,
                "age":                 age,
                "telephone":           pat.telephone,
                "adresse":             pat.adresse,
                "religion":            pat.religion,
                "groupe_sanguin":      pat.groupe_sanguin,
                "allergies":           pat.allergies or [],
                "personne_a_contacter": pat.personne_a_contacter,
            } if pat else None,
            "medecin": {
                "id":           med.id,
                "nom":          med.nom,
                "prenom":       med.prenom,
                "specialite":   getattr(med, 'specialite', None),
                "ville":        getattr(med, 'ville', None),
                "etablissement": getattr(med, 'etablissement', None),
            } if med else None,
            "diagnostic": {
                "id":                  c.diagnostic.id,
                "maladies":            c.diagnostic.maladies or [],
                "etat_patient":        c.diagnostic.etat_patient,
                "version_modele":      c.diagnostic.version_modele,
                "type_consultation":   getattr(c.diagnostic, 'type_consultation', None),
                "recommandations":     c.diagnostic.recommandations or [],
                "examens_recommandes": (
                    c.diagnostic.maladies[0].get('examens_suggeres', [])
                    if c.diagnostic.maladies else []
                ),
            } if c.diagnostic else None,
            "feedback": {
                "concordance":      feedback.concordance,
                "diagnostic_final": feedback.diagnostic_final,
                "commentaire":      feedback.commentaire,
            } if feedback else None,
            "is_shared": False,  # consultations du médecin lui-même
        })
    return data


# ── DELETE /consultations/doublons — Nettoyer les doublons en_attente ─
@router.delete("/doublons", status_code=200)
async def supprimer_doublons(
    db: AsyncSession = Depends(get_db),
    medecin          = Depends(get_current_medecin),
):
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Consultation)
        .where(
            Consultation.medecin_id == medecin.id,
            Consultation.statut     == "en_attente",
        )
        .options(selectinload(Consultation.diagnostic))
        .order_by(Consultation.patient_id, Consultation.created_at.desc())
    )
    all_pending = result.scalars().unique().all()

    # Pour chaque patient, garder la plus récente sans diagnostic, supprimer les autres
    seen = {}
    to_delete = []
    for c in all_pending:
        if c.diagnostic is not None:
            continue  # a déjà un diagnostic, ne pas toucher
        if c.patient_id not in seen:
            seen[c.patient_id] = c.id  # garder celle-ci
        else:
            to_delete.append(c)

    for c in to_delete:
        await db.delete(c)

    await db.commit()
    return {"supprimees": len(to_delete), "message": f"{len(to_delete)} consultation(s) en doublon supprimée(s)"}


# ── GET /consultations — Liste des consultations ─────────────────
@router.get("", response_model=list[ConsultationOut])
async def lister_consultations(
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    result = await db.execute(
        select(Consultation)
        .where(Consultation.medecin_id == medecin.id)
        .order_by(Consultation.created_at.desc())
        .limit(50)
    )
    return result.scalars().all()


# ── GET /consultations/en-attente — Consultations sans avis ──────
@router.get("/en-attente", response_model=list[ConsultationOut])
async def consultations_en_attente(
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    result = await db.execute(
        select(Consultation)
        .where(
            Consultation.medecin_id == medecin.id,
            Consultation.statut    == "en_attente",
        )
        .order_by(Consultation.created_at.desc())
    )
    return result.scalars().all()


# ── GET /consultations/:id — Charger une consultation existante ───
# DOIT être en dernier pour ne pas intercepter /historique, /en-attente
@router.get("/{consultation_id}")
async def get_consultation(
    consultation_id: str,
    db: AsyncSession  = Depends(get_db),
    medecin           = Depends(get_current_medecin),
):
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Consultation)
        .where(Consultation.id == consultation_id)
        .options(selectinload(Consultation.diagnostic), selectinload(Consultation.patient))
    )
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(404, "Consultation introuvable")
    if c.medecin_id != medecin.id:
        raise HTTPException(403, "Accès refusé")

    patient = c.patient
    return {
        "id":                     c.id,
        "patient_id":             c.patient_id,
        "statut":                 c.statut,
        "antecedents":            c.antecedents_consultation or {},
        "symptomes":              c.symptomes              or {},
        "has_diagnostic":         c.diagnostic is not None,
        "patient": {
            "id":                  patient.id,
            "civilite":            patient.civilite,
            "nom":                 patient.nom,
            "prenom":              patient.prenom,
            "date_naissance":      str(patient.date_naissance) if patient.date_naissance else None,
            "telephone":           patient.telephone,
            "email":               patient.email,
            "adresse":             patient.adresse,
            "profession":          patient.profession,
            "religion":            patient.religion,
            "groupe_sanguin":      patient.groupe_sanguin,
            "personne_a_contacter":patient.personne_a_contacter,
            "telephone_urgence":   patient.telephone_urgence,
        } if patient else None,
    }
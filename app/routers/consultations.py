# app/routers/consultations.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
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
    AntecedentsIn, SymptomesIn, OpinionIn, StatutCliniqueIn,
)

router = APIRouter(prefix="/api/v1/consultations", tags=["Consultations"])


# ── Helpers ──────────────────────────────────────────────────────

async def verifier_acces_patient(patient_id: str, medecin_id: str, db: AsyncSession) -> Patient:
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient introuvable")
    if patient.created_by == medecin_id:
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
    c = await get_ma_consultation(consultation_id, medecin.id, db)

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

    # ← RÈGLE MÉTIER : consultation terminée seulement si le médecin a écrit quelque chose
    a_donne_avis = bool(
        payload.observations or payload.medicaments or
        payload.recommandations or payload.conseils_maison
    )
    c.statut = "terminee" if a_donne_avis else "en_attente"

    # Alimenter statut_clinique depuis diagnostic.etat_patient (si pas encore défini)
    if not c.statut_clinique:
        diag_result = await db.execute(
            select(DiagnosticIA).where(DiagnosticIA.consultation_id == consultation_id)
        )
        diag = diag_result.scalar_one_or_none()
        if diag and diag.etat_patient:
            c.statut_clinique = diag.etat_patient

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

    from app.services.pdf_service import generer_bilan_pdf
    pdf_bytes = await generer_bilan_pdf(consultation=c, patient=patient)

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="bilan_{consultation_id}.pdf"'},
    )


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


# ── PATCH /consultations/:id/statut-clinique — Modifier l'état clinique ──
@router.patch("/{consultation_id}/statut-clinique", status_code=200)
async def modifier_statut_clinique(
    consultation_id: str,
    payload: StatutCliniqueIn,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    c = await get_ma_consultation(consultation_id, medecin.id, db)
    c.statut_clinique = payload.statut_clinique
    await db.commit()
    return {"statut_clinique": c.statut_clinique, "consultation_id": consultation_id}


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
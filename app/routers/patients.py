# app/routers/patients.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.database import get_db
from app.core.security import get_current_medecin
from app.models.patient import Patient
from app.models.acces_patient import AccesPatient
from app.schemas.patient import PatientCreate, PatientOut, PatientSearchResult
from app.schemas.consultation import AccesRequestIn, AccesRequestOut

router = APIRouter(prefix="/api/v1/patients", tags=["Patients"])


# ── POST /patients — Créer un patient ────────────────────────────
@router.post("", response_model=PatientOut, status_code=201)
async def creer_patient(
    payload: PatientCreate,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    # civilite → sexe
    sexe = "M" if payload.civilite == "M" else "F" if payload.civilite == "Mme" else None

    patient = Patient(
        nom                  = payload.nom.upper().strip(),
        prenom               = payload.prenom.strip(),
        civilite             = payload.civilite,
        sexe                 = sexe,
        date_naissance       = payload.date_naissance,
        groupe_sanguin       = payload.groupe_sanguin,
        religion             = payload.religion,
        telephone            = payload.telephone,
        email                = payload.email,
        adresse              = payload.adresse,
        profession           = payload.profession,
        personne_a_contacter = payload.personne_a_contacter,
        telephone_urgence    = payload.telephone_urgence,
        allergies            = payload.allergies or [],
        antecedents          = payload.antecedents or {},
        created_by           = medecin.id,
    )
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient


# ── GET /patients/search?q=terme — Recherche ─────────────────────
@router.get("/search", response_model=list[PatientSearchResult])
async def rechercher_patients(
    q: str = Query(..., min_length=2),
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    terme = f"%{q.strip()}%"
    result = await db.execute(
        select(Patient).where(
            or_(
                Patient.nom.ilike(terme),
                Patient.prenom.ilike(terme),
                Patient.telephone.ilike(terme),
            )
        ).limit(20)
    )
    return result.scalars().all()


# ── GET /patients/:id — Détail patient ───────────────────────────
@router.get("/{patient_id}", response_model=PatientOut)
async def get_patient(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient introuvable")

    # Accès : propriétaire OU accès accordé
    if patient.created_by != medecin.id:
        acces = await db.execute(
            select(AccesPatient).where(
                AccesPatient.patient_id          == patient_id,
                AccesPatient.medecin_demandeur_id == medecin.id,
                AccesPatient.statut              == "accorde",
            )
        )
        if not acces.scalar_one_or_none():
            raise HTTPException(403, "Accès refusé — ce patient appartient à un autre médecin")

    return patient


# ── POST /patients/access-requests — Demander accès ──────────────
@router.post("/access-requests", response_model=AccesRequestOut, status_code=201)
async def demander_acces(
    payload: AccesRequestIn,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    patient = await db.get(Patient, payload.patient_id)
    if not patient:
        raise HTTPException(404, "Patient introuvable")
    if not patient.created_by:
        raise HTTPException(400, "Ce patient n'a pas de médecin propriétaire")

    # Demande déjà existante ?
    existing = await db.execute(
        select(AccesPatient).where(
            AccesPatient.patient_id           == payload.patient_id,
            AccesPatient.medecin_demandeur_id == medecin.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(409, "Une demande d'accès existe déjà pour ce patient")

    demande = AccesPatient(
        patient_id              = payload.patient_id,
        medecin_demandeur_id    = medecin.id,
        medecin_proprietaire_id = patient.created_by,
        justificatif_demande    = payload.justificatif,
        statut                  = "en_attente",
    )
    db.add(demande)
    await db.commit()
    await db.refresh(demande)

    # TODO: notifier le médecin propriétaire
    # await creer_notification(patient.created_by, "acces_patient_demande", demande, db)

    return demande
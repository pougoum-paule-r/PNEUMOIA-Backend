# app/routers/patients.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from datetime import datetime, timezone

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


# ── GET /patients/mes-patients — Patients du médecin connecté ────
@router.get("/mes-patients", response_model=list[PatientOut])
async def mes_patients(
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    result = await db.execute(
        select(Patient)
        .where(Patient.created_by == medecin.id)
        .where(Patient.deleted_at.is_(None))
        .order_by(Patient.created_at.desc())
    )
    return result.scalars().all()


# ── DELETE /patients/:id — Soft-delete (corbeille) ───────────────
@router.delete("/{patient_id}", status_code=204)
async def supprimer_patient(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient introuvable")
    if patient.created_by != medecin.id:
        raise HTTPException(403, "Accès refusé")
    if patient.deleted_at is not None:
        raise HTTPException(409, "Patient déjà en corbeille")

    patient.deleted_at = datetime.now(timezone.utc).replace(tzinfo=None)
    patient.deleted_by = medecin.id
    await db.commit()
    return None


# ── GET /patients/corbeille — Patients soft-deletés du médecin ───
@router.get("/corbeille", response_model=list[PatientOut])
async def corbeille_patients(
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    result = await db.execute(
        select(Patient)
        .where(Patient.created_by == medecin.id)
        .where(Patient.deleted_at.is_not(None))
        .order_by(Patient.deleted_at.desc())
    )
    return result.scalars().all()


# ── PATCH /patients/:id/restaurer — Annuler le soft-delete ───────
@router.patch("/{patient_id}/restaurer", response_model=PatientOut)
async def restaurer_patient(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient introuvable")
    if patient.created_by != medecin.id:
        raise HTTPException(403, "Accès refusé")

    patient.deleted_at = None
    patient.deleted_by = None
    await db.commit()
    await db.refresh(patient)
    return patient


# ── GET /patients/:id/consultations ──────────────────────────────
@router.get("/{patient_id}/consultations")
async def consultations_patient(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    from app.models.consultation import Consultation
    from app.models.medecin import Medecin
    from app.models.feedback_ia import FeedbackIA
    from sqlalchemy.orm import selectinload

    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient introuvable")

    # Accès : propriétaire OU accès accordé
    if patient.created_by != medecin.id:
        acces_result = await db.execute(
            select(AccesPatient).where(
                AccesPatient.patient_id           == patient_id,
                AccesPatient.medecin_demandeur_id == medecin.id,
                AccesPatient.statut               == "accorde",
            )
        )
        if not acces_result.scalar_one_or_none():
            raise HTTPException(403, "Accès refusé")

    result = await db.execute(
        select(Consultation)
        .where(Consultation.patient_id == patient_id)
        .options(selectinload(Consultation.diagnostic))
        .order_by(Consultation.created_at.desc())
    )
    consultations = result.scalars().all()

    data = []
    for c in consultations:
        # Charger le feedback médecin si existe
        feedback = None
        if c.diagnostic:
            fb_result = await db.execute(
                select(FeedbackIA)
                .where(FeedbackIA.diagnostic_id == c.diagnostic.id)
                .limit(1)
            )
            feedback = fb_result.scalar_one_or_none()

        # Charger le médecin qui a fait la consultation
        med_consult = await db.get(Medecin, c.medecin_id) if getattr(c, 'medecin_id', None) else None
        # Fallback : médecin créateur du patient
        if not med_consult and patient.created_by:
            med_consult = await db.get(Medecin, patient.created_by)

        data.append({
            "id":               c.id,
            "statut":           c.statut,
            "statut_clinique":  c.statut_clinique,
            "created_at":       c.created_at.isoformat(),
            "observations":    c.observations,
            "recommandations": c.recommandations,
            "prescriptions":   c.prescriptions,
            "avis_medecin":    c.avis_medecin,
            "symptomes":       c.symptomes or {},
            # Médecin ayant effectué la consultation
            "medecin": {
                "id":         med_consult.id,
                "nom":        med_consult.nom,
                "prenom":     med_consult.prenom,
                "specialite": getattr(med_consult, 'specialite', None),
                "ville":      getattr(med_consult, 'ville', None),
            } if med_consult else None,
            "diagnostic": {
                "id":                  c.diagnostic.id             if c.diagnostic else None,
                "maladies":            c.diagnostic.maladies       if c.diagnostic else [],
                "etat_patient":        c.diagnostic.etat_patient   if c.diagnostic else None,
                # version_modele : 'equipe' si FVC+FEV1 fournis, 'base' sinon
                "version_modele":      c.diagnostic.version_modele if c.diagnostic else None,
                "type_consultation":   c.diagnostic.type_consultation if c.diagnostic and hasattr(c.diagnostic, 'type_consultation') else None,
                "recommandations":     c.diagnostic.recommandations if c.diagnostic else [],
                "alertes":             c.diagnostic.alertes        if c.diagnostic and hasattr(c.diagnostic, 'alertes') else [],
                "examens_recommandes": (
                    c.diagnostic.maladies[0].get('examens_suggeres', [])
                    if c.diagnostic and c.diagnostic.maladies else []
                ),
            } if c.diagnostic else None,
            "feedback": {
                "concordance":      feedback.concordance      if feedback else None,
                "diagnostic_final": feedback.diagnostic_final if feedback else None,
                "commentaire":      feedback.commentaire      if feedback else None,
            } if feedback else None,
        })
    return data


# ── PATCH /patients/:id — Modifier un patient ─────────────────────
@router.patch("/{patient_id}", response_model=PatientOut)
async def modifier_patient(
    patient_id: str,
    payload: PatientCreate,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient introuvable")
    if patient.created_by != medecin.id:
        raise HTTPException(403, "Accès refusé — vous ne pouvez modifier que vos propres patients")

    # Mettre à jour les champs
    patient.nom                  = payload.nom.upper().strip()
    patient.prenom               = payload.prenom.strip()
    patient.civilite             = payload.civilite
    patient.sexe                 = "M" if payload.civilite == "M" else "F" if payload.civilite == "Mme" else None
    patient.date_naissance       = payload.date_naissance
    patient.groupe_sanguin       = payload.groupe_sanguin
    patient.religion             = payload.religion
    patient.telephone            = payload.telephone
    patient.email                = payload.email
    patient.adresse              = payload.adresse
    patient.profession           = payload.profession
    patient.personne_a_contacter = payload.personne_a_contacter
    patient.telephone_urgence    = payload.telephone_urgence

    await db.commit()
    await db.refresh(patient)
    return patient


# ── GET /patients/:id/acces — Liste des médecins ayant accès ─────
@router.get("/{patient_id}/acces")
async def acces_patient(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    """
    Retourne la liste des médecins ayant accès au dossier patient.
    Le propriétaire (created_by) est toujours en premier avec est_proprietaire=True.
    """
    from app.models.medecin import Medecin

    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient introuvable")

    # Vérifier que le demandeur a accès (propriétaire ou accès accordé)
    if patient.created_by != medecin.id:
        acces_check = await db.execute(
            select(AccesPatient).where(
                AccesPatient.patient_id           == patient_id,
                AccesPatient.medecin_demandeur_id == medecin.id,
                AccesPatient.statut               == "accorde",
            )
        )
        if not acces_check.scalar_one_or_none():
            raise HTTPException(403, "Accès refusé")

    result = []

    # 1. Propriétaire (médecin créateur du patient)
    if patient.created_by:
        proprietaire = await db.get(Medecin, patient.created_by)
        if proprietaire:
            result.append({
                "medecin_id":      proprietaire.id,
                "nom":             proprietaire.nom,
                "prenom":          proprietaire.prenom,
                "specialite":      getattr(proprietaire, 'specialite', None),
                "ville":           getattr(proprietaire, 'ville', None),
                "role":            "proprietaire",
                "est_proprietaire": True,
                "est_moi":         proprietaire.id == medecin.id,
                "depuis":          patient.created_at.isoformat() if patient.created_at else None,
            })

    # 2. Médecins avec accès accordé
    acces_accordes = await db.execute(
        select(AccesPatient).where(
            AccesPatient.patient_id == patient_id,
            AccesPatient.statut     == "accorde",
        )
    )
    for acces in acces_accordes.scalars().all():
        # Ne pas dupliquer le propriétaire
        if acces.medecin_demandeur_id == patient.created_by:
            continue
        med = await db.get(Medecin, acces.medecin_demandeur_id)
        if med:
            result.append({
                "medecin_id":       med.id,
                "nom":              med.nom,
                "prenom":           med.prenom,
                "specialite":       getattr(med, 'specialite', None),
                "ville":            getattr(med, 'ville', None),
                "role":             "acces",
                "est_proprietaire": False,
                "est_moi":          med.id == medecin.id,
                "depuis":           acces.created_at.isoformat() if getattr(acces, 'created_at', None) else None,
            })

    return result


# ── DELETE /patients/:id/acces/:medecin_id — Révoquer un accès ───
@router.delete("/{patient_id}/acces/{medecin_id}", status_code=204)
async def revoquer_acces(
    patient_id: str,
    medecin_id: str,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient introuvable")
    if patient.created_by != medecin.id:
        raise HTTPException(403, "Seul le propriétaire peut révoquer un accès")

    acces = await db.execute(
        select(AccesPatient).where(
            AccesPatient.patient_id           == patient_id,
            AccesPatient.medecin_demandeur_id == medecin_id,
        )
    )
    acces_obj = acces.scalar_one_or_none()
    if not acces_obj:
        raise HTTPException(404, "Accès introuvable")

    await db.delete(acces_obj)
    await db.commit()
    return None


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
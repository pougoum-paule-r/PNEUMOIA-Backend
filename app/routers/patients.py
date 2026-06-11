# app/routers/patients.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from datetime import datetime, timezone
<<<<<<< HEAD
from pydantic import BaseModel

class MotifRefusIn(BaseModel):
    motif_refus: str | None = None

class AvisIn(BaseModel):
    contenu: str
=======
from typing import Optional
from pydantic import BaseModel
>>>>>>> 04d28998c0bfade766fe29abd76b92e188a5ee68

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


# ── GET /patients/recherche-par-code?code=XXX — Fiche partielle ──
# Endpoint sécurisé : retourne uniquement les données non-sensibles
# sans nécessiter d'être propriétaire du dossier
@router.get("/recherche-par-code")
async def recherche_par_code(
    code: str,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    from app.models.medecin import Medecin

    from app.models.consultation import Consultation

    patient = await db.get(Patient, code.strip().upper())
    if not patient or patient.deleted_at is not None:
        raise HTTPException(404, "Patient introuvable avec cet identifiant")

    # Le dossier n'est partageable que si le médecin a soumis son avis
    avis_check = await db.execute(
        select(Consultation).where(
            Consultation.patient_id == patient.id,
            Consultation.avis_medecin.isnot(None),
        ).limit(1)
    )
    if not avis_check.scalar_one_or_none():
        raise HTTPException(404, "Patient introuvable avec cet identifiant")

    proprietaire = None
    if patient.created_by:
        proprietaire = await db.get(Medecin, patient.created_by)

    age = None
    if patient.date_naissance:
        from datetime import date
        today = date.today()
        age   = today.year - patient.date_naissance.year - (
            (today.month, today.day) < (patient.date_naissance.month, patient.date_naissance.day)
        )

    # Fiche partielle — pas de diagnostic, pas d'antécédents détaillés
    return {
        "id":                   patient.id,
        "nom":                  patient.nom,
        "prenom":               patient.prenom,
        "civilite":             patient.civilite,
        "sexe":                 patient.sexe,
        "age":                  age,
        "groupe_sanguin":       patient.groupe_sanguin,
        "religion":             patient.religion,
        "telephone_urgence":    patient.telephone_urgence,
        "personne_a_contacter": patient.personne_a_contacter,
        "medecin_referent":     f"Dr. {proprietaire.prenom} {proprietaire.nom}" if proprietaire else None,
    }


# ── GET /patients/access-requests/envoyees — Demandes envoyées ───
@router.get("/access-requests/envoyees")
async def demandes_envoyees(
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    from app.models.medecin import Medecin

    result = await db.execute(
        select(AccesPatient, Patient)
        .join(Patient, AccesPatient.patient_id == Patient.id)
        .where(AccesPatient.medecin_demandeur_id == medecin.id)
        .order_by(AccesPatient.created_at.desc())
    )
    rows = result.all()

    data = []
    for acces, patient in rows:
        proprietaire = None
        if patient.created_by:
            proprietaire = await db.get(Medecin, patient.created_by)

        data.append({
            "id":                   acces.id,
            "patient_id":           patient.id,
            "patient_nom":          patient.nom,
            "patient_prenom":       patient.prenom,
            "statut":               acces.statut,
            "justificatif":         acces.justificatif_demande,
            "motif_refus":          acces.motif_refus,
            "created_at":           acces.created_at.isoformat() if acces.created_at else None,
            "updated_at":           acces.updated_at.isoformat() if acces.updated_at else None,
            "medecin_proprietaire": f"Dr. {proprietaire.prenom} {proprietaire.nom}" if proprietaire else None,
        })
    return data


# ── GET /patients/access-requests/recues — Demandes reçues ───────
@router.get("/access-requests/recues")
async def demandes_recues(
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    from app.models.medecin import Medecin

    result = await db.execute(
        select(AccesPatient, Patient)
        .join(Patient, AccesPatient.patient_id == Patient.id)
        .where(
            AccesPatient.medecin_proprietaire_id == medecin.id,
            AccesPatient.statut == "en_attente",
        )
        .order_by(AccesPatient.created_at.desc())
    )
    rows = result.all()

    data = []
    for acces, patient in rows:
        demandeur = await db.get(Medecin, acces.medecin_demandeur_id)
        data.append({
            "id":                    acces.id,
            "patient_id":            patient.id,
            "patient_nom":           patient.nom,
            "patient_prenom":        patient.prenom,
            "urgent":                False,
            "created_at":            acces.created_at.isoformat() if acces.created_at else None,
            "justificatif_demande":  acces.justificatif_demande,
            "diagnostic":            acces.justificatif_demande,
            "medecin_nom":           demandeur.nom        if demandeur else None,
            "medecin_prenom":        demandeur.prenom     if demandeur else None,
            "medecin_specialite":    getattr(demandeur, 'specialite', None) if demandeur else None,
            "medecin_hopital":       getattr(demandeur, 'hopital',    None) if demandeur else None,
            "medecin_ville":         getattr(demandeur, 'ville',      None) if demandeur else None,
        })
    return data


# ── POST /patients/access-requests/:id/accepter ──────────────────
@router.post("/access-requests/{demande_id}/accepter", status_code=200)
async def accepter_demande(
    demande_id: str,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    acces = await db.get(AccesPatient, demande_id)
    if not acces:
        raise HTTPException(404, "Demande introuvable")
    if acces.medecin_proprietaire_id != medecin.id:
        raise HTTPException(403, "Accès refusé")
    acces.statut = "accorde"
    await db.commit()
    return {"message": "Accès accordé"}


# ── POST /patients/access-requests/:id/refuser ───────────────────
@router.post("/access-requests/{demande_id}/refuser", status_code=200)
async def refuser_demande(
    demande_id: str,
    body: MotifRefusIn = Body(default=MotifRefusIn()),
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    acces = await db.get(AccesPatient, demande_id)
    if not acces:
        raise HTTPException(404, "Demande introuvable")
    if acces.medecin_proprietaire_id != medecin.id:
        raise HTTPException(403, "Accès refusé")
    acces.statut = "refuse"
    if body.motif_refus:
        acces.motif_refus = body.motif_refus.strip()
    acces.updated_at = datetime.utcnow()
    await db.commit()
    return {"message": "Demande refusée"}


# ── GET /patients/mes-partages — Dossiers partagés ───────────────
@router.get("/mes-partages")
async def mes_partages(
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    from app.models.medecin import Medecin

    result = await db.execute(
        select(AccesPatient, Patient)
        .join(Patient, AccesPatient.patient_id == Patient.id)
        .where(
            AccesPatient.medecin_proprietaire_id == medecin.id,
            AccesPatient.statut == "accorde",
        )
        .order_by(Patient.nom)
    )
    rows = result.all()

    patients_map = {}
    for acces, patient in rows:
        pid = patient.id
        if pid not in patients_map:
            patients_map[pid] = {
                "patient_id":     patient.id,
                "patient_nom":    patient.nom,
                "patient_prenom": patient.prenom,
                "acces": [],
            }
        demandeur = await db.get(Medecin, acces.medecin_demandeur_id)
        if demandeur:
            patients_map[pid]["acces"].append({
                "medecin_id": demandeur.id,
                "nom":        demandeur.nom,
                "prenom":     demandeur.prenom,
                "specialite": getattr(demandeur, 'specialite', None),
                "depuis":     acces.created_at.isoformat() if getattr(acces, 'created_at', None) else None,
            })

    return list(patients_map.values())


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


# ── GET /patients/corbeille — Patients soft-deletés ──────────────
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


# ── PATCH /patients/:id/restaurer ────────────────────────────────
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
        feedback = None
        if c.diagnostic:
            fb_result = await db.execute(
                select(FeedbackIA)
                .where(FeedbackIA.diagnostic_id == c.diagnostic.id)
                .limit(1)
            )
            feedback = fb_result.scalar_one_or_none()

        med_consult = await db.get(Medecin, c.medecin_id) if getattr(c, 'medecin_id', None) else None
        if not med_consult and patient.created_by:
            med_consult = await db.get(Medecin, patient.created_by)

        # Normaliser concordance
        concordance = None
        if feedback and feedback.concordance is not None:
            concordance = feedback.concordance in (True, 'oui', 1)

        data.append({
            "id":              c.id,
            "statut":          c.statut,
            "statut_clinique": getattr(c, 'statut_clinique', 'stable'),
            "created_at":      c.created_at.isoformat(),
            "observations":    c.observations,
            "recommandations": c.recommandations,
            "prescriptions":   c.prescriptions,
            "avis_medecin":    c.avis_medecin,
            "symptomes":       c.symptomes or {},
            "medecin": {
                "id":         med_consult.id,
                "nom":        med_consult.nom,
                "prenom":     med_consult.prenom,
                "specialite": getattr(med_consult, 'specialite', None),
                "ville":      getattr(med_consult, 'ville', None),
            } if med_consult else None,
            "diagnostic": {
                "id":                  c.diagnostic.id,
                "maladies":            c.diagnostic.maladies or [],
                "etat_patient":        c.diagnostic.etat_patient,
                "version_modele":      c.diagnostic.version_modele,
                "type_consultation":   getattr(c.diagnostic, 'type_consultation', None),
                "recommandations":     c.diagnostic.recommandations or [],
                "alertes":             getattr(c.diagnostic, 'alertes', []) or [],
                "examens_recommandes": (
                    c.diagnostic.maladies[0].get('examens_suggeres', [])
                    if c.diagnostic.maladies else []
                ),
            } if c.diagnostic else None,
            "feedback": {
                "concordance":      concordance,
                "diagnostic_final": feedback.diagnostic_final,
                "commentaire":      feedback.commentaire,
            } if feedback else None,
        })
    return data


# ── PATCH /patients/:id — Modifier un patient ────────────────────
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


# ── GET /patients/:id/acces — Médecins ayant accès ───────────────
@router.get("/{patient_id}/acces")
async def acces_patient(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    from app.models.medecin import Medecin

    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient introuvable")

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

    if patient.created_by:
        proprietaire = await db.get(Medecin, patient.created_by)
        if proprietaire:
            result.append({
                "medecin_id":       proprietaire.id,
                "nom":              proprietaire.nom,
                "prenom":           proprietaire.prenom,
                "specialite":       getattr(proprietaire, 'specialite', None),
                "ville":            getattr(proprietaire, 'ville', None),
                "role":             "proprietaire",
                "est_proprietaire": True,
                "est_moi":          proprietaire.id == medecin.id,
                "depuis":           patient.created_at.isoformat() if patient.created_at else None,
            })

    acces_accordes = await db.execute(
        select(AccesPatient).where(
            AccesPatient.patient_id == patient_id,
            AccesPatient.statut     == "accorde",
        )
    )
    for acces in acces_accordes.scalars().all():
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


# ── DELETE /patients/:id/acces/:medecin_id — Révoquer ────────────
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


# ── GET /patients/recherche-par-code?code=XXX ────────────────────
@router.get("/recherche-par-code")
async def recherche_par_code(
    code: str = Query(..., min_length=5),
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    from app.models.medecin import Medecin
    from datetime import date

    patient = await db.get(Patient, code.strip().upper())
    if not patient or patient.deleted_at is not None:
        raise HTTPException(404, "Patient introuvable avec ce code")

    # Calcul de l'âge
    age = None
    if patient.date_naissance:
        today = date.today()
        dob   = patient.date_naissance
        age   = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    # Médecin référent (créateur du patient)
    medecin_referent = None
    if patient.created_by:
        med = await db.get(Medecin, patient.created_by)
        if med:
            medecin_referent = f"Dr. {med.prenom} {med.nom}"

    return {
        "id":               patient.id,
        "nom":              patient.nom,
        "prenom":           patient.prenom,
        "sexe":             patient.sexe,
        "age":              age,
        "groupe_sanguin":   patient.groupe_sanguin,
        "religion":         patient.religion,
        "telephone_urgence": patient.telephone_urgence,
        "medecin_referent": medecin_referent,
    }


# ── GET /patients/access-requests/recues — Demandes reçues ───────
@router.get("/access-requests/recues")
async def demandes_recues(
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    from app.models.medecin import Medecin
    result = await db.execute(
        select(AccesPatient).where(
            AccesPatient.medecin_proprietaire_id == medecin.id,
            AccesPatient.statut == "en_attente",
        ).order_by(AccesPatient.created_at.desc())
    )
    data = []
    for d in result.scalars().all():
        patient   = await db.get(Patient, d.patient_id)
        demandeur = await db.get(Medecin, d.medecin_demandeur_id)
        data.append({
            "id":                   d.id,
            "patient_id":           d.patient_id,
            "patient_nom":          patient.nom    if patient   else "—",
            "patient_prenom":       patient.prenom if patient   else "—",
            "medecin_nom":          demandeur.nom    if demandeur else "—",
            "medecin_prenom":       demandeur.prenom if demandeur else "—",
            "medecin_specialite":   getattr(demandeur, "specialite",   None) if demandeur else None,
            "medecin_hopital":      getattr(demandeur, "etablissement", None) if demandeur else None,
            "medecin_ville":        None,
            "justificatif_demande": d.justificatif_demande,
            "urgent":               False,
            "created_at":           d.created_at.isoformat(),
        })
    return data


# ── GET /patients/access-requests/envoyees — Demandes envoyées ───
@router.get("/access-requests/envoyees")
async def demandes_envoyees(
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    from app.models.medecin import Medecin
    result = await db.execute(
        select(AccesPatient).where(
            AccesPatient.medecin_demandeur_id == medecin.id,
        ).order_by(AccesPatient.created_at.desc())
    )
    data = []
    for d in result.scalars().all():
        patient      = await db.get(Patient, d.patient_id)
        proprietaire = await db.get(Medecin, d.medecin_proprietaire_id)
        data.append({
            "id":                   d.id,
            "patient_id":           d.patient_id,
            "patient_nom":          patient.nom    if patient      else "—",
            "patient_prenom":       patient.prenom if patient      else "—",
            "medecin_proprietaire": f"Dr. {proprietaire.prenom} {proprietaire.nom}" if proprietaire else None,
            "statut":               d.statut,
            "justificatif":         d.justificatif_demande,
            "motif_refus":          d.motif_refus,
            "created_at":           d.created_at.isoformat(),
            "updated_at":           d.updated_at.isoformat() if d.updated_at else None,
        })
    return data


# ── GET /patients/mes-partages — Dossiers que j'ai partagés ──────
@router.get("/mes-partages")
async def mes_partages(
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    from app.models.medecin import Medecin
    patients_res = await db.execute(
        select(Patient).where(
            Patient.created_by == medecin.id,
            Patient.deleted_at.is_(None),
        )
    )
    data = []
    for patient in patients_res.scalars().all():
        acces_res = await db.execute(
            select(AccesPatient).where(
                AccesPatient.patient_id == patient.id,
                AccesPatient.statut == "accorde",
            )
        )
        acces_list = acces_res.scalars().all()
        if not acces_list:
            continue
        acces_data = []
        for a in acces_list:
            med = await db.get(Medecin, a.medecin_demandeur_id)
            if med:
                acces_data.append({
                    "medecin_id": med.id,
                    "nom":        med.nom,
                    "prenom":     med.prenom,
                    "specialite": getattr(med, "specialite", None),
                    "depuis":     a.created_at.isoformat() if a.created_at else None,
                })
        data.append({
            "patient_id":     patient.id,
            "patient_nom":    patient.nom,
            "patient_prenom": patient.prenom,
            "acces":          acces_data,
        })
    return data


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

    if patient.created_by != medecin.id:
        acces = await db.execute(
            select(AccesPatient).where(
                AccesPatient.patient_id           == patient_id,
                AccesPatient.medecin_demandeur_id == medecin.id,
                AccesPatient.statut               == "accorde",
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
    from app.models.consultation import Consultation

    patient = await db.get(Patient, payload.patient_id)
    if not patient:
        raise HTTPException(404, "Patient introuvable")
    if not patient.created_by:
        raise HTTPException(400, "Ce patient n'a pas de médecin propriétaire")

    # Règle 1 : un médecin ne peut pas demander accès à son propre patient
    if patient.created_by == medecin.id:
        raise HTTPException(400, "Vous êtes déjà le médecin propriétaire de ce patient")

    # Règle 2 : le médecin propriétaire doit avoir soumis son avis (au moins une consultation avec avis)
    avis_check = await db.execute(
        select(Consultation).where(
            Consultation.patient_id == payload.patient_id,
            Consultation.avis_medecin.isnot(None),
        ).limit(1)
    )
    if not avis_check.scalar_one_or_none():
        raise HTTPException(
            400,
            "Le médecin propriétaire n'a pas encore rédigé son avis — "
            "le dossier n'est pas encore partageable"
        )

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
    return demande


<<<<<<< HEAD
# ── POST /patients/:id/avis — Laisser un avis collaboratif ────────
@router.post("/{patient_id}/avis", status_code=201)
async def laisser_avis(
    patient_id: str,
    body: AvisIn,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    from app.models.notification import Notification

    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient introuvable")

    # Vérifier accès (propriétaire ou accès accordé)
    if patient.created_by != medecin.id:
        acces = await db.execute(
            select(AccesPatient).where(
                AccesPatient.patient_id           == patient_id,
                AccesPatient.medecin_demandeur_id == medecin.id,
                AccesPatient.statut               == "accorde",
            )
        )
        if not acces.scalar_one_or_none():
            raise HTTPException(403, "Accès refusé")

    # Créer une notification pour le médecin propriétaire
    if patient.created_by and patient.created_by != medecin.id:
        notif = Notification(
            destinataire_id = patient.created_by,
            type_dest       = "medecin",
            type_notif      = "avis_confrere",
            titre           = f"Avis du Dr. {medecin.prenom} {medecin.nom} sur {patient.prenom} {patient.nom}",
            message         = body.contenu[:500],
            meta            = {
                "patient_id":          patient_id,
                "patient_nom":         f"{patient.prenom} {patient.nom}",
                "medecin_id":          medecin.id,
                "medecin_nom":         f"Dr. {medecin.prenom} {medecin.nom}",
                "medecin_specialite":  getattr(medecin, "specialite", None),
                "contenu":             body.contenu,
                "created_at":          datetime.utcnow().isoformat(),
            },
        )
        db.add(notif)
        await db.commit()

    return {"message": "Avis enregistré", "notifié": patient.created_by != medecin.id}


# ── GET /patients/:id/avis — Lister les avis collaboratifs ────────
@router.get("/{patient_id}/avis")
async def lister_avis(
=======
    return demande


# ── POST /patients/access-requests/:id/accepter ───────────────────
@router.post("/access-requests/{demande_id}/accepter")
async def accepter_demande(
    demande_id: str,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    demande = await db.get(AccesPatient, demande_id)
    if not demande:
        raise HTTPException(404, "Demande introuvable")
    if demande.medecin_proprietaire_id != medecin.id:
        raise HTTPException(403, "Accès refusé")
    if demande.statut != "en_attente":
        raise HTTPException(409, f"Demande déjà traitée ({demande.statut})")
    demande.statut = "accorde"
    demande.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await db.commit()
    return {"id": demande.id, "statut": demande.statut}


# ── POST /patients/access-requests/:id/refuser ───────────────────
class RefusIn(BaseModel):
    motif_refus: Optional[str] = None


@router.post("/access-requests/{demande_id}/refuser")
async def refuser_demande(
    demande_id: str,
    payload: RefusIn,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    demande = await db.get(AccesPatient, demande_id)
    if not demande:
        raise HTTPException(404, "Demande introuvable")
    if demande.medecin_proprietaire_id != medecin.id:
        raise HTTPException(403, "Accès refusé")
    if demande.statut != "en_attente":
        raise HTTPException(409, f"Demande déjà traitée ({demande.statut})")
    demande.statut = "refuse"
    demande.motif_refus = payload.motif_refus
    demande.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await db.commit()
    return {"id": demande.id, "statut": demande.statut}


# ── GET /patients/:id/avis — Avis collaboratifs ───────────────────
@router.get("/{patient_id}/avis")
async def get_avis(
>>>>>>> 04d28998c0bfade766fe29abd76b92e188a5ee68
    patient_id: str,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
<<<<<<< HEAD
    from app.models.notification import Notification
    from sqlalchemy import cast
    from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
=======
    from app.models.avis_patient import AvisPatient
    from app.models.medecin import Medecin
>>>>>>> 04d28998c0bfade766fe29abd76b92e188a5ee68

    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient introuvable")
<<<<<<< HEAD

=======
>>>>>>> 04d28998c0bfade766fe29abd76b92e188a5ee68
    if patient.created_by != medecin.id:
        acces = await db.execute(
            select(AccesPatient).where(
                AccesPatient.patient_id           == patient_id,
                AccesPatient.medecin_demandeur_id == medecin.id,
                AccesPatient.statut               == "accorde",
            )
        )
        if not acces.scalar_one_or_none():
            raise HTTPException(403, "Accès refusé")

    result = await db.execute(
<<<<<<< HEAD
        select(Notification).where(
            Notification.type_notif == "avis_confrere",
            Notification.meta["patient_id"].as_string() == patient_id,
        ).order_by(Notification.created_at.desc()).limit(50)
    )
    notifs = result.scalars().all()

    return [
        {
            "id":                 n.id,
            "medecin_nom":        n.meta.get("medecin_nom"),
            "medecin_specialite": n.meta.get("medecin_specialite"),
            "contenu":            n.meta.get("contenu"),
            "created_at":        n.created_at.isoformat() if n.created_at else None,
        }
        for n in notifs
    ]
=======
        select(AvisPatient)
        .where(AvisPatient.patient_id == patient_id)
        .order_by(AvisPatient.created_at.desc())
    )
    data = []
    for a in result.scalars().all():
        med = await db.get(Medecin, a.medecin_id)
        data.append({
            "id":               a.id,
            "medecin_nom":      f"{med.prenom} {med.nom}" if med else "—",
            "medecin_specialite": getattr(med, "specialite", None) if med else None,
            "contenu":          a.contenu,
            "created_at":       a.created_at.isoformat(),
        })
    return data


# ── POST /patients/:id/avis — Soumettre un avis ───────────────────
class AvisIn(BaseModel):
    contenu: str


@router.post("/{patient_id}/avis", status_code=201)
async def soumettre_avis(
    patient_id: str,
    payload: AvisIn,
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    from app.models.avis_patient import AvisPatient
    from app.models.medecin import Medecin

    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient introuvable")
    if patient.created_by != medecin.id:
        acces = await db.execute(
            select(AccesPatient).where(
                AccesPatient.patient_id           == patient_id,
                AccesPatient.medecin_demandeur_id == medecin.id,
                AccesPatient.statut               == "accorde",
            )
        )
        if not acces.scalar_one_or_none():
            raise HTTPException(403, "Accès refusé")

    avis = AvisPatient(
        patient_id = patient_id,
        medecin_id = medecin.id,
        contenu    = payload.contenu.strip(),
    )
    db.add(avis)
    await db.commit()
    await db.refresh(avis)

    med = await db.get(Medecin, medecin.id)
    return {
        "id":               avis.id,
        "medecin_nom":      f"{med.prenom} {med.nom}" if med else "—",
        "medecin_specialite": getattr(med, "specialite", None) if med else None,
        "contenu":          avis.contenu,
        "created_at":       avis.created_at.isoformat(),
    }
>>>>>>> 04d28998c0bfade766fe29abd76b92e188a5ee68

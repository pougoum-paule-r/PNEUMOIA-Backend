from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.core.security import get_current_admin, verify_password, create_access_token
from app.models.admin import Admin
from app.models.question_admin import QuestionAdmin
from app.models.medecin import Medecin
from app.services.admin_service import AdminService
from app.schemas.admin import (
    LoginSchema,
    ResetRequestSchema,
    ResetConfirmSchema,
    RefusRequestSchema,
)

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# ── Login ──────────────────────────────────────────────────────────────────────

@router.post("/auth/login")
async def admin_login(
    body: LoginSchema,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Admin).where(Admin.email == body.email))
    admin = result.scalar_one_or_none()

    if not admin or not verify_password(body.password, admin.password_hash):
        raise HTTPException(401, "Email ou mot de passe incorrect.")

    if not admin.phone:
        admin.phone = body.phone
        await db.commit()
    elif admin.phone != body.phone:
        raise HTTPException(401, "Numéro de téléphone incorrect.")

    token = create_access_token({
        "sub":   str(admin.id),
        "email": admin.email,
        "phone": admin.phone,
        "role":  "admin",
    })

    return {
        "access_token": token,
        "token_type":   "bearer",
        "admin": {
            "id":    admin.id,
            "email": admin.email,
            "phone": admin.phone,
        }
    }


# ── Reset mot de passe ─────────────────────────────────────────────────────────

@router.post("/auth/reset-request")
async def reset_request(
    body: ResetRequestSchema,
    db: AsyncSession = Depends(get_db),
):
    otp = await AdminService.request_password_reset(db, body.email, body.phone)
    try:
        await AdminService.send_otp_sms(otp, body.phone)
    except Exception as e:
        raise HTTPException(503, f"Échec envoi SMS : {str(e)}")
    return {"message": "Code OTP envoyé par SMS. Valide 10 minutes."}


@router.post("/auth/reset-confirm")
async def reset_confirm(
    body: ResetConfirmSchema,
    db: AsyncSession = Depends(get_db),
):
    await AdminService.verify_and_update_password(
        db,
        email=body.email,
        otp=body.otp,
        new_password=body.new_password,
    )
    return {"message": "Mot de passe mis à jour avec succès."}


# ── Demandes en attente ────────────────────────────────────────────────────────

@router.get("/demandes")
async def get_demandes(
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """
    Retourne tous les médecins en attente avec :
    - Toutes les données personnelles
    - Photo de profil (URL complète)
    - Tous les documents (URL + métadonnées)
    """
    return await AdminService.get_demandes(db)


@router.post("/demandes/{medecin_id}/valider")
async def valider_medecin(
    medecin_id: str,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return await AdminService.valider_medecin(db, medecin_id, admin.id)


@router.post("/demandes/{medecin_id}/rejeter")
async def rejeter_medecin(
    medecin_id: str,
    body: RefusRequestSchema,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return await AdminService.rejeter_medecin(db, medecin_id, body.motif)


# ── Validées par mois/année ────────────────────────────────────────────────────

@router.get("/demandes/valides")
async def get_valides(
    mois:  Optional[int] = None,
    annee: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """
    Retourne les médecins validés pour un mois et une année donnés.
    Si mois/annee non fournis, retourne le mois en cours.
    GET /api/admin/demandes/valides?mois=6&annee=2026
    """
    return await AdminService.get_valides(db, mois, annee)


# ── Actions sur les médecins ──────────────────────────────────────────────────

@router.post("/medecins/{medecin_id}/suspendre")
async def suspendre_medecin(
    medecin_id: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """
    Suspend un médecin — statut passe à "suspendu"
    Le médecin ne peut plus se connecter.
    """
    return await AdminService.suspendre_medecin(
        db, medecin_id,
        raison  = body.get("raison", ""),
        duree   = body.get("duree",  ""),
        message = body.get("message",""),
        admin_id= admin.id,
    )


@router.post("/medecins/{medecin_id}/reactiver")
async def reactiver_medecin(
    medecin_id: str,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """
    Réactive un médecin suspendu — statut repasse à "valide"
    """
    return await AdminService.reactiver_medecin(db, medecin_id, admin.id)


@router.delete("/medecins/{medecin_id}")
async def supprimer_medecin(
    medecin_id: str,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """
    Supprime définitivement un médecin et toutes ses données.
    Action irréversible.
    """
    return await AdminService.supprimer_medecin(db, medecin_id)


# ── Inscriptions refusées ─────────────────────────────────────────────────────

@router.get("/demandes/refusees")
async def get_demandes_refusees(
    ville: str | None = None,
    motif: str | None = None,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """
    Retourne les demandes avec statut 'rejete'.
    Filtres optionnels : ville, motif.
    """
    return await AdminService.get_demandes_refusees(db, ville=ville, motif=motif)


@router.delete("/demandes/{medecin_id}/refusees")
async def supprimer_dossier_refuse(
    medecin_id: str,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """
    Supprime définitivement un dossier refusé.
    """
    return await AdminService.supprimer_dossier_refuse(db, medecin_id)


@router.post("/demandes/{medecin_id}/relancer")
async def relancer_medecin(
    medecin_id: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """
    Envoie un e-mail de relance au médecin refusé.
    Body: { message: str }
    Le médecin peut re-soumettre sa demande.
    """
    return await AdminService.relancer_medecin(
        db, medecin_id,
        message = body.get("message", ""),
        admin_id = admin.id,
    )


# ── Médecins par statut ────────────────────────────────────────────────────────

@router.get("/demandes/statut/{statut}")
async def get_demandes_par_statut(
    statut: str,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """
    Retourne les médecins filtrés par statut.
    Valeurs : en_attente | valide | rejete | suspendu
    GET /api/admin/demandes/statut/rejete
    GET /api/admin/demandes/statut/suspendu
    """
    if statut not in ("en_attente", "valide", "rejete", "suspendu"):
        raise HTTPException(400, f"Statut invalide : {statut}")
    return await AdminService.get_demandes_par_statut(db, statut)


# ── Inscriptions refusées ──────────────────────────────────────────────────────

@router.get("/demandes/refusees")
async def get_demandes_refusees(
    ville:  Optional[str] = None,
    motif:  Optional[str] = None,
    db:     AsyncSession  = Depends(get_db),
    admin:  Admin         = Depends(get_current_admin),
):
    """
    Retourne les médecins avec statut 'rejete'.
    Filtres optionnels : ville, motif.
    GET /api/admin/demandes/refusees?ville=Douala&motif=CNOM invalide
    """
    return await AdminService.get_demandes_refusees(db, ville=ville, motif=motif)


@router.delete("/demandes/{medecin_id}/refusees")
async def supprimer_dossier_refuse(
    medecin_id: str,
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Supprime définitivement un dossier refusé.
    DELETE /api/admin/demandes/{id}/refusees
    """
    return await AdminService.supprimer_dossier_refuse(db, medecin_id)


@router.post("/demandes/{medecin_id}/relancer")
async def relancer_medecin(
    medecin_id: str,
    body:  dict,
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Envoie un e-mail de relance au médecin refusé.
    POST /api/admin/demandes/{id}/relancer
    Body: { "message": "..." }
    """
    return await AdminService.relancer_medecin(
        db,
        medecin_id = medecin_id,
        message    = body.get("message", ""),
        admin_id   = admin.id,
    )


# ── FAQ / Questions admin ───────────────────────────────────────────────────────

class ReponseSchema(BaseModel):
    reponse:      str
    publier_faq:  bool = False


@router.get("/faq/questions")
async def get_questions(
    statut: Optional[str] = None,
    db:     AsyncSession  = Depends(get_db),
    admin:  Admin         = Depends(get_current_admin),
):
    """GET /api/admin/faq/questions?statut=en_attente|repondu|publiee_faq"""
    q = select(QuestionAdmin).order_by(desc(QuestionAdmin.created_at))
    if statut:
        q = q.where(QuestionAdmin.statut == statut)
    result   = await db.execute(q)
    questions = result.scalars().all()

    # Charger les noms des médecins
    medecin_ids = list({qu.medecin_id for qu in questions})
    medecins = {}
    if medecin_ids:
        mr = await db.execute(select(Medecin).where(Medecin.id.in_(medecin_ids)))
        for m in mr.scalars().all():
            medecins[m.id] = f"Dr. {m.prenom} {m.nom}"

    return [
        {
            "id":         qu.id,
            "titre":      qu.titre,
            "message":    qu.message,
            "statut":     qu.statut,
            "reponse":    qu.reponse,
            "medecin_id": qu.medecin_id,
            "medecin":    medecins.get(qu.medecin_id, "Médecin inconnu"),
            "date":       qu.created_at.strftime("%Y-%m-%d %H:%M"),
            "repondu_at": qu.repondu_at.strftime("%Y-%m-%d %H:%M") if qu.repondu_at else None,
        }
        for qu in questions
    ]


@router.patch("/faq/questions/{question_id}/repondre")
async def repondre_question(
    question_id: str,
    body: ReponseSchema,
    db:   AsyncSession = Depends(get_db),
    admin: Admin       = Depends(get_current_admin),
):
    """Répondre à une question et optionnellement la publier en FAQ."""
    q = await db.get(QuestionAdmin, question_id)
    if not q:
        raise HTTPException(404, "Question introuvable")
    q.reponse    = body.reponse.strip()
    q.statut     = "publiee_faq" if body.publier_faq else "repondu"
    q.repondu_at = datetime.utcnow()
    await db.commit()
    return {"message": "Réponse enregistrée", "statut": q.statut}


@router.patch("/faq/questions/{question_id}/publier")
async def publier_faq(
    question_id: str,
    db:   AsyncSession = Depends(get_db),
    admin: Admin       = Depends(get_current_admin),
):
    """Publier une question répondue dans la FAQ publique."""
    q = await db.get(QuestionAdmin, question_id)
    if not q:
        raise HTTPException(404, "Question introuvable")
    if not q.reponse:
        raise HTTPException(422, "Répondez d'abord à la question avant de la publier")
    q.statut = "publiee_faq"
    await db.commit()
    return {"message": "Question publiée en FAQ"}


@router.get("/faq/publiques")
async def get_faq_publiques(db: AsyncSession = Depends(get_db)):
    """FAQ publique — accessible sans authentification."""
    result = await db.execute(
        select(QuestionAdmin)
        .where(QuestionAdmin.statut == "publiee_faq")
        .order_by(desc(QuestionAdmin.repondu_at))
    )
    return [
        {
            "id":      q.id,
            "titre":   q.titre,
            "reponse": q.reponse,
            "date":    q.repondu_at.strftime("%Y-%m-%d") if q.repondu_at else None,
        }
        for q in result.scalars().all()
    ]
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.database import get_db
from app.core.security import get_current_admin, verify_password, create_access_token
from app.models.admin import Admin
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
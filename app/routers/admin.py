from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

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

    # Première connexion — sauvegarder le numéro
    if not admin.phone:
        admin.phone = body.phone
        await db.commit()

    # Connexions suivantes — vérifier que le numéro correspond
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


# ── Demandes médecins ──────────────────────────────────────────────────────────

@router.get("/demandes")
async def get_demandes(
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return await AdminService.get_pending_medics(db)


@router.post("/demandes/{medecin_id}/valider")
async def valider_medecin(
    medecin_id: str,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return await AdminService.validate_medic(db, medecin_id, admin.id)


@router.post("/demandes/{medecin_id}/rejeter")
async def rejeter_medecin(
    medecin_id: str,
    body: RefusRequestSchema,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return await AdminService.reject_medic(db, medecin_id, body.motif)
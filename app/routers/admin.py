# app/routers/admin.py
import traceback
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.database import get_db
from app.models.admin   import Admin
from app.models.medecin import Medecin
from app.core.security  import (verify_password, create_access_token,
                                 generate_activation_token)
from app.core.dependencies import get_current_admin
from app.services.email_service import send_activation_email, send_rejection_email
from app.config import settings

router = APIRouter(prefix="/admin", tags=["Admin"])

# ── Schemas locaux ────────────────────────────────────────────────
class AdminLoginRequest(BaseModel):
    email:    str
    password: str

class RefusRequest(BaseModel):
    motif: str

# ─────────────────────────────────────────────────────────────────
#  GET /api/v1/admin/me  — profil de l'admin connecté
# ─────────────────────────────────────────────────────────────────
@router.get("/me")
async def get_admin_me(
    admin: Admin = Depends(get_current_admin),
):
    """Retourne le profil de l'administrateur authentifié (JWT Bearer)."""
    return {
        "id":    admin.id,
        "nom":   admin.nom,
        "email": admin.email,
    }


# ─────────────────────────────────────────────────────────────────
#  POST /api/v1/admin/login
# ─────────────────────────────────────────────────────────────────
@router.post("/login")
async def admin_login(body: AdminLoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Admin).where(Admin.email == body.email))
    admin  = result.scalar_one_or_none()

    if not admin or not verify_password(body.password, admin.password_hash):
        raise HTTPException(401, "Identifiants incorrects")

    token = create_access_token({"sub": str(admin.id), "role": "admin"})
    return {"access_token": token, "token_type": "bearer"}


# ─────────────────────────────────────────────────────────────────
#  GET /api/v1/admin/demandes  — médecins en attente
# ─────────────────────────────────────────────────────────────────
@router.get("/demandes")
async def get_demandes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Medecin)
        .where(Medecin.statut == "en_attente")
        .order_by(Medecin.created_at.desc())
    )
    medecins = result.scalars().all()
    return [
        {
            "id":            str(m.id),
            "civilite":      m.civilite,
            "nom":           m.nom,
            "prenom":        m.prenom,
            "email":         m.email,
            "specialite":    m.specialite,
            "numero_rpps":   m.numero_rpps,
            "etablissement": m.etablissement,
            "created_at":    m.created_at.isoformat(),
        }
        for m in medecins
    ]


# ─────────────────────────────────────────────────────────────────
#  GET /api/v1/admin/demandes/{id}  — détail + documents
# ─────────────────────────────────────────────────────────────────
@router.get("/demandes/{medecin_id}")
async def get_demande_detail(medecin_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
    select(Medecin)
    .options(selectinload(Medecin.documents))
    .where(Medecin.id == medecin_id)
    )

    m = result.scalar_one_or_none()
    if not m:
        raise HTTPException(404, "Médecin introuvable")

    return {
        "id":            str(m.id),
        "civilite":      m.civilite,
        "nom":           m.nom,
        "prenom":        m.prenom,
        "email":         m.email,
        "specialite":    m.specialite,
        "numero_rpps":   m.numero_rpps,
        "etablissement": m.etablissement,
        "statut":        m.statut,
        "created_at":    m.created_at.isoformat(),
        "documents": [
            {
                "type":     doc.type_document,
                "fichier":  doc.nom_fichier,
                "url":      doc.url_fichier,
                "taille":   doc.taille_octets,
            }
            for doc in m.documents
        ],
    }


# ─────────────────────────────────────────────────────────────────
#  POST /api/v1/admin/demandes/{id}/valider
# ─────────────────────────────────────────────────────────────────
@router.post("/demandes/{medecin_id}/valider")
async def valider_medecin(medecin_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Medecin).where(Medecin.id == medecin_id)
    )
    m = result.scalar_one_or_none()
    if not m:
        raise HTTPException(404, "Médecin introuvable")
    if m.statut != "en_attente":
        raise HTTPException(400, f"Ce médecin est déjà '{m.statut}'")

    # Générer le token d'activation (7 jours)
    token   = generate_activation_token()
    expires = datetime.utcnow() + timedelta(days=7)

    m.statut             = "valide"
    m.activation_token   = token
    m.activation_expires = expires
    m.valide_le          = datetime.utcnow()

    await db.commit()

    lien_activation = f"{settings.FRONTEND_URL}/activation?token={token}"

    # Envoyer email avec lien
    email_ok = False
    try:
        print(f"  Tentative envoi email → {m.email} (FROM: {settings.FROM_EMAIL})")
        await send_activation_email(m.email, m.nom, token)
        email_ok = True
        print(f"  Email envoyé avec succès → {m.email}")
    except Exception as e:
        print(f"  Email ÉCHEC → {m.email}")
        print(f"    Erreur : {e}")
        print(f"    Détail : {traceback.format_exc()}")

    return {
        "message":          f"Dr {m.nom} validé.",
        "email_envoye":     email_ok,
        "email_medecin":    m.email,
        "lien_activation":  lien_activation,
    }


# ─────────────────────────────────────────────────────────────────
#  POST /api/v1/admin/demandes/{id}/rejeter
# ─────────────────────────────────────────────────────────────────
@router.post("/demandes/{medecin_id}/rejeter")
async def rejeter_medecin(
    medecin_id: str,
    body: RefusRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Medecin).where(Medecin.id == medecin_id)
    )
    m = result.scalar_one_or_none()
    if not m:
        raise HTTPException(404, "Médecin introuvable")
    if m.statut != "en_attente":
        raise HTTPException(400, f"Ce médecin est déjà '{m.statut}'")

    m.statut      = "rejete"
    m.motif_rejet = body.motif
    await db.commit()

    # Envoyer email de refus
    try:
        await send_rejection_email(m.email, m.nom, body.motif)
    except Exception as e:
        print(f" Email refus non envoyé : {e}")

    return {"message": f"Dr {m.nom} refusé. Email envoyé."}
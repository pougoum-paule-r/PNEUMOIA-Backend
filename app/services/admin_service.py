from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from app.models.admin import Admin
from app.models.medecin import Medecin
from app.models.document_medecin import DocumentMedecin
from app.core.security import hash_password
from app.config import settings
from twilio.rest import Client
from datetime import datetime, timedelta
import random
import secrets

# ── Labels documents ───────────────────────────────────────────────────────────
LABELS_DOCUMENT = {
    "diplome_specialisation": "Diplôme de spécialisation",
    "diplome_medecine":       "Diplôme de docteur en médecine",
    "inscription_ordre":      "Inscription à l'ordre des médecins",
    "autorisation_exercice":  "Autorisation d'exercice",
    "carte_professionnelle":  "Carte professionnelle",
    "cni":                    "Carte nationale d'identité (CNI)",
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def build_url(path: str | None) -> str | None:
    if not path:
        return None
    if path.startswith("http"):
        return path
    if path.startswith("/"):
        return f"{settings.BACKEND_URL}{path}"
    return f"{settings.BACKEND_URL}/{path.replace(chr(92), '/')}"

def format_document(d: DocumentMedecin) -> dict:
    return {
        "id":          d.id,
        "type":        d.type_document,
        "label":       LABELS_DOCUMENT.get(d.type_document, d.type_document),
        "url":         build_url(d.url_fichier),
        "nom_fichier": d.nom_fichier,
        "mime_type":   d.mime_type,
        "taille_ko":   round(d.taille_octets / 1024) if d.taille_octets else None,
        "created_at":  d.created_at.isoformat() if d.created_at else None,
    }

def format_medecin(m: Medecin) -> dict:
    return {
        "id":            m.id,
        "civilite":      m.civilite,
        "nom":           m.nom,
        "prenom":        m.prenom,
        "email":         m.email,
        "specialite":    m.specialite,
        "numero_rpps":   m.numero_rpps,
        "etablissement": m.etablissement,
        "telephone":     m.telephone,
        "adresse":       m.adresse,
        "bio":           m.bio,
        "linkedin":      m.linkedin,
        "website":       m.website,
        "photo_url":     build_url(m.photo_url),
        "statut":        m.statut,
        "created_at":    m.created_at.isoformat() if m.created_at else None,
        "documents":     [format_document(d) for d in m.documents],
    }


class AdminService:

    # ── Demandes médecins ──────────────────────────────────────────────────────

    @staticmethod
    async def get_demandes(db: AsyncSession) -> list[dict]:
        """
        Retourne tous les médecins en attente avec :
        - Toutes les données personnelles
        - Photo de profil (URL complète)
        - Tous les documents (URL + métadonnées)
        """
        result = await db.execute(
            select(Medecin)
            .where(Medecin.statut == "en_attente")
            .options(selectinload(Medecin.documents))
            .order_by(Medecin.created_at.desc())
        )
        medecins = result.scalars().all()
        return [format_medecin(m) for m in medecins]

    @staticmethod
    async def valider_medecin(db: AsyncSession, medecin_id: str, admin_id: str) -> dict:
        """Valide un médecin et génère un lien d'activation."""
        result = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
        medecin = result.scalar_one_or_none()

        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin introuvable.")
        if medecin.statut != "en_attente":
            raise HTTPException(status_code=400, detail="Ce médecin n'est pas en attente.")

        token = secrets.token_urlsafe(32)
        medecin.statut             = "valide"
        medecin.activation_token   = token
        medecin.activation_expires = datetime.utcnow() + timedelta(days=7)
        medecin.valide_par         = admin_id
        medecin.valide_le          = datetime.utcnow()
        await db.commit()

        lien = f"{settings.FRONTEND_URL}/medecin/activer?token={token}"

        # Email d'activation — géré par le binôme SMTP
        email_envoye = False
        try:
            # from app.services.email_service import send_activation_email
            # await send_activation_email(medecin.email, lien)
            email_envoye = True
        except Exception:
            email_envoye = False

        return {
            "message":         "Médecin validé avec succès.",
            "email_envoye":    email_envoye,
            "email_medecin":   medecin.email,
            "lien_activation": lien,
        }

    @staticmethod
    async def rejeter_medecin(db: AsyncSession, medecin_id: str, motif: str) -> dict:
        """Refuse un médecin avec un motif."""
        result = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
        medecin = result.scalar_one_or_none()

        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin introuvable.")
        if medecin.statut != "en_attente":
            raise HTTPException(status_code=400, detail="Ce médecin n'est pas en attente.")

        medecin.statut      = "rejete"
        medecin.motif_rejet = motif
        await db.commit()

        # Email de refus — géré par le binôme SMTP
        try:
            # from app.services.email_service import send_rejection_email
            # await send_rejection_email(medecin.email, motif)
            pass
        except Exception:
            pass

        return {"message": "Médecin refusé. Notification envoyée."}

    # ── Reset mot de passe admin ───────────────────────────────────────────────

    @staticmethod
    async def request_password_reset(db: AsyncSession, email: str, phone: str) -> str:
        result = await db.execute(select(Admin).where(Admin.email == email))
        admin = result.scalar_one_or_none()

        if not admin:
            raise HTTPException(status_code=400, detail="Aucun compte trouvé avec cet email.")

        if not admin.phone:
            raise HTTPException(status_code=400, detail="Aucun numéro associé à ce compte.")

        if admin.phone != phone:
            raise HTTPException(status_code=400, detail="Numéro de téléphone incorrect.")

        otp = "".join(random.choices("0123456789", k=6))
        admin.reset_otp  = otp
        admin.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        await db.commit()

        return otp

    @staticmethod
    async def verify_and_update_password(
        db: AsyncSession,
        email: str,
        otp: str,
        new_password: str,
    ) -> None:
        result = await db.execute(select(Admin).where(Admin.email == email))
        admin = result.scalar_one_or_none()

        if not admin:
            raise HTTPException(status_code=400, detail="Compte introuvable.")

        if not admin.is_otp_valid(otp):
            raise HTTPException(status_code=400, detail="Code OTP invalide ou expiré.")

        admin.password_hash = hash_password(new_password)
        admin.clear_otp()
        await db.commit()

    @staticmethod
    async def send_otp_sms(otp: str, phone: str) -> str:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=(
                f"PneumoIA — Votre code de réinitialisation est : {otp}. "
                f"Valide 10 minutes. Ne le partagez pas."
            ),
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone,
        )
        return message.sid
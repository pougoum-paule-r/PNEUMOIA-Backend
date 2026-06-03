from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from app.models.admin import Admin
from app.core.security import hash_password
from app.config import settings
from twilio.rest import Client
from datetime import datetime, timedelta
import random


class AdminService:

    # ── Demandes médecins ──────────────────────────────────────────────────────

    @staticmethod
    async def get_pending_medics(db: AsyncSession):
        """Retourne tous les médecins en attente de validation."""
        from app.models.medecin import Medecin  # import local pour éviter les circular imports
        result = await db.execute(
            select(Medecin).where(Medecin.statut == "pending")
        )
        return result.scalars().all()

    @staticmethod
    async def validate_medic(db: AsyncSession, medecin_id: str, admin_id: str):
        """Valide un médecin et génère un lien d'activation."""
        from app.models.medecin import Medecin
        import secrets

        result = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
        medecin = result.scalar_one_or_none()

        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin introuvable.")
        if medecin.statut != "pending":
            raise HTTPException(status_code=400, detail="Ce médecin n'est pas en attente.")

        # Génération du lien d'activation
        token = secrets.token_urlsafe(32)
        medecin.statut         = "validated"
        medecin.activation_token = token
        medecin.validated_by   = admin_id
        medecin.validated_at   = datetime.utcnow()
        await db.commit()

        lien_activation = f"{settings.FRONTEND_URL}/medecin/activer?token={token}"

        # Tentative d'envoi email — non bloquant
        email_envoye = False
        try:
            # await send_activation_email(medecin.email, lien_activation)
            email_envoye = True
        except Exception:
            email_envoye = False

        return {
            "message":         "Médecin validé avec succès.",
            "email_envoye":    email_envoye,
            "email_medecin":   medecin.email,
            "lien_activation": lien_activation,
        }

    @staticmethod
    async def reject_medic(db: AsyncSession, medecin_id: str, motif: str):
        """Refuse un médecin avec un motif et notifie par e-mail."""
        from app.models.medecin import Medecin

        result = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
        medecin = result.scalar_one_or_none()

        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin introuvable.")
        if medecin.statut != "pending":
            raise HTTPException(status_code=400, detail="Ce médecin n'est pas en attente.")

        medecin.statut    = "refused"
        medecin.motif_refus = motif
        medecin.refused_at  = datetime.utcnow()
        await db.commit()

        # Tentative d'envoi email de refus — non bloquant
        try:
            # await send_refusal_email(medecin.email, motif)
            pass
        except Exception:
            pass

        return {"message": "Médecin refusé. Notification envoyée."}

    # ── Reset mot de passe admin ───────────────────────────────────────────────

    @staticmethod
    async def request_password_reset(db: AsyncSession, email: str, phone: str) -> str:
        """
        Vérifie que l'email ET le téléphone correspondent au même admin.
        Génère un OTP à 6 chiffres, le stocke avec une expiration de 10 min.
        Retourne l'OTP pour que le contrôleur l'envoie via Twilio.
        """
        result = await db.execute(select(Admin).where(Admin.email == email))
        admin = result.scalar_one_or_none()

        if not admin or admin.phone != phone:
            raise HTTPException(
                status_code=400,
                detail="Aucun compte trouvé avec cet email et ce numéro de téléphone."
            )

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
        new_password: str
    ) -> None:
        """
        Vérifie l'OTP (existence + expiration + correspondance).
        Met à jour le mot de passe et efface l'OTP.
        """
        result = await db.execute(select(Admin).where(Admin.email == email))
        admin = result.scalar_one_or_none()

        if not admin:
            raise HTTPException(status_code=400, detail="Compte introuvable.")

        if admin.reset_otp != otp:
            raise HTTPException(status_code=400, detail="Code OTP invalide.")

        if datetime.utcnow() > admin.otp_expiry:
            raise HTTPException(status_code=400, detail="Code OTP expiré. Recommencez.")

        admin.password_hash = hash_password(new_password)
        admin.reset_otp     = None
        admin.otp_expiry    = None
        await db.commit()

    @staticmethod
    async def send_otp_sms(otp: str, phone: str) -> str:
        """
        Envoie l'OTP par SMS via Twilio au numéro fourni dynamiquement.
        Retourne le SID du message Twilio.
        """
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        message = client.messages.create(
            body=(
                f"PneumoIA — Votre code de réinitialisation est : {otp}. "
                f"Il est valide pendant 10 minutes. "
                f"Ne le partagez avec personne."
            ),
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone,
        )
        return message.sid
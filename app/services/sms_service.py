from twilio.rest import Client
from fastapi.concurrency import run_in_threadpool
from app.config import settings

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


class NotificationService:

    @staticmethod
    async def notify_admin_new_medecin(nom: str, prenom: str, specialite: str, admin_phone: str):
        def send():
            return client.messages.create(
                body=f"[PneumoIA] Nouvelle inscription : Dr {prenom} {nom} ({specialite}). Connectez-vous pour valider.",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=admin_phone,
            )
        return await run_in_threadpool(send)

    @staticmethod
    async def send_otp_sms(otp: str, phone: str):
        def send():
            return client.messages.create(
                body=f"[PneumoIA] Votre code de réinitialisation est : {otp}. Valide 10 minutes.",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone,
            )
        return await run_in_threadpool(send)


async def notify_admin_new_medecin(nom: str, prenom: str, specialite: str, admin_phone: str):
    return await NotificationService.notify_admin_new_medecin(nom, prenom, specialite, admin_phone)

async def send_otp_sms(otp: str, phone: str):
    return await NotificationService.send_otp_sms(otp, phone)
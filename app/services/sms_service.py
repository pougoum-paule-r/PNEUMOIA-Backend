from twilio.rest import Client
from app.config import settings

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

def notify_admin_new_medecin(nom: str, prenom: str, specialite: str):
    client.messages.create(
        body=(
            f"[PneumoIA] Nouvelle inscription : "
            f"Dr {prenom} {nom} ({specialite}). "
            f"Connectez-vous pour valider le dossier."
        ),
        from_=settings.TWILIO_PHONE_NUMBER,
        to=settings.ADMIN_PHONE
    )
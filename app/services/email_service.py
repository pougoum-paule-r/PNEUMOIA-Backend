import asyncio
import logging
import smtplib
import urllib.request
import json as _json
from email.mime.text        import MIMEText
from email.mime.multipart   import MIMEMultipart
from datetime               import datetime, timedelta
from app.config             import settings

logger = logging.getLogger(__name__)


def _send_via_api(to_email: str, subject: str, html: str) -> None:
    """Envoie via l'API HTTP Brevo — plus rapide que SMTP (file prioritaire)."""
    payload = _json.dumps({
        "sender":      {"name": "PneumoIA", "email": settings.FROM_EMAIL},
        "to":          [{"email": to_email}],
        "subject":     subject,
        "htmlContent": html,
    }).encode()
    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data    = payload,
        headers = {
            "Content-Type": "application/json",
            "api-key":      settings.BREVO_API_KEY,
        },
        method  = "POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        if resp.status not in (200, 201):
            raise RuntimeError(f"Brevo API {resp.status}: {resp.read()}")


def _send_via_smtp(to_email: str, subject: str, html: str) -> None:
    """Envoie via SMTP Brevo — fallback si pas de clé API."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = settings.FROM_EMAIL
    msg["To"]      = to_email
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.FROM_EMAIL, to_email, msg.as_string())


def _send(to_email: str, subject: str, html: str) -> None:
    """Envoie un email HTML. Utilise l'API Brevo si BREVO_API_KEY est défini, sinon SMTP."""
    if settings.BREVO_API_KEY:
        _send_via_api(to_email, subject, html)
    else:
        _send_via_smtp(to_email, subject, html)


async def _send_async(to_email: str, subject: str, html: str) -> None:
    """Wrapper non-bloquant — exécute _send dans un thread pool."""
    await asyncio.to_thread(_send, to_email, subject, html)


# ─── Email de validation du compte ───────────────────────────────────────────
async def send_activation_email(to_email: str, nom: str, token: str) -> None:
    lien   = f"{settings.FRONTEND_URL}/activation?token={token}"
    expiry = (datetime.utcnow() + timedelta(days=7)).strftime("%d/%m/%Y")

    await _send_async(
        to_email = to_email,
        subject  = "PneumoIA — Votre compte a été validé ✅",
        html     = f"""
        <div style="font-family:sans-serif;max-width:500px;margin:auto">
          <h2 style="color:#1d4ed8">Bonjour Dr {nom},</h2>
          <p>Votre dossier a été examiné et <strong>validé</strong> par notre équipe.</p>
          <p>Cliquez sur le bouton ci-dessous pour accéder à votre espace :</p>
          <a href="{lien}"
             style="display:inline-block;background:#2563eb;color:white;
                    padding:12px 28px;border-radius:8px;text-decoration:none;
                    font-weight:bold;margin:16px 0">
            Accéder à mon espace médecin
          </a>
          <p style="color:#6b7280;font-size:13px">
            ⚠️ Ce lien est valable jusqu'au <strong>{expiry}</strong>.<br>
            Après cette date, contactez l'administrateur.
          </p>
        </div>
        """,
    )


# ─── Email de rejet du dossier ───────────────────────────────────────────────
async def send_rejection_email(to_email: str, nom: str, motif: str) -> None:
    await _send_async(
        to_email = to_email,
        subject  = "PneumoIA — Demande d'inscription refusée",
        html     = f"""
        <div style="font-family:sans-serif;max-width:500px;margin:auto">
          <h2 style="color:#dc2626">Bonjour Dr {nom},</h2>
          <p>Après examen de votre dossier, votre demande d'inscription
             n'a pas pu être validée.</p>
          <div style="background:#fef2f2;border-left:4px solid #dc2626;
                      padding:12px 16px;border-radius:4px;margin:16px 0">
            <strong>Motif :</strong> {motif}
          </div>
          <p>Vous pouvez soumettre une nouvelle demande avec des documents corrigés.</p>
        </div>
        """,
    )


# ─── Email OTP (code de connexion) ───────────────────────────────────────────
async def send_otp_email(to_email: str, nom: str, otp: str) -> None:
    await _send_async(
        to_email = to_email,
        subject  = "PneumoIA — Votre code de connexion",
        html     = f"""
        <div style="font-family:sans-serif;max-width:500px;margin:auto">
          <h2 style="color:#1d4ed8">Bonjour Dr {nom},</h2>
          <p>Votre code de connexion à usage unique :</p>
          <div style="font-size:42px;font-weight:bold;color:#2563eb;
                      letter-spacing:10px;margin:24px 0;text-align:center">
            {otp}
          </div>
          <p style="color:#6b7280;font-size:13px">
            ⏱️ Ce code expire dans <strong>5 minutes</strong>.<br>
            Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.
          </p>
        </div>
        """,
    )


# ─── Email OTP reset de mot de passe ─────────────────────────────────────────
async def send_reset_otp_email(to_email: str, nom: str, otp: str) -> None:
    await _send_async(
        to_email = to_email,
        subject  = "PneumoIA — Code de réinitialisation de mot de passe",
        html     = f"""
        <div style="font-family:sans-serif;max-width:500px;margin:auto">
          <h2 style="color:#d97706">Bonjour Dr {nom},</h2>
          <p>Vous avez demandé la réinitialisation de votre mot de passe.</p>
          <p>Votre code à usage unique :</p>
          <div style="font-size:42px;font-weight:bold;color:#d97706;
                      letter-spacing:10px;margin:24px 0;text-align:center;
                      background:#fffbeb;border-radius:12px;padding:16px">
            {otp}
          </div>
          <p style="color:#6b7280;font-size:13px">
            ⏱️ Ce code expire dans <strong>5 minutes</strong>.<br>
            ⚠️ Si vous n'êtes <strong>pas</strong> à l'origine de cette demande,
            ignorez cet email et contactez immédiatement l'administrateur.<br>
            Vous disposez de <strong>3 tentatives</strong> pour entrer ce code.
          </p>
        </div>
        """,
    )


# ─── Alerte piratage → Admin ──────────────────────────────────────────────────
async def send_piratage_admin_email(
    admin_email: str, medecin_nom: str, medecin_email: str,
    medecin_id: str, nb_tentatives: int,
) -> None:
    now = datetime.utcnow().strftime("%d/%m/%Y à %H:%M UTC")
    await _send_async(
        to_email = admin_email,
        subject  = "🚨 PneumoIA — Tentative de piratage de compte détectée",
        html     = f"""
        <div style="font-family:sans-serif;max-width:500px;margin:auto">
          <div style="background:#fef2f2;border-left:4px solid #dc2626;padding:16px;border-radius:8px;margin-bottom:16px">
            <h2 style="color:#dc2626;margin:0 0 8px">⚠️ Alerte de sécurité</h2>
            <p style="margin:0;color:#7f1d1d">
              <strong>{nb_tentatives} tentatives incorrectes</strong> de réinitialisation
              de mot de passe ont été détectées sur un compte médecin.
            </p>
          </div>
          <table style="width:100%;border-collapse:collapse;font-size:14px">
            <tr><td style="padding:8px;color:#6b7280;width:140px">Médecin</td>
                <td style="padding:8px;font-weight:bold">Dr. {medecin_nom}</td></tr>
            <tr style="background:#f9fafb">
                <td style="padding:8px;color:#6b7280">Email</td>
                <td style="padding:8px">{medecin_email}</td></tr>
            <tr><td style="padding:8px;color:#6b7280">Identifiant</td>
                <td style="padding:8px;font-family:monospace">{medecin_id}</td></tr>
            <tr style="background:#f9fafb">
                <td style="padding:8px;color:#6b7280">Date / heure</td>
                <td style="padding:8px">{now}</td></tr>
          </table>
          <p style="color:#6b7280;font-size:13px;margin-top:16px">
            Vérifiez l'activité du compte et contactez le médecin pour confirmer
            qu'il est bien à l'origine de cette demande.
          </p>
        </div>
        """,
    )


# ─── Alerte piratage → Médecin ───────────────────────────────────────────────
async def send_piratage_medecin_email(to_email: str, nom: str) -> None:
    now = datetime.utcnow().strftime("%d/%m/%Y à %H:%M UTC")
    await _send_async(
        to_email = to_email,
        subject  = "🚨 PneumoIA — Activité suspecte sur votre compte",
        html     = f"""
        <div style="font-family:sans-serif;max-width:500px;margin:auto">
          <div style="background:#fef2f2;border-left:4px solid #dc2626;padding:16px;border-radius:8px;margin-bottom:16px">
            <h2 style="color:#dc2626;margin:0 0 8px">⚠️ Alerte de sécurité</h2>
            <p style="margin:0;color:#7f1d1d">
              3 tentatives incorrectes de réinitialisation de mot de passe ont été
              détectées sur votre compte PneumoIA.
            </p>
          </div>
          <p style="color:#374151">Bonjour Dr {nom},</p>
          <p style="color:#374151">
            Le <strong>{now}</strong>, quelqu'un a tenté 3 fois de réinitialiser
            le mot de passe de votre compte sans succès.
          </p>
          <p style="color:#dc2626;font-weight:bold">
            Si ce n'était PAS vous, votre compte est peut-être en danger.
            Contactez immédiatement l'administrateur PneumoIA.
          </p>
          <p style="color:#9ca3af;font-size:12px;margin-top:16px">
            L'administrateur a également été notifié de cette activité suspecte.
          </p>
        </div>
        """,
    )

import asyncio
import logging
import smtplib
import ssl
from datetime import datetime, timedelta
from email.mime.text      import MIMEText
from email.mime.multipart import MIMEMultipart

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def _send_via_api(to_email: str, subject: str, html: str) -> None:
    """Brevo HTTP API — async natif, pas de getaddrinfo thread issue."""
    payload = {
        "sender":      {"name": "PneumoIA", "email": settings.FROM_EMAIL},
        "to":          [{"email": to_email}],
        "subject":     subject,
        "htmlContent": html,
    }
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "api-key":      settings.BREVO_API_KEY,
            },
        )
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Brevo API {r.status_code}: {r.text}")


def _smtp_send_sync(to_email: str, subject: str, html: str) -> None:
    """Envoi SMTP synchrone — appelé via asyncio.to_thread."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = settings.FROM_EMAIL
    msg["To"]      = to_email
    msg.attach(MIMEText(html, "html"))

    ctx = ssl.create_default_context()
    if settings.SMTP_PORT == 465:
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15, context=ctx) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.FROM_EMAIL, to_email, msg.as_string())
    else:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            server.ehlo()
            server.starttls(context=ctx)
            server.ehlo()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.FROM_EMAIL, to_email, msg.as_string())


async def _send_via_smtp(to_email: str, subject: str, html: str) -> None:
    await asyncio.to_thread(_smtp_send_sync, to_email, subject, html)


async def _send(to_email: str, subject: str, html: str) -> None:
    if settings.BREVO_API_KEY:
        await _send_via_api(to_email, subject, html)
    else:
        await _send_via_smtp(to_email, subject, html)


# ─── Email de validation du compte ───────────────────────────────────────────
async def send_activation_email(to_email: str, nom: str, token: str) -> None:
    lien   = f"{settings.FRONTEND_URL}/activation?token={token}"
    expiry = (datetime.utcnow() + timedelta(days=7)).strftime("%d/%m/%Y")

    await _send(
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
    await _send(
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
    await _send(
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
    await _send(
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


# ─── Nouvelle demande d'adhésion médecin → Admin ─────────────────────────────
async def send_nouvelle_demande_admin_email(
    admin_email: str, medecin_nom: str, medecin_prenom: str,
    specialite: str, medecin_id: str,
) -> None:
    lien = f"{settings.FRONTEND_URL}/admin/demandes/{medecin_id}"
    await _send(
        to_email = admin_email,
        subject  = f"PneumoIA — Nouvelle demande d'adhésion : Dr {medecin_prenom} {medecin_nom}",
        html     = f"""
        <div style="font-family:sans-serif;max-width:500px;margin:auto">
          <h2 style="color:#0f766e">Nouvelle demande d'adhésion 🩺</h2>
          <p>Un médecin vient de soumettre une demande d'accès à la plateforme PneumoIA.</p>
          <table style="width:100%;border-collapse:collapse;font-size:14px;margin:16px 0">
            <tr><td style="padding:8px;color:#6b7280;width:140px">Médecin</td>
                <td style="padding:8px;font-weight:bold">Dr {medecin_prenom} {medecin_nom}</td></tr>
            <tr style="background:#f9fafb">
                <td style="padding:8px;color:#6b7280">Spécialité</td>
                <td style="padding:8px">{specialite}</td></tr>
            <tr><td style="padding:8px;color:#6b7280">Identifiant</td>
                <td style="padding:8px;font-family:monospace">{medecin_id}</td></tr>
          </table>
          <a href="{lien}"
             style="display:inline-block;background:#0f766e;color:white;
                    padding:12px 28px;border-radius:8px;text-decoration:none;
                    font-weight:bold;margin:16px 0">
            Examiner la demande
          </a>
          <p style="color:#6b7280;font-size:13px">
            Connectez-vous au tableau de bord administrateur pour valider ou refuser ce dossier.
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
    await _send(
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


# ─── Demande de déblocage → Admin ────────────────────────────────────────────
async def send_deblocage_request_email(
    admin_email: str, medecin_nom: str, medecin_email: str,
    medecin_id: str, raison: str,
) -> None:
    now = datetime.utcnow().strftime("%d/%m/%Y à %H:%M UTC")
    await _send(
        to_email = admin_email,
        subject  = f"PneumoIA — Demande de déblocage : Dr {medecin_nom}",
        html     = f"""
        <div style="font-family:sans-serif;max-width:500px;margin:auto">
          <div style="background:#eff6ff;border-left:4px solid #2563eb;padding:16px;border-radius:8px;margin-bottom:16px">
            <h2 style="color:#1d4ed8;margin:0 0 8px">🔓 Demande de déblocage de compte</h2>
            <p style="margin:0;color:#1e3a5f">
              Un médecin dont le compte a été suspendu automatiquement demande le rétablissement de son accès.
            </p>
          </div>
          <table style="width:100%;border-collapse:collapse;font-size:14px">
            <tr><td style="padding:8px;color:#6b7280;width:140px">Médecin</td>
                <td style="padding:8px;font-weight:bold">Dr. {medecin_nom}</td></tr>
            <tr style="background:#f9fafb">
                <td style="padding:8px;color:#6b7280">Email</td>
                <td style="padding:8px">{medecin_email}</td></tr>
            <tr><td style="padding:8px;color:#6b7280">Identifiant</td>
                <td style="padding:8px;font-family:monospace;font-size:12px">{medecin_id}</td></tr>
            <tr style="background:#f9fafb">
                <td style="padding:8px;color:#6b7280">Motif blocage</td>
                <td style="padding:8px;color:#dc2626">{raison}</td></tr>
            <tr><td style="padding:8px;color:#6b7280">Date demande</td>
                <td style="padding:8px">{now}</td></tr>
          </table>
          <p style="color:#6b7280;font-size:13px;margin-top:16px">
            Connectez-vous au tableau de bord administrateur pour débloquer ce compte si la demande est légitime.
          </p>
        </div>
        """,
    )


# ─── Alerte piratage → Médecin ───────────────────────────────────────────────
async def send_piratage_medecin_email(to_email: str, nom: str, deblocage_link: str = "") -> None:
    now = datetime.utcnow().strftime("%d/%m/%Y à %H:%M UTC")
    btn = (
        f'<div style="text-align:center;margin-top:16px">'
        f'<a href="{deblocage_link}" '
        f'style="display:inline-block;padding:12px 28px;background:#2563eb;color:#fff;'
        f'border-radius:8px;text-decoration:none;font-weight:bold;font-size:15px">'
        f'Contacter l\'administrateur</a>'
        f'<p style="color:#9ca3af;font-size:11px;margin-top:8px">Ce lien est valable 7 jours.</p>'
        f'</div>'
        if deblocage_link else ""
    )
    await _send(
        to_email = to_email,
        subject  = "🚨 PneumoIA — Votre compte a été suspendu",
        html     = f"""
        <div style="font-family:sans-serif;max-width:500px;margin:auto">
          <div style="background:#fef2f2;border-left:4px solid #dc2626;padding:16px;border-radius:8px;margin-bottom:16px">
            <h2 style="color:#dc2626;margin:0 0 8px">⚠️ Compte suspendu</h2>
            <p style="margin:0;color:#7f1d1d">
              Votre compte PneumoIA a été suspendu automatiquement pour des raisons de sécurité.
            </p>
          </div>
          <p style="color:#374151">Bonjour Dr {nom},</p>
          <p style="color:#374151">
            Le <strong>{now}</strong>, plusieurs tentatives incorrectes ont été détectées sur votre compte.
            Par mesure de sécurité, votre accès a été <strong style="color:#dc2626">suspendu automatiquement</strong>.
          </p>
          <div style="background:#fffbeb;border:1px solid #fcd34d;border-radius:8px;padding:14px;margin:16px 0">
            <p style="margin:0;color:#92400e;font-weight:bold">Pour rétablir votre accès :</p>
            <p style="margin:8px 0 0;color:#78350f">
              Cliquez sur le bouton ci-dessous. L'administrateur sera notifié et pourra débloquer votre compte.
            </p>
            {btn}
          </div>
          <p style="color:#9ca3af;font-size:12px;margin-top:16px">
            Si vous êtes à l'origine de ces tentatives, ignorez cet email.
            L'administrateur a également été notifié de cette activité.
          </p>
        </div>
        """,
    )

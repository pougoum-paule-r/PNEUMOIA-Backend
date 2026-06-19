# app/routers/aides.py
import asyncio
import random, string, logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional
from jose import JWTError

from app.database import get_db
from app.models.aide_soignant import AideSoignant, generate_code_referent
from app.models.medecin import Medecin
from app.core.security import hash_password, verify_password, create_access_token, decode_token
from app.config import settings
from app.services.email_service import _send as smtp_send

router = APIRouter(prefix="/aides", tags=["Aides Soignants"])
bearer = HTTPBearer()

# OTP en mémoire pour les aides soignants: aide_id -> (code, expiry)
_aide_otp: dict[str, tuple[str, datetime]] = {}

# ── Schemas ───────────────────────────────────────────────────────
class InscriptionAideRequest(BaseModel):
    nom:           str
    prenom:        str
    email:         str
    telephone:     Optional[str] = None
    password:      str
    code_referent: str

class LoginAideRequest(BaseModel):
    email:    str
    password: str

class VerifyOtpAideRequest(BaseModel):
    aide_id: str
    code:    str

class RefuserAideRequest(BaseModel):
    motif: Optional[str] = None

class PermissionsRequest(BaseModel):
    peut_creer_patient:    bool = True
    peut_lire_dossier:     bool = True
    peut_modifier_patient: bool = True
    peut_saisir_symptomes: bool = True
    peut_supprimer:        bool = False
    peut_voir_diagnostic:  bool = False
    peut_prescrire:        bool = False

class PatientAideCreate(BaseModel):
    civilite:             Optional[str]       = None
    nom:                  str
    prenom:               str
    date_naissance:       Optional[str]       = None
    groupe_sanguin:       Optional[str]       = None
    telephone:            Optional[str]       = None
    email:                Optional[str]       = None
    adresse:              Optional[str]       = None
    profession:           Optional[str]       = None
    religion:             Optional[str]       = None
    personne_a_contacter: Optional[str]       = None
    telephone_urgence:    Optional[str]       = None
    allergies:            Optional[list[str]] = []
    antecedents:          Optional[dict]      = {}

class PatientAideUpdate(BaseModel):
    civilite:             Optional[str]       = None
    nom:                  Optional[str]       = None
    prenom:               Optional[str]       = None
    date_naissance:       Optional[str]       = None
    groupe_sanguin:       Optional[str]       = None
    telephone:            Optional[str]       = None
    email:                Optional[str]       = None
    adresse:              Optional[str]       = None
    profession:           Optional[str]       = None
    religion:             Optional[str]       = None
    personne_a_contacter: Optional[str]       = None
    telephone_urgence:    Optional[str]       = None
    allergies:            Optional[list[str]] = None
    antecedents:          Optional[dict]      = None

class ChangePasswordRequest(BaseModel):
    ancien_password: str
    nouveau_password: str

class PreferencesAideRequest(BaseModel):
    notif_email:        Optional[bool] = None
    notif_systeme:      Optional[bool] = None
    notif_code_referent: Optional[bool] = None
    theme:              Optional[str]  = None   # "light" | "dark"

# ── Helper JWT ────────────────────────────────────────────────────
async def get_medecin_from_token(
    credentials: HTTPAuthorizationCredentials,
    db: AsyncSession
) -> Medecin:
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("role") != "medecin":
            raise HTTPException(403, "Accès réservé aux médecins")
        medecin_id = payload.get("sub")
    except JWTError:
        raise HTTPException(401, "Token invalide")

    result  = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
    medecin = result.scalar_one_or_none()
    if not medecin:
        raise HTTPException(404, "Médecin introuvable")
    return medecin


async def _send_email(to: str, subject: str, html: str, aide: "AideSoignant | None" = None):
    """Envoie un email si notif_email n'est pas désactivé dans les préférences aide."""
    if aide is not None:
        prefs = aide.preferences or {}
        if not prefs.get("notif_email", True):
            logger.warning("Email non envoyé à %s : notif_email désactivé", to)
            return
    try:
        await smtp_send(to, subject, html)
        import sys
        print(f"[EMAIL OK] → {to} : {subject}", file=sys.stderr)
    except Exception as e:
        import sys
        print(f"[EMAIL ERREUR] → {to} : {e}", file=sys.stderr)
        logger.warning("Email non envoyé → %s : %s", to, e)


# ─────────────────────────────────────────────────────────────────
# GET /aides/verifier-code/{code}
# ─────────────────────────────────────────────────────────────────
@router.get("/verifier-code/{code}")
async def verifier_code(code: str, db: AsyncSession = Depends(get_db)):
    result  = await db.execute(
        select(Medecin).where(
            Medecin.code_referent == code.upper(),
            Medecin.code_referent_actif == True
        )
    )
    medecin = result.scalar_one_or_none()
    if not medecin:
        raise HTTPException(404, "Code référent invalide ou désactivé")
    return {
        "valide":    True,
        "medecin":   f"{medecin.civilite or 'Dr'} {medecin.prenom} {medecin.nom}",
        "specialite": medecin.specialite,
    }


# ─────────────────────────────────────────────────────────────────
# POST /aides/inscription
# ─────────────────────────────────────────────────────────────────
@router.post("/inscription", status_code=201)
async def inscription_aide(body: InscriptionAideRequest, db: AsyncSession = Depends(get_db)):
    result  = await db.execute(
        select(Medecin).where(
            Medecin.code_referent == body.code_referent.upper(),
            Medecin.code_referent_actif == True
        )
    )
    medecin = result.scalar_one_or_none()
    if not medecin:
        raise HTTPException(404, "Code référent invalide ou désactivé")

    existing = await db.execute(select(AideSoignant).where(AideSoignant.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Cet email est déjà utilisé par un autre aide soignant")

    existing_med = await db.execute(select(Medecin).where(Medecin.email == body.email))
    if existing_med.scalar_one_or_none():
        raise HTTPException(400, "Cet email est déjà enregistré comme médecin — un même email ne peut pas appartenir aux deux rôles")

    aide = AideSoignant(
        medecin_id    = medecin.id,
        nom           = body.nom,
        prenom        = body.prenom,
        email         = body.email,
        telephone     = body.telephone,
        password_hash = hash_password(body.password),
        statut        = "en_attente",
    )
    db.add(aide)
    await db.flush()

    from app.services.notification_service import push_notif
    await push_notif(
        db,
        dest_id   = medecin.id,
        type_dest = "medecin",
        type_notif= "aide_demande",
        titre     = "Nouvelle demande d'aide soignant",
        message   = f"{body.prenom} {body.nom} ({body.email}) souhaite rejoindre votre équipe.",
        meta      = {"lien": "/medecin/parametres"},
    )
    await db.commit()

    asyncio.create_task(_send_email(
        to      = medecin.email,
        subject = "👥 PneumoIA — Nouvel aide soignant",
        html    = f"""
        <div style="font-family:sans-serif;max-width:500px;margin:auto">
          <h2>Bonjour {medecin.civilite or 'Dr'} {medecin.nom},</h2>
          <p><strong>{body.prenom} {body.nom}</strong> ({body.email})
             souhaite rejoindre votre équipe.</p>
          <p>Connectez-vous à PneumoIA pour valider ou refuser cette demande.</p>
        </div>
        """
    ))

    return {
        "message": f"Demande envoyée à {medecin.civilite or 'Dr'} {medecin.nom}. "
                   f"Vous serez notifié par email dès validation."
    }


# ─────────────────────────────────────────────────────────────────
# POST /aides/login  (étape 1 : email + mot de passe → OTP)
# ─────────────────────────────────────────────────────────────────
@router.post("/login")
async def login_aide(body: LoginAideRequest, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AideSoignant).where(AideSoignant.email == body.email))
    aide   = result.scalar_one_or_none()

    if not aide or not verify_password(body.password, aide.password_hash):
        raise HTTPException(401, "Email ou mot de passe incorrect")

    if aide.statut == "en_attente":
        raise HTTPException(403, "Votre compte est en attente de validation par le médecin")
    if aide.statut == "refuse":
        raise HTTPException(403, "Votre demande a été refusée")
    if aide.statut == "suspendu":
        raise HTTPException(403, "Votre compte est suspendu")

    # Générer et stocker l'OTP
    code   = ''.join(random.choices(string.digits, k=6))
    expiry = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=5)
    _aide_otp[aide.id] = (code, expiry)
    print(f"[OTP] Généré pour {aide.email} | notif_email={( aide.preferences or {}).get('notif_email', True)}", flush=True)

    _html_otp = f"""
        <div style="font-family:sans-serif;max-width:400px;margin:auto">
          <h2>Bonjour {aide.prenom},</h2>
          <p>Votre code de connexion PneumoIA :</p>
          <div style="font-size:32px;font-weight:bold;letter-spacing:8px;
                      text-align:center;padding:16px;background:#f0fdf4;
                      border-radius:12px;color:#059669;margin:16px 0">
            {code}
          </div>
          <p style="color:#6b7280;font-size:13px">Ce code expire dans 5 minutes.</p>
        </div>
        """
    background_tasks.add_task(
        _send_email, aide.email, "🔐 PneumoIA — Code de connexion", _html_otp
    )

    return {"aide_id": aide.id}


# ─────────────────────────────────────────────────────────────────
# POST /aides/verify-otp  (étape 2 : valider l'OTP → token)
# ─────────────────────────────────────────────────────────────────
@router.post("/verify-otp")
async def verify_otp_aide(body: VerifyOtpAideRequest, db: AsyncSession = Depends(get_db)):
    entry = _aide_otp.get(body.aide_id)
    if not entry:
        raise HTTPException(400, "Aucun code OTP en attente. Reconnectez-vous.")

    code, expiry = entry
    if datetime.now(timezone.utc).replace(tzinfo=None) > expiry:
        _aide_otp.pop(body.aide_id, None)
        raise HTTPException(400, "Code OTP expiré. Reconnectez-vous.")

    if body.code != code:
        raise HTTPException(400, "Code OTP incorrect")

    _aide_otp.pop(body.aide_id, None)

    result = await db.execute(select(AideSoignant).where(AideSoignant.id == body.aide_id))
    aide   = result.scalar_one_or_none()
    if not aide:
        raise HTTPException(404, "Aide soignant introuvable")

    token = create_access_token({
        "sub":        aide.id,
        "role":       "aide_soignant",
        "medecin_id": aide.medecin_id,
        "permissions": {
            "peut_creer_patient":    aide.peut_creer_patient,
            "peut_lire_dossier":     aide.peut_lire_dossier,
            "peut_modifier_patient": aide.peut_modifier_patient,
            "peut_saisir_symptomes": aide.peut_saisir_symptomes,
            "peut_supprimer":        aide.peut_supprimer,
            "peut_voir_diagnostic":  aide.peut_voir_diagnostic,
            "peut_prescrire":        aide.peut_prescrire,
        }
    })

    return {
        "access_token": token,
        "token_type":   "bearer",
        "aide": {
            "id":        aide.id,
            "nom":       aide.nom,
            "prenom":    aide.prenom,
            "email":     aide.email,
            "medecin_id": aide.medecin_id,
        },
        "permissions": {
            "peut_creer_patient":    aide.peut_creer_patient,
            "peut_lire_dossier":     aide.peut_lire_dossier,
            "peut_modifier_patient": aide.peut_modifier_patient,
            "peut_saisir_symptomes": aide.peut_saisir_symptomes,
            "peut_supprimer":        aide.peut_supprimer,
            "peut_voir_diagnostic":  aide.peut_voir_diagnostic,
            "peut_prescrire":        aide.peut_prescrire,
        }
    }


# ─────────────────────────────────────────────────────────────────
# GET /aides/mes-aides
# ─────────────────────────────────────────────────────────────────
@router.get("/mes-aides")
async def get_mes_aides(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db)
):
    medecin = await get_medecin_from_token(credentials, db)
    result  = await db.execute(
        select(AideSoignant)
        .where(AideSoignant.medecin_id == medecin.id)
        .order_by(AideSoignant.created_at.desc())
    )
    aides = result.scalars().all()
    return [
        {
            "id":        a.id,
            "nom":       a.nom,
            "prenom":    a.prenom,
            "email":     a.email,
            "telephone": a.telephone,
            "statut":    a.statut,
            "created_at": a.created_at.isoformat(),
            "permissions": {
                "peut_creer_patient":    a.peut_creer_patient,
                "peut_lire_dossier":     a.peut_lire_dossier,
                "peut_modifier_patient": a.peut_modifier_patient,
                "peut_saisir_symptomes": a.peut_saisir_symptomes,
                "peut_supprimer":        a.peut_supprimer,
                "peut_voir_diagnostic":  a.peut_voir_diagnostic,
                "peut_prescrire":        a.peut_prescrire,
            },
        }
        for a in aides
    ]


# ─────────────────────────────────────────────────────────────────
# POST /aides/{aide_id}/valider
# ─────────────────────────────────────────────────────────────────
@router.post("/{aide_id}/valider")
async def valider_aide(
    aide_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db)
):
    medecin = await get_medecin_from_token(credentials, db)
    result  = await db.execute(
        select(AideSoignant).where(
            AideSoignant.id == aide_id,
            AideSoignant.medecin_id == medecin.id
        )
    )
    aide = result.scalar_one_or_none()
    if not aide:
        raise HTTPException(404, "Aide soignant introuvable")

    aide.statut = "actif"
    await db.flush()

    from app.services.notification_service import push_notif
    await push_notif(
        db,
        dest_id   = aide.id,
        type_dest = "aide_soignant",
        type_notif= "validation",
        titre     = "Compte validé",
        message   = f"{medecin.civilite or 'Dr'} {medecin.prenom} {medecin.nom} a approuvé votre compte. Vous pouvez maintenant accéder à toutes vos fonctionnalités.",
        meta      = {"lien": "/aide/dashboard"},
    )

    await db.commit()

    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
    asyncio.create_task(_send_email(
        to      = aide.email,
        subject = "✅ PneumoIA — Votre compte aide soignant est activé",
        html    = f"""
        <div style="font-family:sans-serif;max-width:500px;margin:auto">
          <h2>Bonjour {aide.prenom},</h2>
          <p>{medecin.civilite or 'Dr'} {medecin.nom} a validé votre compte.</p>
          <p>Vous pouvez maintenant vous connecter à PneumoIA.</p>
          <a href="{frontend_url}/aide/login"
             style="background:#2563eb;color:white;padding:12px 24px;
                    border-radius:8px;text-decoration:none;display:inline-block">
            Se connecter
          </a>
        </div>
        """,
        aide    = aide,
    ))

    return {"message": f"{aide.prenom} {aide.nom} validé avec succès"}


# ─────────────────────────────────────────────────────────────────
# POST /aides/{aide_id}/refuser
# ─────────────────────────────────────────────────────────────────
@router.post("/{aide_id}/refuser")
async def refuser_aide(
    aide_id: str,
    body:    RefuserAideRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db)
):
    medecin = await get_medecin_from_token(credentials, db)
    result  = await db.execute(
        select(AideSoignant).where(
            AideSoignant.id == aide_id,
            AideSoignant.medecin_id == medecin.id
        )
    )
    aide = result.scalar_one_or_none()
    if not aide:
        raise HTTPException(404, "Aide soignant introuvable")

    aide.statut = "refuse"
    await db.commit()

    motif_html = f"<p><strong>Motif :</strong> {body.motif}</p>" if body.motif else ""
    asyncio.create_task(_send_email(
        to      = aide.email,
        subject = "❌ PneumoIA — Demande de rejoindre une équipe refusée",
        html    = f"""
        <div style="font-family:sans-serif;max-width:500px;margin:auto">
          <h2>Bonjour {aide.prenom},</h2>
          <p>{medecin.civilite or 'Dr'} {medecin.nom} n'a pas pu accepter votre demande.</p>
          {motif_html}
          <p style="color:#6b7280;font-size:13px">
            Si vous pensez qu'il s'agit d'une erreur, contactez directement le médecin.
          </p>
        </div>
        """,
        aide    = aide,
    ))

    return {"message": f"Demande de {aide.prenom} {aide.nom} refusée"}


# ─────────────────────────────────────────────────────────────────
# PUT /aides/{aide_id}/permissions
# ─────────────────────────────────────────────────────────────────
@router.put("/{aide_id}/permissions")
async def modifier_permissions(
    aide_id: str,
    body: PermissionsRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db)
):
    medecin = await get_medecin_from_token(credentials, db)
    result  = await db.execute(
        select(AideSoignant).where(
            AideSoignant.id == aide_id,
            AideSoignant.medecin_id == medecin.id
        )
    )
    aide = result.scalar_one_or_none()
    if not aide:
        raise HTTPException(404, "Aide soignant introuvable")

    aide.peut_creer_patient    = body.peut_creer_patient
    aide.peut_lire_dossier     = body.peut_lire_dossier
    aide.peut_modifier_patient = body.peut_modifier_patient
    aide.peut_saisir_symptomes = body.peut_saisir_symptomes
    aide.peut_supprimer        = body.peut_supprimer
    aide.peut_voir_diagnostic  = body.peut_voir_diagnostic
    aide.peut_prescrire        = body.peut_prescrire
    await db.flush()

    from app.services.notification_service import push_notif
    await push_notif(
        db,
        dest_id   = aide.id,
        type_dest = "aide_soignant",
        type_notif= "permission",
        titre     = "Permissions mises à jour",
        message   = f"{medecin.civilite or 'Dr'} {medecin.prenom} {medecin.nom} a modifié vos permissions d'accès à la plateforme.",
        meta      = {"lien": "/aide/parametres"},
    )

    await db.commit()
    return {"message": "Permissions mises à jour"}


# ─────────────────────────────────────────────────────────────────
# DELETE /aides/{aide_id}
# ─────────────────────────────────────────────────────────────────
@router.delete("/{aide_id}")
async def supprimer_aide(
    aide_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db)
):
    medecin = await get_medecin_from_token(credentials, db)
    result  = await db.execute(
        select(AideSoignant).where(
            AideSoignant.id == aide_id,
            AideSoignant.medecin_id == medecin.id
        )
    )
    aide = result.scalar_one_or_none()
    if not aide:
        raise HTTPException(404, "Aide soignant introuvable")

    await db.delete(aide)
    await db.commit()
    return {"message": f"{aide.prenom} {aide.nom} retiré de votre équipe"}


# ─────────────────────────────────────────────────────────────────
# GET /aides/code-referent
# ─────────────────────────────────────────────────────────────────
@router.get("/code-referent")
async def get_code_referent(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db)
):
    medecin = await get_medecin_from_token(credentials, db)
    return {
        "code_referent": medecin.code_referent,
        "actif":         medecin.code_referent_actif,
    }


# ─────────────────────────────────────────────────────────────────
# POST /aides/code-referent/regenerer
# ─────────────────────────────────────────────────────────────────
@router.post("/code-referent/regenerer")
async def regenerer_code(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db)
):
    medecin = await get_medecin_from_token(credentials, db)

    while True:
        nouveau_code = generate_code_referent()
        existing = await db.execute(
            select(Medecin).where(Medecin.code_referent == nouveau_code)
        )
        if not existing.scalar_one_or_none():
            break

    medecin.code_referent = nouveau_code
    await db.flush()

    # Notifier tous les aides actifs du changement de code
    aides_result = await db.execute(
        select(AideSoignant).where(
            AideSoignant.medecin_id == medecin.id,
            AideSoignant.statut == "actif"
        )
    )
    aides_actifs = aides_result.scalars().all()

    from app.services.notification_service import push_notif
    for aide in aides_actifs:
        await push_notif(
            db,
            dest_id   = aide.id,
            type_dest = "aide_soignant",
            type_notif= "code_referent",
            titre     = "Code référent mis à jour",
            message   = f"{medecin.civilite or 'Dr'} {medecin.prenom} {medecin.nom} a régénéré son code référent. Votre accès reste actif.",
            meta      = {"lien": "/aide/parametres"},
        )

    await db.commit()

    for aide in aides_actifs:
        asyncio.create_task(_send_email(
            to      = aide.email,
            subject = "🔄 PneumoIA — Code référent mis à jour",
            html    = f"""
            <div style="font-family:sans-serif;max-width:500px;margin:auto">
              <h2 style="color:#dc2626">Bonjour {aide.prenom},</h2>
              <p>{medecin.civilite or 'Dr'} {medecin.nom} a régénéré son code référent.</p>
              <p>Votre accès reste actif. Ce changement concerne uniquement les nouvelles inscriptions.</p>
              <p style="color:#6b7280;font-size:13px">Si vous avez des questions, contactez directement votre médecin référent.</p>
            </div>
            """,
            aide    = aide,
        ))

    return {
        "message":       "Code référent régénéré avec succès",
        "code_referent": nouveau_code
    }


# ── Helper: récupérer l'aide depuis le token ──────────────────────
async def get_current_aide(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> AideSoignant:
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("role") != "aide_soignant":
            raise HTTPException(403, "Accès réservé aux aides soignants")
        aide_id = payload.get("sub")
    except JWTError:
        raise HTTPException(401, "Token invalide")

    result = await db.execute(select(AideSoignant).where(AideSoignant.id == aide_id))
    aide   = result.scalar_one_or_none()
    if not aide:
        raise HTTPException(404, "Aide soignant introuvable")
    if aide.statut != "actif":
        raise HTTPException(403, f"Compte non autorisé (statut : {aide.statut})")
    return aide


# ─────────────────────────────────────────────────────────────────
# GET /aides/patients — Liste des patients du médecin référent
# ─────────────────────────────────────────────────────────────────
@router.get("/patients")
async def get_patients_aide(
    aide: AideSoignant = Depends(get_current_aide),
    db:   AsyncSession  = Depends(get_db),
):
    if not (aide.peut_lire_dossier or aide.peut_creer_patient or aide.peut_modifier_patient):
        raise HTTPException(403, "Vous n'avez pas les permissions pour accéder aux patients")

    from app.models.patient import Patient
    result = await db.execute(
        select(Patient)
        .where(Patient.aide_id == aide.id)
        .where(Patient.deleted_at.is_(None))
        .order_by(Patient.nom)
    )
    patients = result.scalars().all()
    return [
        {
            "id":             p.id,
            "nom":            p.nom,
            "prenom":         p.prenom,
            "civilite":       p.civilite,
            "date_naissance": p.date_naissance.isoformat() if p.date_naissance else None,
            "groupe_sanguin": p.groupe_sanguin,
            "telephone":      p.telephone,
            "email":          p.email,
            "adresse":        p.adresse,
            "created_at":     p.created_at.isoformat() + "Z" if p.created_at else None,
        }
        for p in patients
    ]


# ─────────────────────────────────────────────────────────────────
# POST /aides/patients — Créer un patient (via aide soignant)
# ─────────────────────────────────────────────────────────────────
@router.post("/patients", status_code=201)
async def creer_patient_aide(
    body: PatientAideCreate,
    aide: AideSoignant = Depends(get_current_aide),
    db:   AsyncSession  = Depends(get_db),
):
    if not aide.peut_creer_patient:
        raise HTTPException(403, "Vous n'avez pas la permission de créer des patients")

    from app.models.patient import Patient
    from datetime import date

    dob = None
    if body.date_naissance:
        try:
            dob = date.fromisoformat(body.date_naissance)
        except ValueError:
            dob = None

    sexe = "M" if body.civilite == "M" else "F" if body.civilite == "Mme" else None

    patient = Patient(
        nom                  = body.nom.upper().strip(),
        prenom               = body.prenom.strip(),
        civilite             = body.civilite,
        sexe                 = sexe,
        date_naissance       = dob,
        groupe_sanguin       = body.groupe_sanguin,
        telephone            = body.telephone,
        email                = body.email,
        adresse              = body.adresse,
        profession           = body.profession,
        religion             = body.religion,
        personne_a_contacter = body.personne_a_contacter,
        telephone_urgence    = body.telephone_urgence,
        allergies            = body.allergies or [],
        antecedents          = body.antecedents or {},
        created_by           = aide.medecin_id,
        aide_id              = aide.id,
        created_by_aide      = aide.id,
    )
    db.add(patient)
    await db.flush()

    from app.services.notification_service import push_notif
    from app.models.medecin import Medecin
    medecin = await db.get(Medecin, aide.medecin_id) if aide.medecin_id else None

    if aide.medecin_id:
        await push_notif(
            db,
            dest_id   = aide.medecin_id,
            type_dest = "medecin",
            type_notif= "aide_nouveau_patient",
            titre     = "Nouveau patient créé",
            message   = f"{aide.prenom} {aide.nom} a créé le dossier de {body.prenom} {body.nom.upper()}.",
            meta      = {"lien": "/medecin/patients"},
            force     = True,
        )

    await db.commit()
    await db.refresh(patient)

    # Email au médecin référent
    if medecin and medecin.email:
        import asyncio
        asyncio.create_task(_send_email(
            to      = medecin.email,
            subject = "🩺 PneumoIA — Nouveau patient créé par votre aide soignant",
            html    = f"""
            <div style="font-family:sans-serif;max-width:500px;margin:auto">
              <h2 style="color:#2563EB">Nouveau dossier patient</h2>
              <p>Bonjour {medecin.civilite or 'Dr'} {medecin.prenom} {medecin.nom},</p>
              <p><strong>{aide.prenom} {aide.nom}</strong> (aide soignant) a créé un nouveau dossier patient :</p>
              <div style="background:#f0f4ff;padding:12px;border-radius:8px;margin:12px 0">
                <p style="margin:0;font-size:16px;font-weight:bold">{body.prenom} {body.nom.upper()}</p>
              </div>
              <p>Connectez-vous à PneumoIA pour consulter le dossier.</p>
              <p style="color:#6b7280;font-size:13px">Cet email a été généré automatiquement.</p>
            </div>
            """,
        ))
    return {
        "id":     patient.id,
        "nom":    patient.nom,
        "prenom": patient.prenom,
        "message": "Patient créé avec succès"
    }


# ─────────────────────────────────────────────────────────────────
# GET /aides/me — Profil de l'aide connecté
# ─────────────────────────────────────────────────────────────────
@router.get("/me")
async def get_profil_aide(
    aide: AideSoignant = Depends(get_current_aide),
):
    return {
        "id":        aide.id,
        "nom":       aide.nom,
        "prenom":    aide.prenom,
        "email":     aide.email,
        "telephone": aide.telephone,
        "statut":    aide.statut,
        "medecin_id": aide.medecin_id,
        "permissions": {
            "peut_creer_patient":    aide.peut_creer_patient,
            "peut_lire_dossier":     aide.peut_lire_dossier,
            "peut_modifier_patient": aide.peut_modifier_patient,
            "peut_saisir_symptomes": aide.peut_saisir_symptomes,
            "peut_supprimer":        aide.peut_supprimer,
            "peut_voir_diagnostic":  aide.peut_voir_diagnostic,
            "peut_prescrire":        aide.peut_prescrire,
        }
    }


# ─────────────────────────────────────────────────────────────────
# PATCH /aides/me — Mettre à jour le profil
# ─────────────────────────────────────────────────────────────────
class UpdateProfilAideRequest(BaseModel):
    prenom:    Optional[str] = None
    nom:       Optional[str] = None
    telephone: Optional[str] = None

@router.patch("/me")
async def update_profil_aide(
    body: UpdateProfilAideRequest,
    aide: AideSoignant = Depends(get_current_aide),
    db:   AsyncSession  = Depends(get_db),
):
    if body.prenom    is not None: aide.prenom    = body.prenom.strip()
    if body.nom       is not None: aide.nom       = body.nom.strip()
    if body.telephone is not None: aide.telephone = body.telephone.strip() or None
    await db.commit()
    await db.refresh(aide)
    return {
        "id":        aide.id,
        "nom":       aide.nom,
        "prenom":    aide.prenom,
        "email":     aide.email,
        "telephone": aide.telephone,
        "statut":    aide.statut,
    }


# ─────────────────────────────────────────────────────────────────
# PATCH /aides/me/password — Changer le mot de passe
# ─────────────────────────────────────────────────────────────────
@router.patch("/me/password")
async def changer_password_aide(
    body: ChangePasswordRequest,
    aide: AideSoignant = Depends(get_current_aide),
    db:   AsyncSession  = Depends(get_db),
):
    if not verify_password(body.ancien_password, aide.password_hash):
        raise HTTPException(400, "Mot de passe actuel incorrect")
    if len(body.nouveau_password) < 6:
        raise HTTPException(400, "Le nouveau mot de passe doit faire au moins 6 caractères")

    aide.password_hash = hash_password(body.nouveau_password)
    await db.flush()

    from app.services.notification_service import push_notif
    await push_notif(
        db,
        dest_id   = aide.id,
        type_dest = "aide_soignant",
        type_notif= "parametres",
        titre     = "Mot de passe modifié",
        message   = "Votre mot de passe a été modifié avec succès. Si vous n'êtes pas à l'origine de cette action, contactez votre médecin référent.",
        meta      = {"lien": "/aide/parametres"},
    )
    await db.commit()
    return {"message": "Mot de passe modifié avec succès"}


# ─────────────────────────────────────────────────────────────────
# GET /aides/me/preferences — Lire les préférences
# ─────────────────────────────────────────────────────────────────
_PREFS_DEFAULTS = {
    "notif_email":         True,
    "notif_systeme":       True,
    "notif_code_referent": True,
    "theme":               "light",
}

@router.get("/me/preferences")
async def get_preferences_aide(
    aide: AideSoignant = Depends(get_current_aide),
):
    stored = aide.preferences or {}
    return {**_PREFS_DEFAULTS, **stored}


# ─────────────────────────────────────────────────────────────────
# PATCH /aides/me/preferences — Mettre à jour les préférences
# ─────────────────────────────────────────────────────────────────
@router.patch("/me/preferences")
async def update_preferences_aide(
    body: PreferencesAideRequest,
    aide: AideSoignant = Depends(get_current_aide),
    db:   AsyncSession  = Depends(get_db),
):
    current = dict(aide.preferences or {})
    updates = body.model_dump(exclude_none=True)
    current.update(updates)
    aide.preferences = current
    # Force SQLAlchemy à détecter le changement sur un champ JSONB
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(aide, "preferences")
    await db.commit()
    return {**_PREFS_DEFAULTS, **current}


# ─────────────────────────────────────────────────────────────────
# GET /aides/patients/{patient_id} — Détail d'un patient
# ─────────────────────────────────────────────────────────────────
@router.get("/patients/{patient_id}")
async def get_patient_aide(
    patient_id: str,
    aide: AideSoignant = Depends(get_current_aide),
    db:   AsyncSession  = Depends(get_db),
):
    if not (aide.peut_lire_dossier or aide.peut_modifier_patient):
        raise HTTPException(403, "Vous n'avez pas les permissions pour lire les dossiers")

    from app.models.patient import Patient
    result = await db.execute(
        select(Patient).where(
            Patient.aide_id == aide.id,
            Patient.id == patient_id,
            Patient.deleted_at.is_(None)
        )
    )
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(404, "Patient introuvable")

    return {
        "id":                  patient.id,
        "nom":                 patient.nom,
        "prenom":              patient.prenom,
        "civilite":            patient.civilite,
        "date_naissance":      patient.date_naissance.isoformat() if patient.date_naissance else None,
        "groupe_sanguin":      patient.groupe_sanguin,
        "telephone":           patient.telephone,
        "email":               patient.email,
        "adresse":             patient.adresse,
        "profession":          patient.profession,
        "religion":            patient.religion,
        "personne_a_contacter": patient.personne_a_contacter,
        "telephone_urgence":   patient.telephone_urgence,
        "allergies":           patient.allergies or [],
        "antecedents":         patient.antecedents or {},
        "created_at":          patient.created_at.isoformat(),
    }


# ─────────────────────────────────────────────────────────────────
# PATCH /aides/patients/{patient_id} — Modifier un patient
# ─────────────────────────────────────────────────────────────────
@router.patch("/patients/{patient_id}")
async def modifier_patient_aide(
    patient_id: str,
    body: PatientAideUpdate,
    aide: AideSoignant = Depends(get_current_aide),
    db:   AsyncSession  = Depends(get_db),
):
    if not aide.peut_modifier_patient:
        raise HTTPException(403, "Vous n'avez pas la permission de modifier les patients")

    from app.models.patient import Patient
    from datetime import date as date_type
    result = await db.execute(
        select(Patient).where(
            Patient.aide_id == aide.id,
            Patient.id == patient_id,
            Patient.deleted_at.is_(None)
        )
    )
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(404, "Patient introuvable")

    if body.nom is not None:              patient.nom                  = body.nom.upper().strip()
    if body.prenom is not None:           patient.prenom               = body.prenom.strip()
    if body.civilite is not None:         patient.civilite             = body.civilite
    if body.groupe_sanguin is not None:   patient.groupe_sanguin       = body.groupe_sanguin
    if body.telephone is not None:        patient.telephone            = body.telephone
    if body.email is not None:            patient.email                = body.email
    if body.adresse is not None:          patient.adresse              = body.adresse
    if body.profession is not None:       patient.profession           = body.profession
    if body.religion is not None:         patient.religion             = body.religion
    if body.personne_a_contacter is not None: patient.personne_a_contacter = body.personne_a_contacter
    if body.telephone_urgence is not None:    patient.telephone_urgence    = body.telephone_urgence
    if body.allergies is not None:        patient.allergies            = body.allergies
    if body.antecedents is not None:      patient.antecedents          = body.antecedents
    if body.date_naissance is not None:
        try:
            patient.date_naissance = date_type.fromisoformat(body.date_naissance)
        except ValueError:
            pass

    await db.flush()

    from app.services.notification_service import push_notif
    await push_notif(
        db,
        dest_id   = aide.medecin_id,
        type_dest = "medecin",
        type_notif= "aide_modif_patient",
        titre     = "Dossier patient modifié",
        message   = f"{aide.prenom} {aide.nom} a modifié le dossier de {patient.prenom} {patient.nom}.",
        meta      = {"lien": "/medecin/patients"},
    )

    await db.commit()
    await db.refresh(patient)
    return {"message": "Patient modifié avec succès", "id": patient.id}


# ═══════════════════════════════════════════════════════════════════
# CONSULTATIONS — endpoints aide soignant
# (utilisent aide.medecin_id comme médecin responsable)
# ═══════════════════════════════════════════════════════════════════

class ConsultationAideCreate(BaseModel):
    patient_id: str

@router.post("/consultations", status_code=201)
async def creer_consultation_aide(
    body: ConsultationAideCreate,
    aide: AideSoignant = Depends(get_current_aide),
    db:   AsyncSession  = Depends(get_db),
):
    if not (aide.peut_saisir_symptomes or aide.peut_voir_diagnostic):
        raise HTTPException(403, "Vous n'avez pas la permission de créer des consultations")

    from app.models.patient import Patient
    patient = await db.execute(
        select(Patient).where(
            Patient.aide_id == aide.id,
            Patient.id      == body.patient_id,
            Patient.deleted_at.is_(None),
        )
    )
    patient = patient.scalar_one_or_none()
    if not patient:
        raise HTTPException(404, "Patient introuvable ou non autorisé")

    from app.models.consultation import Consultation

    # Idempotence : si une consultation en_attente sans diagnostic existe déjà, la réutiliser
    existing = await db.execute(
        select(Consultation)
        .where(
            Consultation.patient_id  == body.patient_id,
            Consultation.medecin_id  == aide.medecin_id,
            Consultation.statut      == "en_attente",
        )
        .options(selectinload(Consultation.diagnostic))
        .order_by(Consultation.created_at.desc())
        .limit(1)
    )
    existing_c = existing.scalar_one_or_none()
    if existing_c and existing_c.diagnostic is None:
        return {"id": existing_c.id, "patient_id": existing_c.patient_id, "statut": existing_c.statut}

    c = Consultation(
        patient_id    = body.patient_id,
        medecin_id    = aide.medecin_id,
        symptomes     = {},
        prescriptions = {},
        partage       = {},
        statut        = "en_attente",
    )
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return {"id": c.id, "patient_id": c.patient_id, "statut": c.statut}


class AntecedentsAideIn(BaseModel):
    diabete: Optional[bool] = None
    hypertension: Optional[bool] = None
    asthme: Optional[bool] = None
    bpco: Optional[bool] = None
    tuberculose: Optional[bool] = None
    vih: Optional[bool] = None
    typhoide: Optional[bool] = None
    paludisme: Optional[bool] = None
    covid19: Optional[bool] = None
    hepatite_b: Optional[bool] = None
    hepatite_c: Optional[bool] = None
    cancer_poumon: Optional[bool] = None
    traitement_en_cours: Optional[str] = None
    allergie_medicaments: Optional[str] = None
    tabagisme: Optional[str] = None
    cigarettes_par_jour: Optional[int] = None
    duree_tabagisme: Optional[int] = None
    alcool: Optional[bool] = None
    profession_risque: Optional[bool] = None
    exposition_professionnelle: Optional[str] = None

    class Config:
        extra = "allow"

@router.patch("/consultations/{consultation_id}/antecedents", status_code=200)
async def sauvegarder_antecedents_aide(
    consultation_id: str,
    body: AntecedentsAideIn,
    aide: AideSoignant = Depends(get_current_aide),
    db:   AsyncSession  = Depends(get_db),
):
    from app.models.consultation import Consultation
    from app.models.patient import Patient
    c = await db.get(Consultation, consultation_id)
    if not c or c.medecin_id != aide.medecin_id:
        raise HTTPException(404, "Consultation introuvable")

    # Vérifier que le patient appartient à cet aide
    patient = await db.execute(
        select(Patient).where(Patient.aide_id == aide.id, Patient.id == c.patient_id)
    )
    if not patient.scalar_one_or_none():
        raise HTTPException(403, "Accès refusé")

    data = body.model_dump(exclude_none=True)
    c.antecedents_consultation = data
    patient_obj = await db.get(Patient, c.patient_id)
    if patient_obj:
        patient_obj.antecedents = data
    await db.commit()
    return {"message": "Antécédents sauvegardés"}


class SymptomesAideIn(BaseModel):
    class Config:
        extra = "allow"

@router.patch("/consultations/{consultation_id}/symptomes", status_code=200)
async def sauvegarder_symptomes_aide(
    consultation_id: str,
    body: SymptomesAideIn,
    aide: AideSoignant = Depends(get_current_aide),
    db:   AsyncSession  = Depends(get_db),
):
    if not aide.peut_saisir_symptomes and not aide.peut_voir_diagnostic:
        raise HTTPException(403, "Permission refusée")

    from app.models.consultation import Consultation
    from app.models.patient import Patient
    c = await db.get(Consultation, consultation_id)
    if not c or c.medecin_id != aide.medecin_id:
        raise HTTPException(404, "Consultation introuvable")

    patient = await db.execute(
        select(Patient).where(Patient.aide_id == aide.id, Patient.id == c.patient_id)
    )
    if not patient.scalar_one_or_none():
        raise HTTPException(403, "Accès refusé")

    c.symptomes = body.model_dump(exclude_none=True)
    await db.commit()
    return {"message": "Symptômes sauvegardés"}

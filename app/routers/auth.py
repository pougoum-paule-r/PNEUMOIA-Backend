import asyncio, os, shutil, uuid, random, string
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.medecin          import Medecin
from app.models.aide_soignant    import AideSoignant
from app.models.document_medecin import DocumentMedecin
from app.models.otp              import OTPCode
from app.models.admin            import Admin
from app.models.notification     import Notification
from app.schemas.auth            import (LoginRequest, OTPVerifyRequest,
                                          TokenResponse, MessageResponse)
from app.core.security           import (hash_password, verify_password,
                                          create_access_token,
                                          generate_activation_token,
                                          generate_otp)
from app.core.security import get_current_medecin, decode_token
from sqlalchemy        import update as sa_update
from jose              import JWTError
from app.services.email_service  import (
    send_otp_email, send_reset_otp_email,
    send_piratage_admin_email, send_piratage_medecin_email,
    send_nouvelle_demande_admin_email,
)
from app.services.sms_service    import notify_admin_new_medecin
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])

# ── Constantes ────────────────────────────────────────────────
UPLOAD_DIR          = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

PHOTO_MAX_SIZE      = 2 * 1024 * 1024          # 2 Mo
DOCUMENT_MAX_SIZE   = 5 * 1024 * 1024          # 5 Mo
PHOTO_TYPES_AUTORISES  = {"image/jpeg", "image/png", "image/webp"}

def generate_doc_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

def valider_photo(photo: UploadFile):
    """Vérifie type et taille de la photo de profil."""
    if photo.content_type not in PHOTO_TYPES_AUTORISES:
        raise HTTPException(
            400,
            f"Format photo non accepté : {photo.content_type}. "
            f"Acceptés : JPG, PNG, WEBP"
        )
    # Lire pour vérifier la taille
    contenu = photo.file.read()
    if len(contenu) > PHOTO_MAX_SIZE:
        raise HTTPException(
            400,
            f"Photo trop lourde ({len(contenu)//1024} Ko). Maximum : 2 Mo"
        )
    # Remettre le curseur au début pour la sauvegarde
    photo.file.seek(0)
    return contenu

def valider_document(fichier: UploadFile, nom_doc: str):
    """Vérifie uniquement la taille d'un document (toutes extensions acceptées)."""
    contenu = fichier.file.read()
    if len(contenu) > DOCUMENT_MAX_SIZE:
        raise HTTPException(
            400,
            f"Fichier '{nom_doc}' trop lourd ({len(contenu)//1024} Ko). Maximum : 5 Mo"
        )
    fichier.file.seek(0)
    return contenu


# ─────────────────────────────────────────────────────────────
#  POST /api/v1/auth/register
# ─────────────────────────────────────────────────────────────
@router.post("/register", response_model=MessageResponse, status_code=201)
async def register(
    # ── Champs texte ──
    civilite:      str = Form(...),
    nom:           str = Form(...),
    prenom:        str = Form(...),
    specialite:    str = Form(...),
    numero_rpps:   str = Form(...),
    etablissement: str = Form(""),
    telephone:     str | None = Form(None),
    adresse:       str | None = Form(None),
    bio:           str | None = Form(None),
    linkedin:      str | None = Form(None),
    website:       str | None = Form(None),
    email:         str = Form(...),
    password:      str = Form(...),
    # ── Photo de profil (obligatoire) ──
    photo_profil:           UploadFile = File(...),
    # ── 6 documents obligatoires ──
    diplome_specialisation: UploadFile = File(...),
    diplome_medecine:       UploadFile = File(...),
    inscription_ordre:      UploadFile = File(...),
    autorisation_exercice:  UploadFile = File(...),
    carte_professionnelle:  UploadFile = File(...),
    cni:                    UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    # ── 1. Vérifications unicité ──────────────────────────────
    existing_email = await db.execute(
        select(Medecin).where(Medecin.email == email)
    )
    if existing_email.scalar_one_or_none():
        raise HTTPException(400, "Cet email est déjà utilisé")

    existing_aide_email = await db.execute(
        select(AideSoignant).where(AideSoignant.email == email)
    )
    if existing_aide_email.scalar_one_or_none():
        raise HTTPException(400, "Cet email est déjà enregistré comme aide soignant — un même email ne peut pas appartenir aux deux rôles")

    existing_rpps = await db.execute(
        select(Medecin).where(Medecin.numero_rpps == numero_rpps)
    )
    if existing_rpps.scalar_one_or_none():
        raise HTTPException(400, "Ce numéro RPPS est déjà enregistré")

    # ── 2. Validation photo + documents (taille & type) ───────
    valider_photo(photo_profil)

    documents_a_sauvegarder = {
        "diplome_specialisation": diplome_specialisation,
        "diplome_medecine":       diplome_medecine,
        "inscription_ordre":      inscription_ordre,
        "autorisation_exercice":  autorisation_exercice,
        "carte_professionnelle":  carte_professionnelle,
        "cni":                    cni,
    }
    for nom_doc, fichier in documents_a_sauvegarder.items():
        valider_document(fichier, nom_doc)

    # ── 3. Créer le médecin (flush pour obtenir l'ID PNEU-) ───
    medecin = Medecin(
        civilite=civilite,
        nom=nom,
        prenom=prenom,
        email=email,
        password_hash=hash_password(password),
        specialite=specialite,
        numero_rpps=numero_rpps,
        etablissement=etablissement,
        telephone=telephone,
        adresse=adresse,
        bio=bio,
        linkedin=linkedin,
        website=website,
        statut="en_attente",
    )
    db.add(medecin)
    await db.flush()  # génère l'ID PNEU-XXXXXXX

    # ── 4. Sauvegarder la photo de profil ─────────────────────
    dossier_medecin = UPLOAD_DIR / medecin.id
    dossier_medecin.mkdir(parents=True, exist_ok=True)

    ext_photo   = Path(photo_profil.filename).suffix.lower()
    nom_photo   = f"photo_profil{ext_photo}"
    chemin_photo = dossier_medecin / nom_photo

    with open(chemin_photo, "wb") as f:
        shutil.copyfileobj(photo_profil.file, f)

    # Stocker l'URL relative (servie comme fichier statique via /uploads)
    medecin.photo_url = f"/uploads/{medecin.id}/{nom_photo}"

    # ── 5. Sauvegarder les 6 documents ────────────────────────
    dossier_docs = dossier_medecin / "documents"
    dossier_docs.mkdir(parents=True, exist_ok=True)

    for type_doc, fichier in documents_a_sauvegarder.items():
        extension   = Path(fichier.filename).suffix.lower()
        nom_fichier = f"{type_doc}{extension}"
        chemin      = dossier_docs / nom_fichier

        with open(chemin, "wb") as f:
            shutil.copyfileobj(fichier.file, f)

        doc = DocumentMedecin(
            id=generate_doc_id(),
            medecin_id=medecin.id,
            type_document=type_doc,
            url_fichier=str(chemin),
            nom_fichier=fichier.filename,
            taille_octets=fichier.size,
            mime_type=fichier.content_type,
        )
        db.add(doc)

    # ── 6. Commit tout en BD ───────────────────────────────────
    await db.commit()

    # ── 7. Notifier l'admin (SMS + notification in-app + email) ───────
    admin_result = await db.execute(select(Admin).limit(1))
    admin = admin_result.scalar_one_or_none()

    # 7a. Notification in-app persistée en BDD
    notif = Notification(
        destinataire_id=str(admin.id) if admin else "admin",
        type_dest="admin",
        type_notif="nouvelle_inscription_medecin",
        titre=f"Nouvelle demande d'accès — Dr {prenom} {nom}",
        message=(
            f"Dr {prenom} {nom} ({specialite}) a soumis une demande d'accès "
            f"à la plateforme. Identifiant : {medecin.id}."
        ),
        meta={"medecin_id": medecin.id, "lien": f"/admin/demandes/{medecin.id}"},
    )
    db.add(notif)
    await db.commit()

    # 7b. SMS Twilio — numéro admin depuis la BDD (enregistré à la première connexion)
    phone_admin = admin.phone if admin and admin.phone else None
    print(f"[SMS] Numéro admin en BDD : {phone_admin!r}")
    if phone_admin:
        try:
            await notify_admin_new_medecin(nom, prenom, specialite, phone_admin)
            print(f"[SMS] ✅ SMS envoyé à {phone_admin}")
        except Exception as e:
            print(f"[SMS] ❌ Échec Twilio — numéro={phone_admin} erreur={type(e).__name__}: {e}")
    else:
        print("[SMS] ⚠️ Numéro admin non encore enregistré en BDD — connecte-toi au dashboard admin pour l'enregistrer")

    # 7c. Email — adresse admin en BDD, sinon fallback sur ADMIN_EMAIL du .env
    email_admin = (admin.email if admin and admin.email else None) or settings.ADMIN_EMAIL
    if email_admin:
        try:
            await send_nouvelle_demande_admin_email(
                email_admin, nom, prenom, specialite, medecin.id,
            )
            print(f"[EMAIL] ✅ Notification envoyée à {email_admin}")
        except Exception as e:
            print(f"[EMAIL] ❌ Échec notification admin — {type(e).__name__}: {e}")

    return {
        "message": (
            f"Dossier de Dr {prenom} {nom} soumis avec succès. "
            f"Votre identifiant est {medecin.id}. "
            f"Vous serez notifié par email sous 24-48h."
        )
    }


# ─────────────────────────────────────────────────────────────
#  POST /api/v1/auth/login  (étape 1)
# ─────────────────────────────────────────────────────────────
@router.post("/login", response_model=MessageResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result  = await db.execute(select(Medecin).where(Medecin.email == body.email))
    medecin = result.scalar_one_or_none()

    if not medecin or not verify_password(body.password, medecin.password_hash):
        raise HTTPException(401, "Email ou mot de passe incorrect")

    if medecin.statut == "en_attente":
        raise HTTPException(403, "Votre compte est en attente de validation par l'administrateur")
    if medecin.statut == "rejete":
        raise HTTPException(403, "Votre inscription a été refusée. Vérifiez votre email.")
    if medecin.statut == "suspendu":
        raise HTTPException(403, "Votre compte est suspendu. Contactez l'administrateur.")

    # Générer OTP
    otp    = generate_otp()
    expiry = datetime.utcnow() + timedelta(minutes=5)

    otp_entry = OTPCode(
        id=generate_doc_id(),
        medecin_id=medecin.id,
        code=otp,
        expires_at=expiry,
        used=False,
    )
    db.add(otp_entry)
    await db.commit()

    import logging as _logging
    _logger = _logging.getLogger(__name__)
    email_sent = True
    try:
        await asyncio.wait_for(send_otp_email(medecin.email, medecin.nom, otp), timeout=6.0)
    except Exception as e:
        email_sent = False
        _logger.warning("Email OTP non envoyé (%s) — CODE CONSOLE: %s", e, otp)
        print(f"\n{'='*50}\n[OTP LOGIN] {medecin.email} → code: {otp}\n{'='*50}\n", flush=True)

    return {
        "message":    "Code OTP envoyé à votre email. Valable 5 minutes." if email_sent
                      else "Le code OTP a été généré mais l'envoi par email a échoué. Contactez l'administrateur si vous ne recevez pas le code.",
        "medecin_id": str(medecin.id),
        "email_sent": email_sent,
    }


# ─────────────────────────────────────────────────────────────
#  POST /api/v1/auth/verify-otp  (étape 2)
# ─────────────────────────────────────────────────────────────
@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(body: OTPVerifyRequest, db: AsyncSession = Depends(get_db)):
    from app.models.audit_log import AuditLog

    # Récupère le dernier OTP non utilisé (indépendamment du code saisi)
    result = await db.execute(
        select(OTPCode)
        .where(OTPCode.medecin_id == body.medecin_id)
        .where(OTPCode.used       == False)
        .order_by(OTPCode.created_at.desc())
        .limit(1)
    )
    otp_entry = result.scalar_one_or_none()

    if not otp_entry:
        raise HTTPException(401, "Code OTP incorrect ou expiré. Demandez un nouveau code.")

    if datetime.utcnow() > otp_entry.expires_at:
        raise HTTPException(401, "Code OTP expiré. Reconnectez-vous pour en recevoir un nouveau.")

    # ── Code incorrect → incrémenter fail_count ───────────────────
    if otp_entry.code != body.code:
        otp_entry.fail_count = (otp_entry.fail_count or 0) + 1
        await db.commit()

        if otp_entry.fail_count >= 3:
            med_result = await db.execute(select(Medecin).where(Medecin.id == body.medecin_id))
            medecin    = med_result.scalar_one_or_none()

            if medecin and medecin.statut not in ("corbeille", "rejete"):
                medecin.statut_precedent = medecin.statut
                medecin.statut           = "corbeille"
                medecin.supprime_le      = datetime.utcnow()
                medecin.supprime_par     = "system"

                db.add(AuditLog(
                    action     = "compte_bloque_tentatives",
                    medecin_id = medecin.id,
                    details    = {
                        "raison":     "3 tentatives OTP incorrectes consécutives",
                        "tentatives": otp_entry.fail_count,
                        "email":      medecin.email,
                    },
                ))

                admins = (await db.execute(select(Admin))).scalars().all()
                for admin in admins:
                    db.add(Notification(
                        destinataire_id = admin.id,
                        type_dest       = "admin",
                        type_notif      = "compte_bloque_tentatives",
                        titre           = "Compte médecin bloqué — tentatives suspectes",
                        message         = (
                            f"Le compte de Dr. {medecin.prenom} {medecin.nom} ({medecin.email}) "
                            f"a été mis en corbeille après 3 tentatives OTP incorrectes. "
                            f"Vous pouvez le restaurer depuis la corbeille."
                        ),
                        meta = {
                            "medecin_id":  medecin.id,
                            "medecin_nom": f"{medecin.prenom} {medecin.nom}",
                            "email":       medecin.email,
                            "actionLink":  "/administrateur/corbeille",
                        },
                    ))

                await db.commit()

            raise HTTPException(
                429,
                "Votre compte a été bloqué après 3 tentatives incorrectes. "
                "Contactez l'administrateur pour restaurer votre accès.",
            )

        restantes = 3 - otp_entry.fail_count
        raise HTTPException(
            401,
            f"Code OTP incorrect. {restantes} tentative(s) restante(s) avant le blocage du compte.",
        )

    # ── Code correct → succès ──────────────────────────────────────
    otp_entry.used       = True
    otp_entry.fail_count = 0

    med_result = await db.execute(select(Medecin).where(Medecin.id == body.medecin_id))
    medecin    = med_result.scalar_one_or_none()
    if medecin:
        medecin.derniere_connexion = datetime.utcnow()

    await db.commit()

    token = create_access_token({"sub": str(body.medecin_id), "role": "medecin"})
    return {"access_token": token, "token_type": "bearer"}


# ─────────────────────────────────────────────────────────────
#  Helper : convertit un chemin stocké en URL absolue publique
# ─────────────────────────────────────────────────────────────
def _photo_to_url(raw: str | None) -> str | None:
    """Transforme n'importe quelle valeur stockée en photo_url en URL HTTP."""
    if not raw:
        return None
    if raw.startswith("http"):          # Déjà une URL complète
        return raw
    if raw.startswith("/uploads/"):     # URL relative propre
        return f"{settings.BACKEND_URL}{raw}"
    # Anciens chemins filesystem (Windows ou relatifs)  ex: "uploads\PNEU-...\photo.jpg"
    clean = raw.replace("\\", "/").lstrip("./")
    return f"{settings.BACKEND_URL}/{clean}"


# ─────────────────────────────────────────────────────────────
#  GET /api/v1/auth/profil  — profil du médecin connecté
# ─────────────────────────────────────────────────────────────
@router.get("/profil")
async def get_profil(
    medecin: Medecin = Depends(get_current_medecin),
):
    """Retourne le profil complet du médecin authentifié (JWT Bearer)."""
    return {
        "id":            medecin.id,
        "civilite":      medecin.civilite,
        "nom":           medecin.nom,
        "prenom":        medecin.prenom,
        "email":         medecin.email,
        "specialite":    medecin.specialite,
        "etablissement": medecin.etablissement,
        "numero_rpps":   medecin.numero_rpps,
        "photo_url":     _photo_to_url(medecin.photo_url),
        "statut":        medecin.statut,
        "telephone":     medecin.telephone,
        "adresse":       medecin.adresse,
        "ville":         medecin.ville,
        "bio":           medecin.bio,
        "linkedin":      medecin.linkedin,
        "website":       medecin.website,
    }


# ─────────────────────────────────────────────────────────────
#  PATCH /api/v1/auth/photo  — mise à jour de la photo de profil
# ─────────────────────────────────────────────────────────────
@router.patch("/photo")
async def update_photo(
    photo: UploadFile = File(...),
    medecin: Medecin  = Depends(get_current_medecin),
    db: AsyncSession  = Depends(get_db),
):
    """Remplace la photo de profil du médecin connecté."""

    # 1. Valider type + taille
    valider_photo(photo)

    # 2. Supprimer l'ancienne photo si elle existe sur le disque
    if medecin.photo_url and medecin.photo_url.startswith("/uploads/"):
        old_path = Path(".") / medecin.photo_url.lstrip("/")
        if old_path.exists():
            old_path.unlink(missing_ok=True)

    # 3. Construire le chemin de la nouvelle photo
    dossier_medecin = UPLOAD_DIR / medecin.id
    dossier_medecin.mkdir(parents=True, exist_ok=True)

    ext_photo    = Path(photo.filename).suffix.lower() or ".jpg"
    nom_photo    = f"photo_profil_{uuid.uuid4().hex[:8]}{ext_photo}"
    chemin_photo = dossier_medecin / nom_photo

    # 4. Sauvegarder sur le disque
    with open(chemin_photo, "wb") as f:
        shutil.copyfileobj(photo.file, f)

    # 5. Mettre à jour la BD
    medecin.photo_url = f"/uploads/{medecin.id}/{nom_photo}"
    await db.commit()
    await db.refresh(medecin)

    return {"photo_url": _photo_to_url(medecin.photo_url)}


# ─────────────────────────────────────────────────────────────
#  PATCH /api/v1/auth/change-password — changement de mot de passe
# ─────────────────────────────────────────────────────────────
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password:     str

@router.patch("/change-password")
async def change_password(
    body:    ChangePasswordRequest,
    medecin: Medecin      = Depends(get_current_medecin),
    db:      AsyncSession = Depends(get_db),
):
    """Permet à un médecin authentifié de changer son propre mot de passe."""
    if not verify_password(body.current_password, medecin.password_hash):
        raise HTTPException(status_code=400, detail="Mot de passe actuel incorrect")
    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail="Le nouveau mot de passe doit contenir au moins 8 caractères")
    import re
    if not re.search(r'[A-Z]', body.new_password) or \
       not re.search(r'[a-z]', body.new_password) or \
       not re.search(r'[0-9]', body.new_password):
        raise HTTPException(status_code=400, detail="Doit contenir majuscule, minuscule et chiffre")
    medecin.password_hash = hash_password(body.new_password)
    await db.commit()
    return {"message": "Mot de passe mis à jour avec succès"}


# ─────────────────────────────────────────────────────────────
#  PATCH /api/v1/auth/profil  — mise à jour des infos du profil
# ─────────────────────────────────────────────────────────────
class ProfilUpdateRequest(BaseModel):
    nom:           str | None = None
    prenom:        str | None = None
    civilite:      str | None = None
    etablissement: str | None = None
    telephone:     str | None = None
    adresse:       str | None = None
    ville:         str | None = None
    bio:           str | None = None
    linkedin:      str | None = None
    website:       str | None = None

@router.patch("/profil")
async def update_profil(
    data:    ProfilUpdateRequest,
    medecin: Medecin      = Depends(get_current_medecin),
    db:      AsyncSession = Depends(get_db),
):
    """Met à jour les champs modifiables par le médecin lui-même."""
    if data.nom           is not None: medecin.nom           = data.nom
    if data.prenom        is not None: medecin.prenom        = data.prenom
    if data.civilite      is not None: medecin.civilite      = data.civilite
    if data.etablissement is not None: medecin.etablissement = data.etablissement
    if data.telephone     is not None: medecin.telephone     = data.telephone
    if data.adresse       is not None: medecin.adresse       = data.adresse
    if data.ville         is not None: medecin.ville         = data.ville
    if data.bio           is not None: medecin.bio           = data.bio
    if data.linkedin      is not None: medecin.linkedin      = data.linkedin
    if data.website       is not None: medecin.website       = data.website

    await db.commit()
    await db.refresh(medecin)

    return {
        "id":            medecin.id,
        "civilite":      medecin.civilite,
        "nom":           medecin.nom,
        "prenom":        medecin.prenom,
        "email":         medecin.email,
        "specialite":    medecin.specialite,
        "etablissement": medecin.etablissement,
        "numero_rpps":   medecin.numero_rpps,
        "photo_url":     _photo_to_url(medecin.photo_url),
        "statut":        medecin.statut,
        "telephone":     medecin.telephone,
        "adresse":       medecin.adresse,
        "ville":         medecin.ville,
        "bio":           medecin.bio,
        "linkedin":      medecin.linkedin,
        "website":       medecin.website,
    }


# ─────────────────────────────────────────────────────────────
#  GET /api/v1/auth/documents  — liste des documents du médecin
# ─────────────────────────────────────────────────────────────
LABELS_DOCUMENT = {
    "diplome_specialisation": "Diplôme de spécialisation",
    "diplome_medecine":       "Diplôme de docteur en médecine",
    "inscription_ordre":      "Inscription à l'ordre",
    "autorisation_exercice":  "Autorisation d'exercice",
    "carte_professionnelle":  "Carte professionnelle",
    "cni":                    "Carte nationale d'identité",
}

@router.get("/documents")
async def get_documents(
    medecin: Medecin = Depends(get_current_medecin),
    db: AsyncSession  = Depends(get_db),
):
    result = await db.execute(
        select(DocumentMedecin).where(DocumentMedecin.medecin_id == medecin.id)
    )
    docs = result.scalars().all()
    return [
        {
            "id":           d.id,
            "type":         d.type_document,
            "label":        LABELS_DOCUMENT.get(d.type_document, d.type_document),
            "nom_fichier":  d.nom_fichier,
            "url":          f"{settings.BACKEND_URL}{d.url_fichier}" if d.url_fichier.startswith("/") else d.url_fichier,
            "taille_ko":    round(d.taille_octets / 1024) if d.taille_octets else None,
            "date":         d.created_at.strftime("%d/%m/%Y") if d.created_at else None,
        }
        for d in docs
    ]


# ─────────────────────────────────────────────────────────────
#  POST /api/v1/auth/forgot-password
#  Vérifie l'email → envoie un OTP de réinitialisation
# ─────────────────────────────────────────────────────────────
class ForgotPasswordRequest(BaseModel):
    email: str

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(body: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    result  = await db.execute(select(Medecin).where(Medecin.email == body.email))
    medecin = result.scalar_one_or_none()

    if not medecin:
        raise HTTPException(404, "Email introuvable ou inexistant dans la base de données")

    # Invalider tout OTP reset précédent encore actif
    await db.execute(
        sa_update(OTPCode)
        .where(OTPCode.medecin_id == medecin.id, OTPCode.purpose == 'reset', OTPCode.used == False)
        .values(used=True)
    )

    otp    = generate_otp()
    expiry = datetime.utcnow() + timedelta(minutes=5)
    otp_entry = OTPCode(
        id=generate_doc_id(),
        medecin_id=medecin.id,
        code=otp,
        expires_at=expiry,
        used=False,
        purpose='reset',
        fail_count=0,
    )
    db.add(otp_entry)
    await db.commit()

    import logging as _logging
    _logger = _logging.getLogger(__name__)
    email_sent = True
    try:
        await asyncio.wait_for(send_reset_otp_email(medecin.email, medecin.nom, otp), timeout=6.0)
    except Exception as e:
        email_sent = False
        _logger.warning("Email reset OTP non envoyé (%s) — CODE CONSOLE: %s", e, otp)
        print(f"\n{'='*50}\n[OTP RESET] {medecin.email} → code: {otp}\n{'='*50}\n", flush=True)

    return {
        "message":    "Code OTP envoyé à votre email. Valable 5 minutes." if email_sent
                      else "Le code OTP a été généré mais l'envoi par email a échoué.",
        "medecin_id": str(medecin.id),
        "email_sent": email_sent,
    }


# ─────────────────────────────────────────────────────────────
#  POST /api/v1/auth/reset-verify-otp
#  Vérifie le code (max 3 tentatives) → retourne un reset_token
# ─────────────────────────────────────────────────────────────
class ResetVerifyOTPRequest(BaseModel):
    medecin_id: str
    code:       str

@router.post("/reset-verify-otp")
async def reset_verify_otp(body: ResetVerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(OTPCode)
        .where(OTPCode.medecin_id == body.medecin_id)
        .where(OTPCode.purpose    == 'reset')
        .where(OTPCode.used       == False)
        .order_by(OTPCode.created_at.desc())
        .limit(1)
    )
    otp_entry = result.scalar_one_or_none()

    if not otp_entry:
        raise HTTPException(404, "Aucun code de réinitialisation en cours. Recommencez.")

    if datetime.utcnow() > otp_entry.expires_at:
        otp_entry.used = True
        await db.commit()
        raise HTTPException(401, "Code OTP expiré. Demandez un nouveau code.")

    if otp_entry.fail_count >= 3:
        raise HTTPException(429, "Trop de tentatives incorrectes. Demandez un nouveau code.")

    if otp_entry.code != body.code:
        otp_entry.fail_count += 1
        await db.commit()

        if otp_entry.fail_count >= 3:
            # Notifier admin + médecin
            medecin = await db.get(Medecin, body.medecin_id)
            admins  = (await db.execute(select(Admin))).scalars().all()
            for admin in admins:
                try:
                    await send_piratage_admin_email(
                        admin.email, medecin.nom, medecin.email,
                        medecin.id, otp_entry.fail_count
                    )
                except Exception as e:
                    print(f"⚠️ Email admin non envoyé : {e}")
            try:
                await send_piratage_medecin_email(medecin.email, medecin.nom)
            except Exception as e:
                print(f"⚠️ Email médecin non envoyé : {e}")
            raise HTTPException(
                429,
                "Compte bloqué après 3 tentatives incorrectes. "
                "L'administrateur a été notifié. Demandez un nouveau code."
            )

        restantes = 3 - otp_entry.fail_count
        raise HTTPException(
            401,
            f"Le code à usage unique que vous avez entré est incorrect. "
            f"{restantes} tentative(s) restante(s)."
        )

    # Code correct
    otp_entry.used = True
    await db.commit()

    reset_token = create_access_token(
        {"sub": str(body.medecin_id), "purpose": "reset_password"},
        expires_minutes=10,
    )
    return {"reset_token": reset_token, "message": "Code vérifié. Vous pouvez réinitialiser votre mot de passe."}


# ─────────────────────────────────────────────────────────────
#  POST /api/v1/auth/reset-password
#  Reçoit le reset_token + nouveau mot de passe
# ─────────────────────────────────────────────────────────────
class ResetPasswordRequest(BaseModel):
    reset_token:  str
    new_password: str

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password_endpoint(body: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(body.reset_token)
        if payload.get("purpose") != "reset_password":
            raise HTTPException(400, "Token de réinitialisation invalide")
        medecin_id = payload.get("sub")
        if not medecin_id:
            raise HTTPException(400, "Token invalide")
    except JWTError:
        raise HTTPException(401, "Token de réinitialisation invalide ou expiré")

    if len(body.new_password) < 8:
        raise HTTPException(400, "Le mot de passe doit contenir au moins 8 caractères")

    medecin = await db.get(Medecin, medecin_id)
    if not medecin:
        raise HTTPException(404, "Médecin introuvable")

    medecin.password_hash = hash_password(body.new_password)
    await db.commit()

    return {"message": "Mot de passe réinitialisé avec succès. Vous pouvez maintenant vous connecter."}


# ─────────────────────────────────────────────────────────────
#  GET /api/v1/auth/activate?token=xxx
# ─────────────────────────────────────────────────────────────
@router.get("/activate", response_model=MessageResponse)
async def activate_account(token: str, db: AsyncSession = Depends(get_db)):
    result  = await db.execute(
        select(Medecin).where(Medecin.activation_token == token)
    )
    medecin = result.scalar_one_or_none()

    if not medecin:
        raise HTTPException(400, "Lien invalide ou déjà utilisé")
    if medecin.statut != "valide":
        raise HTTPException(403, "Compte non validé par l'administrateur")
    if datetime.utcnow() > medecin.activation_expires:
        raise HTTPException(400, "Ce lien a expiré (7 jours). Contactez l'administrateur.")

    return {"message": "Compte activé. Vous pouvez maintenant vous connecter."}
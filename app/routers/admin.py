"""
admin_router.py — Routes API pour le panneau d'administration PneumoIA

Organisation :
   1.  Auth                  → login, reset mot de passe
   2.  Demandes en attente   → liste, valider, rejeter
   3.  Validées par mois     → filtrage mois/année
   4.  Refusées              → liste, supprimer, relancer
   5.  Médecins actifs       → liste enrichie avec stats
   6.  Médecin par ID        → profil complet + documents
   7.  Actions médecins      → suspendre, réactiver, supprimer
   8.  Médecins par statut   → endpoint générique
   9.  FAQ — questions       → liste, répondre
   10. FAQ — publiées        → CRUD admin
   11. Statistiques          → consultations, répartition géo
   12. Paramètres            → get, update
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

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


# ─────────────────────────────────────────────────────────────────────────────
# 1. AUTH
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/auth/login")
async def admin_login(
    body: LoginSchema,
    db: AsyncSession = Depends(get_db),
):
    """
    Connexion admin — retourne un JWT Bearer token.
    Vérifie email + mot de passe + numéro de téléphone.
    POST /api/admin/auth/login
    """
    result = await db.execute(select(Admin).where(Admin.email == body.email))
    admin  = result.scalar_one_or_none()

    if not admin or not verify_password(body.password, admin.password_hash):
        raise HTTPException(401, "Email ou mot de passe incorrect.")

    if not admin.phone:
        admin.phone = body.phone
        await db.commit()
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
        "admin": {"id": admin.id, "email": admin.email, "phone": admin.phone},
    }


@router.post("/auth/reset-request")
async def reset_request(
    body: ResetRequestSchema,
    db: AsyncSession = Depends(get_db),
):
    """
    Demande de réinitialisation — envoie un OTP par SMS via Twilio.
    Valide 10 minutes.
    POST /api/admin/auth/reset-request
    """
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
    """
    Vérifie l'OTP et met à jour le mot de passe.
    POST /api/admin/auth/reset-confirm
    """
    await AdminService.verify_and_update_password(
        db, email=body.email, otp=body.otp, new_password=body.new_password,
    )
    return {"message": "Mot de passe mis à jour avec succès."}


# ─────────────────────────────────────────────────────────────────────────────
# 2. DEMANDES EN ATTENTE
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/demandes")
async def get_demandes(
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """
    Retourne tous les médecins en attente de validation.
    Inclut : données personnelles, photo de profil, documents joints.
    GET /api/admin/demandes
    """
    return await AdminService.get_demandes(db)


@router.post("/demandes/{medecin_id}/valider")
async def valider_medecin(
    medecin_id: str,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """
    Valide un médecin — statut passe à 'valide'.
    Génère un lien d'activation + email Brevo.
    POST /api/admin/demandes/{id}/valider
    """
    return await AdminService.valider_medecin(db, medecin_id, admin.id)


@router.post("/demandes/{medecin_id}/rejeter")
async def rejeter_medecin(
    medecin_id: str,
    body: RefusRequestSchema,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """
    Refuse un médecin — statut passe à 'rejete'.
    Email de refus avec motif envoyé via Brevo.
    POST /api/admin/demandes/{id}/rejeter
    """
    return await AdminService.rejeter_medecin(db, medecin_id, body.motif)


# ─────────────────────────────────────────────────────────────────────────────
# 3. VALIDÉES PAR MOIS / ANNÉE
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/demandes/valides")
async def get_valides(
    mois:  Optional[int] = None,
    annee: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """
    Retourne les médecins validés pour un mois/année donnés.
    Par défaut : mois en cours.
    GET /api/admin/demandes/valides?mois=6&annee=2026
    """
    return await AdminService.get_valides(db, mois, annee)


# ─────────────────────────────────────────────────────────────────────────────
# 4. REFUSÉES
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/demandes/refusees")
async def get_demandes_refusees(
    ville: Optional[str] = None,
    motif: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """
    Retourne les dossiers refusés avec filtres optionnels ville/motif.
    GET /api/admin/demandes/refusees?ville=Douala&motif=CNOM invalide
    """
    return await AdminService.get_demandes_refusees(db, ville=ville, motif=motif)


@router.delete("/demandes/{medecin_id}/refusees")
async def supprimer_dossier_refuse(
    medecin_id: str,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """
    Supprime définitivement un dossier refusé. Action irréversible.
    DELETE /api/admin/demandes/{id}/refusees
    """
    return await AdminService.supprimer_dossier_refuse(db, medecin_id)


@router.post("/demandes/{medecin_id}/relancer")
async def relancer_medecin(
    medecin_id: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """
    Envoie un e-mail de relance au médecin refusé via Brevo.
    relance_sent passe à True — bouton grisé côté frontend.
    POST /api/admin/demandes/{id}/relancer
    Body: { "message": "..." }
    """
    return await AdminService.relancer_medecin(
        db,
        medecin_id = medecin_id,
        message    = body.get("message", ""),
        admin_id   = admin.id,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 5. MÉDECINS ACTIFS AVEC STATS
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/medecins/actifs")
async def get_medecins_actifs(
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """
    Retourne tous les médecins validés enrichis avec leurs stats :
    patients, consultations, concordance IA, dernière activité, rang.
    Le statut Actif/Inactif est calculé côté frontend (règle > 14j).
    GET /api/admin/medecins/actifs
    """
    return await AdminService.get_medecins_actifs(db)


# ─────────────────────────────────────────────────────────────────────────────
# 6. PROFIL MÉDECIN PAR ID
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/medecins/{medecin_id}")
async def get_medecin_by_id(
    medecin_id: str,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """
    Retourne le profil complet d'un médecin avec toutes ses stats + documents.
    Utilisé par ProfilMedecin.jsx pour hydrater la page depuis le backend.
    GET /api/admin/medecins/{id}
    """
    return await AdminService.get_medecin_by_id(db, medecin_id)


# ─────────────────────────────────────────────────────────────────────────────
# 7. ACTIONS SUR LES MÉDECINS
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/medecins/{medecin_id}/suspendre")
async def suspendre_medecin(
    medecin_id: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """
    Suspend un médecin — statut passe à 'suspendu'.
    Email de notification envoyé via Brevo avec raison + durée.
    POST /api/admin/medecins/{id}/suspendre
    Body: { raison, duree, message }
    """
    return await AdminService.suspendre_medecin(
        db, medecin_id,
        raison   = body.get("raison",  ""),
        duree    = body.get("duree",   ""),
        message  = body.get("message", ""),
        admin_id = admin.id,
    )


@router.post("/medecins/{medecin_id}/reactiver")
async def reactiver_medecin(
    medecin_id: str,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """
    Réactive un médecin suspendu — statut repasse à 'valide'.
    Email de notification envoyé via Brevo avec motif initial.
    POST /api/admin/medecins/{id}/reactiver
    """
    return await AdminService.reactiver_medecin(db, medecin_id, admin.id)


@router.delete("/medecins/{medecin_id}")
async def supprimer_medecin(
    medecin_id: str,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """
    Supprime définitivement un médecin et toutes ses données.
    Email de notification envoyé via Brevo. Action irréversible.
    DELETE /api/admin/medecins/{id}
    """
    return await AdminService.supprimer_medecin(db, medecin_id)


# ─────────────────────────────────────────────────────────────────────────────
# 8. MÉDECINS PAR STATUT (endpoint générique)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/demandes/statut/{statut}")
async def get_demandes_par_statut(
    statut: str,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """
    Retourne les médecins filtrés par statut.
    Valeurs acceptées : en_attente | valide | rejete | suspendu
    GET /api/admin/demandes/statut/suspendu
    GET /api/admin/demandes/statut/rejete
    """
    if statut not in ("en_attente", "valide", "rejete", "suspendu"):
        raise HTTPException(400, f"Statut invalide : {statut}")
    return await AdminService.get_demandes_par_statut(db, statut)


# ─────────────────────────────────────────────────────────────────────────────
# 9. FAQ — QUESTIONS DES MÉDECINS
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/faq/questions")
async def get_questions(
    statut:    Optional[str] = None,
    categorie: Optional[str] = None,
    ville:     Optional[str] = None,
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Retourne les questions posées par les médecins.
    Filtres optionnels : statut (en_attente|repondu), categorie, ville.
    GET /api/admin/faq/questions?statut=en_attente&categorie=IA
    """
    return await AdminService.get_questions(db, statut=statut, categorie=categorie, ville=ville)


@router.post("/faq/questions/{question_id}/repondre")
async def repondre_question(
    question_id: str,
    body:  dict,
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Répond à une question de médecin.
    Email de réponse envoyé automatiquement via Brevo.
    POST /api/admin/faq/questions/{id}/repondre
    Body: { "reponse": "..." }
    """
    reponse = body.get("reponse", "").strip()
    if not reponse:
        raise HTTPException(400, "La réponse ne peut pas être vide.")
    return await AdminService.repondre_question(db, question_id, reponse, admin.id)


# ─────────────────────────────────────────────────────────────────────────────
# 10. FAQ — PUBLIÉES PAR L'ADMIN
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/faq")
async def get_faq(
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Retourne toutes les entrées FAQ (publiées + brouillons).
    GET /api/admin/faq
    """
    return await AdminService.get_faq(db)


@router.post("/faq")
async def creer_faq(
    body:  dict,
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Crée une nouvelle entrée FAQ.
    POST /api/admin/faq
    Body: { question, reponse, categorie, publie }
    """
    return await AdminService.creer_faq(
        db,
        question  = body.get("question",  ""),
        reponse   = body.get("reponse",   ""),
        categorie = body.get("categorie", "Autre"),
        publie    = body.get("publie",    False),
        admin_id  = admin.id,
    )


@router.put("/faq/{faq_id}")
async def modifier_faq(
    faq_id: str,
    body:   dict,
    db:     AsyncSession = Depends(get_db),
    admin:  Admin        = Depends(get_current_admin),
):
    """
    Modifie une entrée FAQ existante.
    PUT /api/admin/faq/{id}
    Body: { question, reponse, categorie, publie }
    """
    return await AdminService.modifier_faq(
        db, faq_id,
        question  = body.get("question",  ""),
        reponse   = body.get("reponse",   ""),
        categorie = body.get("categorie", "Autre"),
        publie    = body.get("publie",    False),
        admin_id  = admin.id,
    )


@router.patch("/faq/{faq_id}/toggle")
async def toggle_faq_publie(
    faq_id: str,
    db:     AsyncSession = Depends(get_db),
    admin:  Admin        = Depends(get_current_admin),
):
    """
    Publie ou dépublie une entrée FAQ (toggle).
    PATCH /api/admin/faq/{id}/toggle
    """
    return await AdminService.toggle_faq_publie(db, faq_id, admin.id)


@router.delete("/faq/vider")
async def vider_faq(
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Supprime toutes les entrées FAQ définitivement en base.
    ⚠️  Le frontend masque uniquement — cet endpoint n'est pas appelé pour l'instant.
    DELETE /api/admin/faq/vider
    """
    return await AdminService.vider_faq(db, admin.id)


@router.delete("/faq/{faq_id}")
async def supprimer_faq(
    faq_id: str,
    db:     AsyncSession = Depends(get_db),
    admin:  Admin        = Depends(get_current_admin),
):
    """
    Supprime définitivement une entrée FAQ.
    ⚠️  Le frontend masque uniquement — cet endpoint n'est pas appelé pour l'instant.
    DELETE /api/admin/faq/{id}
    """
    return await AdminService.supprimer_faq(db, faq_id, admin.id)


# ─────────────────────────────────────────────────────────────────────────────
# 11. STATISTIQUES
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/stats/consultations/semaine")
async def get_consultations_semaine(
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Consultations par jour sur les 30 derniers jours.
    Utilisé par CourbeActivite.jsx.
    GET /api/admin/stats/consultations/semaine
    """
    return await AdminService.get_consultations_semaine(db)


@router.get("/stats/consultations/annee")
async def get_consultations_annee(
    year:  int = 2026,
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Consultations agrégées par mois pour une année (12 entrées).
    GET /api/admin/stats/consultations/annee?year=2026
    """
    return await AdminService.get_consultations_annee(db, year)


@router.get("/stats/consultations/total")
async def get_consultations_total(
    from_date: Optional[str] = None,
    to_date:   Optional[str] = None,
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Total consultations sur une période personnalisée.
    GET /api/admin/stats/consultations/total?from=2026-01-01&to=2026-06-30
    """
    if not from_date or not to_date:
        raise HTTPException(400, "Paramètres 'from' et 'to' requis (format YYYY-MM-DD).")
    return await AdminService.get_consultations_total(db, from_date, to_date)


@router.get("/stats/repartition-geo")
async def get_repartition_geo(
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Répartition des médecins validés par ville.
    GET /api/admin/stats/repartition-geo
    """
    return await AdminService.get_repartition_geo(db)


# ─────────────────────────────────────────────────────────────────────────────
# 12. PARAMÈTRES
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/parametres")
async def get_parametres(
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Retourne les paramètres globaux de la plateforme.
    Fallback sur valeurs par défaut si table absente.
    GET /api/admin/parametres
    """
    return await AdminService.get_parametres(db)


@router.put("/parametres")
async def update_parametres(
    body:  dict,
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Met à jour les paramètres globaux (upsert sur clé "global").
    PUT /api/admin/parametres
    Body: { tous les paramètres }
    """
    return await AdminService.update_parametres(db, body, admin.id)
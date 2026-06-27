"""
admin_router.py — Routes API pour le panneau d'administration PneumoIA

Organisation :
   1.  Auth                        → login, reset mot de passe
   2.  Demandes en attente         → liste, valider, rejeter
   3.  Validées par mois           → filtrage mois/année
   4.  Refusées                    → liste, supprimer, relancer
   5.  Médecins actifs             → liste enrichie avec stats
   6.  Médecin par ID              → profil complet + documents
   7.  Documents médecins          → valider, rejeter (email au médecin)
   8.  Actions médecins            → suspendre, réactiver, supprimer (→ corbeille)
   9.  Médecins par statut         → endpoint générique
   10. FAQ — questions             → liste, répondre
   11. FAQ — publiées              → CRUD admin
   12. Statistiques                → consultations, répartition géo, KPIs, top médecins
   13. Paramètres                  → get, update
   14. Notifications               → liste, marquer lue, tout lire
   15. Journal d'audit             → liste, purger
   16. Corbeille                   → liste, restaurer, supprimer définitivement
   17. Avis / commentaires         → liste, supprimer, marquer vus
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.core.security import get_current_admin, verify_password, create_access_token
from app.models.admin import Admin
from app.models.notification import Notification
from app.models.question_admin import QuestionAdmin
from app.models.faqPubliee import FAQPubliee
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
    Génère un lien d'activation + email SMTP envoyé au médecin.
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
    Email de refus avec motif envoyé via SMTP au médecin.
    POST /api/admin/demandes/{id}/rejeter
    """
    return await AdminService.rejeter_medecin(db, medecin_id, body.motif, admin.id)


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
    Envoie un e-mail de relance au médecin refusé via SMTP.
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
    Retourne tous les médecins validés enrichis avec leurs stats.
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
    GET /api/admin/medecins/{id}
    """
    return await AdminService.get_medecin_by_id(db, medecin_id)


# ─────────────────────────────────────────────────────────────────────────────
# 7. VALIDATION / REJET DE DOCUMENTS
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/documents/{document_id}/valider")
async def valider_document(
    document_id: str,
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Valide un document médecin — statut passe à 'valide'.
    Email de notification envoyé au médecin via SMTP.
    POST /api/admin/documents/{id}/valider
    """
    return await AdminService.valider_document(db, document_id, admin.id)


@router.post("/documents/{document_id}/rejeter")
async def rejeter_document(
    document_id: str,
    body:  dict,
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Rejette un document médecin avec un motif — statut passe à 'rejete'.
    Email de notification envoyé au médecin via SMTP.
    POST /api/admin/documents/{id}/rejeter
    Body: { "motif": "..." }
    """
    motif = body.get("motif", "").strip()
    if not motif:
        raise HTTPException(400, "Un motif de rejet est obligatoire.")
    return await AdminService.rejeter_document(db, document_id, motif, admin.id)


# ─────────────────────────────────────────────────────────────────────────────
# 8. ACTIONS SUR LES MÉDECINS
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
    Email de notification envoyé au médecin (SMTP) avec raison + durée.
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
    Déplace un médecin dans la corbeille (soft delete — statut = 'corbeille').
    Suppression définitive depuis /api/admin/corbeille/{id}.
    DELETE /api/admin/medecins/{id}
    """
    return await AdminService.supprimer_medecin(db, medecin_id, admin.id)


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
    GET /api/admin/faq/questions?statut=en_attente&categorie=IA&ville=Douala
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
    POST /api/admin/faq/questions/{id}/repondre
    Body: { "reponse": "..." }
    """
    reponse = body.get("reponse", "").strip()
    if not reponse:
        raise HTTPException(400, "La réponse ne peut pas être vide.")
    return await AdminService.repondre_question(db, question_id, reponse, admin.id)


@router.post("/faq/questions/{question_id}/publier-faq")
async def publier_question_en_faq(
    question_id: str,
    body:  dict,
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Publie une question de médecin directement en FAQ (landing page + médecins).
    POST /api/admin/faq/questions/{id}/publier-faq
    Body: { "reponse": "...", "categorie": "Autre" }
    """
    q = await db.get(QuestionAdmin, question_id)
    if not q:
        raise HTTPException(404, "Question introuvable")

    if q.statut == "en_attente":
        raise HTTPException(400, "Répondez d'abord à la question avant de la publier en FAQ.")

    reponse = (body.get("reponse") or "").strip() or (q.reponse or "").strip()
    if not reponse:
        raise HTTPException(400, "La réponse ne peut pas être vide")

    categorie = (body.get("categorie") or "Autre").strip()

    q.statut     = "publiee_faq"
    q.reponse    = reponse
    q.repondu_at = datetime.utcnow()

    faq = FAQPubliee(
        admin_id  = admin.id,
        question  = q.titre,
        reponse   = reponse,
        categorie = categorie,
        publie    = True,
    )
    db.add(faq)
    await db.commit()
    await db.refresh(faq)

    return {
        "id":         faq.id,
        "question":   faq.question,
        "reponse":    faq.reponse,
        "categorie":  faq.categorie,
        "publie":     faq.publie,
        "nb_vues":    faq.nb_vues,
        "created_at": faq.created_at.isoformat() if faq.created_at else None,
        "updated_at": None,
    }


@router.delete("/faq/questions/historique")
async def vider_historique_questions(
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Supprime définitivement toutes les questions répondues.
    DELETE /api/admin/faq/questions/historique
    """
    return await AdminService.vider_historique_questions(db, admin.id)


@router.delete("/faq/questions/{question_id}")
async def supprimer_question(
    question_id: str,
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Supprime définitivement une question.
    DELETE /api/admin/faq/questions/{id}
    """
    return await AdminService.supprimer_question(db, question_id, admin.id)


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
    Supprime toutes les entrées FAQ définitivement.
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
    DELETE /api/admin/faq/{id}
    """
    return await AdminService.supprimer_faq(db, faq_id, admin.id)


# ─────────────────────────────────────────────────────────────────────────────
# 11. STATISTIQUES
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/stats/kpis")
async def get_kpis(
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    KPIs globaux du dashboard : médecins actifs, demandes en attente,
    consultations total, précision IA moyenne.
    GET /api/admin/stats/kpis
    """
    return await AdminService.get_kpis(db)


@router.get("/stats/consultations/semaine")
async def get_consultations_semaine(
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Consultations par jour sur les 30 derniers jours — pour la courbe d'activité.
    GET /api/admin/stats/consultations/semaine
    Retourne : { jours: [{ j: "Lun", c: 432 }, ...] }
    """
    return await AdminService.get_consultations_semaine(db)


@router.get("/stats/consultations/jours")
async def get_consultations_jours(
    from_date: str  = Query(..., alias="from"),
    to_date:   str  = Query(..., alias="to"),
    db:        AsyncSession = Depends(get_db),
    admin:     Admin        = Depends(get_current_admin),
):
    """
    Consultations par jour sur une plage quelconque.
    GET /api/admin/stats/consultations/jours?from=2026-05-11&to=2026-06-17
    Retourne : [{ date: "2026-06-11", c: 5 }, ...]
    """
    return await AdminService.get_consultations_jours(db, from_date, to_date)


@router.get("/stats/consultations/annee")
async def get_consultations_annee(
    year:  int = Query(default=2026),
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Consultations agrégées par mois pour une année (12 valeurs).
    GET /api/admin/stats/consultations/annee?year=2026
    Retourne : { mois: [4820, 5200, 0, ...] }
    """
    return await AdminService.get_consultations_annee(db, year)


@router.get("/stats/consultations/total")
async def get_consultations_total(
    from_date: Optional[str] = Query(None, alias="from"),
    to_date:   Optional[str] = Query(None, alias="to"),
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    KPIs consultations sur une période personnalisée.
    GET /api/admin/stats/consultations/total?from=2026-01-01&to=2026-06-30
    Retourne : { total, moyenne_par_jour, pic, variation_vs_mois_precedent }
    """
    if not from_date or not to_date:
        raise HTTPException(400, "Paramètres 'from' et 'to' requis (format YYYY-MM-DD).")
    return await AdminService.get_consultations_total(db, from_date, to_date)


@router.get("/stats/repartition-geo")
async def get_repartition_geo(
    mois:  Optional[int] = None,
    annee: Optional[int] = None,
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Répartition des médecins validés par ville et par région.
    GET /api/admin/stats/repartition-geo?mois=6&annee=2026
    Retourne : { villes: [...], regions: [...] }
    """
    return await AdminService.get_repartition_geo(db, mois, annee)


@router.get("/stats/concordance/evolution")
async def get_concordance_evolution(
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Concordance IA moyenne par mois sur les 6 derniers mois glissants.
    GET /api/admin/stats/concordance/evolution
    Retourne : [{ m: "Jan", v: 85 }, ...]
    """
    return await AdminService.get_concordance_evolution(db)


@router.get("/stats/concordance/pathologies")
async def get_concordance_pathologies(
    mois:  int = Query(...),
    annee: int = Query(...),
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Concordance IA moyenne par pathologie pour un mois/année.
    GET /api/admin/stats/concordance/pathologies?mois=6&annee=2026
    Retourne : [{ p: "Pneumonie bactérienne", t: 87, nb: 12 }, ...]
    """
    return await AdminService.get_concordance_pathologies(db, mois, annee)


@router.get("/stats/top-medecins-concordance")
async def get_top_medecins_concordance(
    mois:  Optional[int] = None,
    annee: Optional[int] = None,
    limit: int = Query(default=5),
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Top N médecins classés par taux de concordance IA décroissant.
    GET /api/admin/stats/top-medecins-concordance?mois=6&annee=2026
    Retourne : [{ id, prenom, nom, photo_url, concordance_ia, nb_consultations, tendance }]
    """
    return await AdminService.get_top_medecins_concordance(db, limit, mois=mois, annee=annee)


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
    """
    return await AdminService.update_parametres(db, body, admin.id)


# ─────────────────────────────────────────────────────────────────────────────
# 13. NOTIFICATIONS ADMIN
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/notifications")
async def get_notifications(
    non_lues_seulement: bool = False,
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Retourne les notifications de l'admin (nouvelles inscriptions, etc.).
    GET /api/admin/notifications?non_lues_seulement=true
    """
    query = (
        select(Notification)
        .where(
            Notification.destinataire_id == str(admin.id),
            Notification.type_dest == "admin",
        )
        .order_by(desc(Notification.created_at))
        .limit(100)
    )
    if non_lues_seulement:
        query = query.where(Notification.lu == False)

    result = await db.execute(query)
    notifs = result.scalars().all()
    non_lues = sum(1 for n in notifs if not n.lu)

    return {
        "total":    len(notifs),
        "non_lues": non_lues,
        "notifications": [
            {
                "id":         n.id,
                "type":       n.type_notif,
                "titre":      n.titre,
                "message":    n.message,
                "meta":       n.meta,
                "lu":         n.lu,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in notifs
        ],
    }


@router.patch("/notifications/{notif_id}/lu")
async def marquer_notification_lue(
    notif_id: str,
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Marque une notification comme lue.
    PATCH /api/admin/notifications/{id}/lu
    """
    result = await db.execute(
        select(Notification).where(
            Notification.id == notif_id,
            Notification.destinataire_id == str(admin.id),
            Notification.type_dest == "admin",
        )
    )
    notif = result.scalar_one_or_none()
    if not notif:
        raise HTTPException(404, "Notification introuvable")
    notif.lu = True
    await db.commit()
    return {"message": "Notification marquée comme lue", "id": notif_id}


@router.patch("/notifications/tout-lire")
async def marquer_toutes_lues(
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Marque toutes les notifications de l'admin comme lues.
    PATCH /api/admin/notifications/tout-lire
    """
    result = await db.execute(
        select(Notification).where(
            Notification.destinataire_id == str(admin.id),
            Notification.type_dest == "admin",
            Notification.lu == False,
        )
    )
    notifs = result.scalars().all()
    for n in notifs:
        n.lu = True
    await db.commit()
    return {"message": f"{len(notifs)} notification(s) marquée(s) comme lue(s)"}


# ─────────────────────────────────────────────────────────────────────────────
# 14. JOURNAL D'AUDIT
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/audit/logs")
async def get_audit_logs(
    type:   Optional[str] = None,
    statut: Optional[str] = None,
    db:     AsyncSession = Depends(get_db),
    admin:  Admin        = Depends(get_current_admin),
):
    """
    Retourne les entrées du journal d'audit avec filtres optionnels.
    GET /api/admin/audit/logs?type=Connexion&statut=success
    Retourne : { logs: [{ id, action, acteur, date, statut, type }] }
    """
    return await AdminService.get_audit_logs(db, type=type, statut=statut)


@router.delete("/audit/logs/purger")
async def purger_audit_logs(
    body:  dict,
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Supprime les entrées du journal antérieures à N jours (0 = tout purger).
    DELETE /api/admin/audit/logs/purger
    Body: { "days": 30 }
    """
    days = int(body.get("days", 30))
    return await AdminService.purger_audit_logs(db, days, admin.id)


# ─────────────────────────────────────────────────────────────────────────────
# 15. CORBEILLE
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/corbeille")
async def get_corbeille(
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Retourne les médecins en corbeille (supprimés mais restaurables).
    GET /api/admin/corbeille
    """
    return await AdminService.get_corbeille(db)


@router.post("/corbeille/{medecin_id}/restaurer")
async def restaurer_medecin(
    medecin_id: str,
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Restaure un médecin depuis la corbeille — reprend son statut précédent.
    POST /api/admin/corbeille/{id}/restaurer
    """
    return await AdminService.restaurer_medecin(db, medecin_id, admin.id)


@router.delete("/corbeille/{medecin_id}")
async def supprimer_definitif(
    medecin_id: str,
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Supprime définitivement un médecin depuis la corbeille. Irréversible.
    DELETE /api/admin/corbeille/{id}
    """
    return await AdminService.supprimer_definitif(db, medecin_id, admin.id)


# ─────────────────────────────────────────────────────────────────────────────
# 16. AVIS / COMMENTAIRES
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/avis")
async def get_avis(
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Retourne tous les avis publiés par les médecins sur la plateforme.
    GET /api/admin/avis
    """
    return await AdminService.get_avis(db)


class AvisDeleteBody(BaseModel):
    raison: Optional[str] = None

@router.delete("/avis/{avis_id}")
async def supprimer_avis(
    avis_id: str,
    body:    AvisDeleteBody = Body(default=AvisDeleteBody()),
    db:      AsyncSession   = Depends(get_db),
    admin:   Admin          = Depends(get_current_admin),
):
    """
    Supprime un avis. Le médecin est notifié sur la plateforme (et par email).
    DELETE /api/admin/avis/{id}
    """
    return await AdminService.supprimer_avis(db, avis_id, admin.id, body.raison)


@router.patch("/avis/marquer-vus")
async def marquer_avis_vus(
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Marque tous les avis comme vus.
    PATCH /api/admin/avis/marquer-vus
    """
    return await AdminService.marquer_avis_vus(db)


@router.get("/avis/archives")
async def get_avis_archives(
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Retourne les avis archivés par l'admin (purge auto après 7 jours via cron).
    GET /api/admin/avis/archives
    """
    return await AdminService.get_avis_archives(db)


@router.patch("/avis/{avis_id}/archiver")
async def archiver_avis(
    avis_id: str,
    db:      AsyncSession = Depends(get_db),
    admin:   Admin        = Depends(get_current_admin),
):
    """
    Archive un avis (reste sur la landing page, disparaît de la vue active admin).
    PATCH /api/admin/avis/{id}/archiver
    """
    return await AdminService.archiver_avis(db, avis_id, admin.id)


@router.post("/avis/purge-archives")
async def purge_avis_archives(
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    """
    Supprime manuellement les avis archivés depuis plus de 7 jours.
    POST /api/admin/avis/purge-archives
    """
    return await AdminService.purge_avis_archives(db)


# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# 18. REQUÊTES MÉDECINS (signalements de bugs / demandes d'assistance)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/requetes")
async def liste_requetes(
    statut: Optional[str] = None,
    db:     AsyncSession  = Depends(get_db),
    admin:  Admin         = Depends(get_current_admin),
):
    from app.models.requete_medecin import RequeteMedecin
    from app.models.medecin import Medecin
    from app.services.admin_service import build_url
    q = (
        select(RequeteMedecin, Medecin.photo_url)
        .outerjoin(Medecin, RequeteMedecin.medecin_id == Medecin.id)
        .order_by(desc(RequeteMedecin.created_at))
    )
    if statut:
        q = q.where(RequeteMedecin.statut == statut)
    result = await db.execute(q)
    rows = result.all()
    return [
        {
            "id":            r.id,
            "medecin_id":    r.medecin_id,
            "nom_medecin":   r.nom_medecin,
            "email_medecin": r.email_medecin,
            "photo_url":     build_url(photo_url),
            "titre":         r.titre,
            "categorie":     r.categorie,
            "description":   r.description,
            "statut":        r.statut,
            "action_admin":  r.action_admin,
            "reponse_admin": r.reponse_admin,
            "repondu_par":   r.repondu_par,
            "repondu_le":    r.repondu_le.isoformat() if r.repondu_le else None,
            "created_at":    r.created_at.isoformat(),
        }
        for r, photo_url in rows
    ]


@router.get("/requetes/count")
async def count_requetes_en_attente(
    db:    AsyncSession = Depends(get_db),
    admin: Admin        = Depends(get_current_admin),
):
    from app.models.requete_medecin import RequeteMedecin
    from sqlalchemy import func
    result = await db.execute(
        select(func.count()).select_from(RequeteMedecin)
        .where(RequeteMedecin.statut == "en_attente")
    )
    return {"count": result.scalar() or 0}


@router.put("/requetes/{req_id}/repondre")
async def repondre_requete(
    req_id: str,
    body:   dict,
    db:     AsyncSession = Depends(get_db),
    admin:  Admin        = Depends(get_current_admin),
):
    from app.models.requete_medecin import RequeteMedecin
    from app.models.notification import Notification

    req = await db.get(RequeteMedecin, req_id)
    if not req:
        raise HTTPException(404, "Requête introuvable")

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    req.action_admin  = body.get("action_admin") or None
    req.reponse_admin = body.get("reponse_admin") or None
    req.statut        = body.get("statut", "resolu")
    req.repondu_par   = admin.id
    req.repondu_le    = now
    if req.statut in ("resolu", "ferme"):
        req.traite_le = now

    db.add(Notification(
        destinataire_id = req.medecin_id,
        type_dest       = "medecin",
        type_notif      = "requete_traitee",
        titre           = "Votre requête a été traitée",
        message         = (
            f"Votre requête « {req.titre} » a reçu une réponse de l'administrateur."
        ),
        meta = {
            "lien":       "/medecin/commentaires",
            "requete_id": req.id,
        },
    ))
    await db.commit()
    return {"message": "Réponse enregistrée avec succès."}


@router.put("/requetes/{req_id}/modifier-reponse")
async def modifier_reponse_requete(
    req_id: str,
    body:   dict,
    db:     AsyncSession = Depends(get_db),
    admin:  Admin        = Depends(get_current_admin),
):
    from app.models.requete_medecin import RequeteMedecin

    req = await db.get(RequeteMedecin, req_id)
    if not req:
        raise HTTPException(404, "Requête introuvable")
    if not req.repondu_le:
        raise HTTPException(400, "Cette requête n'a pas encore reçu de réponse.")

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    req.action_admin  = body.get("action_admin", req.action_admin)
    req.reponse_admin = body.get("reponse_admin", req.reponse_admin)
    req.repondu_par   = admin.id
    req.repondu_le    = now
    nouveau_statut = body.get("statut")
    if nouveau_statut and nouveau_statut in ("en_attente", "en_cours", "resolu", "ferme"):
        req.statut = nouveau_statut
        if nouveau_statut in ("resolu", "ferme") and not req.traite_le:
            req.traite_le = now
    await db.commit()
    return {"message": "Réponse modifiée avec succès."}


@router.put("/requetes/{req_id}/statut")
async def changer_statut_requete(
    req_id: str,
    body:   dict,
    db:     AsyncSession = Depends(get_db),
    admin:  Admin        = Depends(get_current_admin),
):
    from app.models.requete_medecin import RequeteMedecin
    from app.models.notification import Notification

    req = await db.get(RequeteMedecin, req_id)
    if not req:
        raise HTTPException(404, "Requête introuvable")
    nouveau = body.get("statut")
    if nouveau not in ("en_attente", "en_cours", "resolu", "ferme"):
        raise HTTPException(400, "Statut invalide")
    req.statut = nouveau
    if nouveau in ("resolu", "ferme") and not req.traite_le:
        req.traite_le = datetime.now(timezone.utc).replace(tzinfo=None)

    STATUT_LABELS = {
        "en_attente": "En attente",
        "en_cours": "En cours de traitement",
        "resolu": "Résolue",
        "ferme": "Fermée",
    }
    db.add(Notification(
        destinataire_id = req.medecin_id,
        type_dest       = "medecin",
        type_notif      = "requete_statut",
        titre           = f"Requête mise à jour — {STATUT_LABELS.get(nouveau, nouveau)}",
        message         = f"Votre requête « {req.titre} » est maintenant : {STATUT_LABELS.get(nouveau, nouveau)}.",
        meta = {
            "lien":       "/medecin/commentaires",
            "requete_id": req.id,
        },
    ))
    await db.commit()
    return {"message": "Statut mis à jour."}

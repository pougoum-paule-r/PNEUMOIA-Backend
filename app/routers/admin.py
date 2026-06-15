"""
admin_router.py — Routes API pour le panneau d'administration PneumoIA

Organisation :
   1.  Auth                        → login, reset mot de passe
   2.  Demandes en attente         → liste, valider, rejeter
   3.  Validées par mois           → filtrage mois/année
   4.  Refusées                    → liste, supprimer, relancer
   5.  Médecins actifs             → liste enrichie avec stats
   6.  Médecin par ID              → profil complet + documents
   7.  Actions médecins            → suspendre, réactiver, supprimer (→ corbeille)
   8.  Médecins par statut         → endpoint générique
   9.  FAQ — questions             → liste, répondre
   10. FAQ — publiées              → CRUD admin
   11. Statistiques                → consultations, répartition géo, KPIs, top médecins
   12. Paramètres                  → get, update
   13. Notifications               → liste, marquer lue, tout lire
   14. Journal d'audit             → liste, purger
   15. Corbeille                   → liste, restaurer, supprimer définitivement
   16. Avis / commentaires         → liste, supprimer, marquer vus
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional

from app.database import get_db
from app.core.security import get_current_admin, verify_password, create_access_token
from app.models.admin import Admin
from app.models.notification import Notification
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
    Répond à une question de médecin. Email envoyé via Brevo.
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
    return await AdminService.get_top_medecins_concordance(db, limit)


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


@router.delete("/avis/{avis_id}")
async def supprimer_avis(
    avis_id: str,
    db:      AsyncSession = Depends(get_db),
    admin:   Admin        = Depends(get_current_admin),
):
    """
    Supprime un avis. Le médecin est notifié par email.
    DELETE /api/admin/avis/{id}
    """
    return await AdminService.supprimer_avis(db, avis_id, admin.id)


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

"""
admin_service.py — Service d'administration PneumoIA

Organisation :
  1.  Helpers & formatters
  2.  Demandes en attente
  3.  Validées par mois/année
  4.  Médecins par statut (générique)
  5.  Médecins actifs avec stats
  6.  Profil médecin par ID
  7.  Valider un médecin
  8.  Rejeter un médecin
  9.  Dossiers refusés (liste, supprimer, relancer)
  10. Suspendre un médecin
  11. Réactiver un médecin
  12. Supprimer un médecin (→ corbeille soft delete)
  13. Reset mot de passe admin
  14. FAQ — questions médecins
  15. FAQ — publiées admin
  16. Statistiques (consultations, répartition géo, KPIs, top médecins)
  17. Paramètres
  18. Journal d'audit
  19. Corbeille
  20. Avis / commentaires

NOTE : Adaptez les imports des modèles selon votre structure de projet.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, Date
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from datetime import datetime, timedelta
from typing import Optional
import random
import secrets
import calendar
import uuid

from app.models.admin import Admin
from app.models.medecin import Medecin
from app.models.document_medecin import DocumentMedecin
from app.core.security import hash_password
from app.config import settings
from app.services.audit_helper import log_admin_action

# ── Modèles à adapter selon votre projet ─────────────────────────────────────
# from app.models.consultation import Consultation
# from app.models.diagnostic import DiagnosticIA
# from app.models.audit_log import AuditLog
# from app.models.faq import FaqQuestion, FaqPublie
# from app.models.parametre import Parametre
# from app.models.avis import Avis


# ─────────────────────────────────────────────────────────────────────────────
# 1. HELPERS & FORMATTERS
# ─────────────────────────────────────────────────────────────────────────────

LABELS_DOCUMENT = {
    "diplome_specialisation": "Diplôme de spécialisation",
    "diplome_medecine":       "Diplôme de docteur en médecine",
    "inscription_ordre":      "Inscription à l'ordre des médecins",
    "autorisation_exercice":  "Autorisation d'exercice",
    "carte_professionnelle":  "Carte professionnelle",
    "cni":                    "Carte nationale d'identité (CNI)",
}

def build_url(path: str | None) -> str | None:
    if not path: return None
    if path.startswith("http"): return path
    if path.startswith("/"): return f"{settings.BACKEND_URL}{path}"
    return f"{settings.BACKEND_URL}/{path.replace(chr(92), '/')}"

def format_document(d: DocumentMedecin) -> dict:
    return {
        "id":          d.id,
        "type":        d.type_document,
        "label":       LABELS_DOCUMENT.get(d.type_document, d.type_document),
        "url":         build_url(d.url_fichier),
        "nom_fichier": d.nom_fichier,
        "mime_type":   d.mime_type,
        "taille_ko":   round(d.taille_octets / 1024) if d.taille_octets else None,
        "created_at":  d.created_at.isoformat() if d.created_at else None,
    }

def format_medecin(m: Medecin) -> dict:
    """Format de base — utilisé pour demandes en attente et par statut."""
    return {
        "id":            m.id,
        "civilite":      m.civilite,
        "nom":           m.nom,
        "prenom":        m.prenom,
        "email":         m.email,
        "specialite":    m.specialite,
        "numero_rpps":   m.numero_rpps,
        "etablissement": m.etablissement,
        "telephone":     m.telephone,
        "adresse":       m.adresse,
        "bio":           m.bio,
        "linkedin":      m.linkedin,
        "website":       m.website,
        "photo_url":     build_url(m.photo_url),
        "statut":        m.statut,
        "created_at":    m.created_at.isoformat() if m.created_at else None,
        "valide_le":     m.valide_le.isoformat() if m.valide_le else None,
        "valide_par":    m.valideur.email if m.valideur else None,
        "motif_rejet":   m.motif_rejet,
        "suspension_raison": getattr(m, "suspension_raison", None),
        "suspension_duree":  getattr(m, "suspension_duree",  None),
        "suspension_par":    getattr(m, "suspension_par",    None),
        "suspension_le":     getattr(m, "suspension_le", None) and m.suspension_le.isoformat(),
        "documents":     [format_document(d) for d in (m.documents or [])],
    }


class AdminService:

    # ─────────────────────────────────────────────────────────────────────────
    # 2. DEMANDES EN ATTENTE
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_demandes(db: AsyncSession) -> list[dict]:
        """Retourne tous les médecins en attente avec documents et photo."""
        result = await db.execute(
            select(Medecin)
            .where(Medecin.statut == "en_attente")
            .options(selectinload(Medecin.documents))
            .order_by(Medecin.created_at.desc())
        )
        return [format_medecin(m) for m in result.scalars().all()]

    # ─────────────────────────────────────────────────────────────────────────
    # 3. VALIDÉES PAR MOIS / ANNÉE
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_valides(
        db: AsyncSession,
        mois: Optional[int] = None,
        annee: Optional[int] = None,
    ) -> list[dict]:
        """Retourne les médecins validés pour un mois/année donnés."""
        now   = datetime.utcnow()
        m     = mois  or now.month
        y     = annee or now.year
        debut = datetime(y, m, 1)
        fin   = datetime(y + 1, 1, 1) if m == 12 else datetime(y, m + 1, 1)

        result = await db.execute(
            select(Medecin)
            .where(Medecin.statut == "valide", Medecin.valide_le >= debut, Medecin.valide_le < fin)
            .options(selectinload(Medecin.documents), selectinload(Medecin.valideur))
            .order_by(Medecin.valide_le.desc())
        )
        return [format_medecin(m) for m in result.scalars().all()]

    # ─────────────────────────────────────────────────────────────────────────
    # 4. MÉDECINS PAR STATUT (générique)
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_demandes_par_statut(db: AsyncSession, statut: str) -> list[dict]:
        """Retourne les médecins filtrés par statut : en_attente | valide | rejete | suspendu."""
        result = await db.execute(
            select(Medecin)
            .where(Medecin.statut == statut)
            .options(selectinload(Medecin.documents), selectinload(Medecin.valideur))
            .order_by(Medecin.created_at.desc())
        )
        return [format_medecin(m) for m in result.scalars().all()]

    # ─────────────────────────────────────────────────────────────────────────
    # 5. MÉDECINS ACTIFS AVEC STATS
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_medecins_actifs(db: AsyncSession) -> list[dict]:
        """Retourne les médecins validés enrichis avec leurs stats d'activité."""
        result = await db.execute(
            select(Medecin)
            .where(Medecin.statut == "valide")
            .options(
                selectinload(Medecin.consultations).selectinload("diagnostic"),
                selectinload(Medecin.cas_cliniques),
                selectinload(Medecin.valideur),
            )
            .order_by(Medecin.valide_le.desc())
        )
        return [AdminService._format_medecin_actif(m) for m in result.scalars().all()]

    @staticmethod
    def _format_medecin_actif(m: Medecin) -> dict:
        """
        Formate un médecin avec ses stats pour MedecinsActifs et ProfilMedecin.
        - concordance IA  → DiagnosticIA.maladies[0]["pct"] (30 dernières consultations)
        - derniere_activite → date de la consultation la plus récente
        - nb_cas_cliniques  → CasCliniquPublic publiés par ce médecin
        """
        consultations = m.consultations or []
        cas_cliniques = m.cas_cliniques or []

        # Patients uniques
        nb_patients = len(set(c.patient_id for c in consultations if c.patient_id))

        # Concordance IA — maladies[0]["pct"] sur les 30 dernières consultations
        scores = []
        for cons in sorted(consultations, key=lambda x: x.created_at or datetime.min, reverse=True)[:30]:
            if cons.diagnostic and cons.diagnostic.maladies:
                maladies = cons.diagnostic.maladies
                if isinstance(maladies, list) and maladies:
                    pct = maladies[0].get("pct")
                    if pct is not None:
                        scores.append(float(pct))
        concordance_ia = round(sum(scores) / len(scores)) if scores else None

        # Dernière activité
        dates = [c.created_at for c in consultations if c.created_at]
        derniere_activite = max(dates).isoformat() if dates else None

        # Cas cliniques publiés
        nb_cas = len(cas_cliniques)

        # Consultations partagées
        nb_partages = len([c for c in consultations if isinstance(c.partage, dict) and c.partage.get("actif")])

        # Activité récente (5 dernières consultations terminées)
        recentes = sorted(
            [c for c in consultations if c.statut == "terminee"],
            key=lambda c: c.created_at or datetime.min, reverse=True
        )[:5]
        activite_recente = [
            {
                "texte": f"Consultation #{c.id[:8]} enregistrée",
                "quand": c.created_at.strftime("%d/%m/%Y %H:%M") if c.created_at else "—",
            }
            for c in recentes
        ]

        return {
            "id": m.id, "civilite": m.civilite, "nom": m.nom, "prenom": m.prenom,
            "email": m.email, "telephone": m.telephone, "specialite": m.specialite,
            "numero_rpps": m.numero_rpps, "etablissement": m.etablissement, "adresse": m.adresse,
            "photo_url": build_url(m.photo_url), "statut": m.statut,
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "valide_le":  m.valide_le.isoformat()  if m.valide_le  else None,
            "valide_par": m.valideur.email           if m.valideur   else None,
            "nb_patients":      nb_patients,
            "nb_consultations": len(consultations),
            "concordance_ia":   concordance_ia,
            "derniere_activite": derniere_activite,
            "nb_cas_partages":  nb_partages,
            "nb_cas_cliniques": nb_cas,
            "rang_communaute":  f"#{nb_cas}/38" if nb_cas else "—",
            "cas_partages":     f"{nb_cas} cas publiés",
            "activite_recente": activite_recente,
        }

    # ─────────────────────────────────────────────────────────────────────────
    # 6. PROFIL MÉDECIN PAR ID
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_medecin_by_id(db: AsyncSession, medecin_id: str) -> dict:
        """Retourne le profil complet d'un médecin avec stats + documents."""
        result = await db.execute(
            select(Medecin)
            .where(Medecin.id == medecin_id)
            .options(
                selectinload(Medecin.documents),
                selectinload(Medecin.consultations).selectinload("diagnostic"),
                selectinload(Medecin.cas_cliniques),
                selectinload(Medecin.valideur),
            )
        )
        medecin = result.scalar_one_or_none()
        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin introuvable.")

        data = AdminService._format_medecin_actif(medecin)
        data["documents"] = [format_document(d) for d in medecin.documents]
        return data

    # ─────────────────────────────────────────────────────────────────────────
    # 7. VALIDER UN MÉDECIN
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def valider_medecin(db: AsyncSession, medecin_id: str, admin_id: str) -> dict:
        """Valide un médecin — statut passe à 'valide' + email d'activation Brevo."""
        result  = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
        medecin = result.scalar_one_or_none()

        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin introuvable.")
        if medecin.statut != "en_attente":
            raise HTTPException(status_code=400, detail="Ce médecin n'est pas en attente.")

        token = secrets.token_urlsafe(32)
        medecin.statut             = "valide"
        medecin.activation_token   = token
        medecin.activation_expires = datetime.utcnow() + timedelta(days=7)
        medecin.valide_par         = admin_id
        medecin.valide_le          = datetime.utcnow()
        await db.commit()

        lien = f"{settings.FRONTEND_URL}/medecin/activer?token={token}"

        # Email d'activation via Brevo
        email_envoye = False
        try:
            import httpx
            brevo_payload = {
                "sender": {"name": "PneumoIA", "email": settings.ADMIN_EMAIL},
                "to":     [{"email": medecin.email, "name": f"{medecin.prenom} {medecin.nom}"}],
                "subject": "Votre compte PneumoIA a été validé — Activez votre accès",
                "htmlContent": f"""
                    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px">
                      <h2 style="color:#0f766e">PneumoIA — Compte validé !</h2>
                      <p>Bonjour <strong>{medecin.prenom} {medecin.nom}</strong>,</p>
                      <p>Votre demande d'inscription a été <strong>validée</strong> par l'administration.</p>
                      <div style="margin:24px 0">
                        <a href="{lien}"
                           style="background:#0f766e;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:bold">
                          Activer mon compte
                        </a>
                      </div>
                      <p style="color:#6b7280;font-size:12px">Ce lien est valable 7 jours.</p>
                    </div>
                """,
            }
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://api.brevo.com/v3/smtp/email",
                    json=brevo_payload,
                    headers={"api-key": settings.BREVO_API_KEY, "Content-Type": "application/json"},
                    timeout=10,
                )
                email_envoye = resp.status_code in (200, 201)
        except Exception:
            pass

        await log_admin_action(db, admin_id, "demande_validee", medecin_id=medecin.id,
            details={"medecin_nom": f"{medecin.prenom} {medecin.nom}", "email": medecin.email})

        return {
            "message":        "Médecin validé avec succès.",
            "email_envoye":   email_envoye,
            "email_medecin":  medecin.email,
            "lien_activation": lien,
        }

    # ─────────────────────────────────────────────────────────────────────────
    # 8. REJETER UN MÉDECIN
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def rejeter_medecin(db: AsyncSession, medecin_id: str, motif: str) -> dict:
        """Refuse un médecin avec un motif + email de refus Brevo."""
        result  = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
        medecin = result.scalar_one_or_none()

        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin introuvable.")
        if medecin.statut != "en_attente":
            raise HTTPException(status_code=400, detail="Ce médecin n'est pas en attente.")

        medecin.statut      = "rejete"
        medecin.motif_rejet = motif
        await db.commit()

        try:
            import httpx
            brevo_payload = {
                "sender": {"name": "PneumoIA", "email": settings.ADMIN_EMAIL},
                "to":     [{"email": medecin.email, "name": f"{medecin.prenom} {medecin.nom}"}],
                "subject": "Votre demande d'inscription PneumoIA n'a pas été retenue",
                "htmlContent": f"""
                    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px">
                      <h2 style="color:#dc2626">PneumoIA — Demande non retenue</h2>
                      <p>Bonjour <strong>{medecin.prenom} {medecin.nom}</strong>,</p>
                      <p>Votre demande d'inscription n'a pas été retenue pour la raison suivante :</p>
                      <div style="background:#fef2f2;border:1px solid #fca5a5;border-radius:8px;padding:16px;margin:16px 0">
                        <p style="margin:0;color:#dc2626">{motif}</p>
                      </div>
                      <p>Pour toute question, contactez l'administration PneumoIA.</p>
                    </div>
                """,
            }
            async with httpx.AsyncClient() as client:
                await client.post("https://api.brevo.com/v3/smtp/email", json=brevo_payload,
                    headers={"api-key": settings.BREVO_API_KEY, "Content-Type": "application/json"}, timeout=10)
        except Exception:
            pass

        await log_admin_action(db, "system", "demande_rejetee", medecin_id=medecin.id,
            details={"medecin_nom": f"{medecin.prenom} {medecin.nom}", "motif": motif})

        return {"message": "Médecin refusé. Notification envoyée."}

    # ─────────────────────────────────────────────────────────────────────────
    # 9. DOSSIERS REFUSÉS — liste, supprimer, relancer
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_demandes_refusees(
        db: AsyncSession,
        ville: str | None = None,
        motif: str | None = None,
    ) -> list[dict]:
        """Retourne les dossiers refusés avec filtres optionnels ville/motif."""
        query = (
            select(Medecin)
            .where(Medecin.statut == "rejete")
            .options(selectinload(Medecin.documents))
            .order_by(Medecin.updated_at.desc())
        )
        if ville: query = query.where(Medecin.adresse.ilike(f"%{ville}%"))
        if motif: query = query.where(Medecin.motif_rejet == motif)

        result   = await db.execute(query)
        medecins = result.scalars().all()

        return [
            {
                **format_medecin(m),
                "refuse_par":   m.valide_par or "Administrateur",
                "date_demande": m.created_at.strftime("%d/%m/%Y") if m.created_at else "—",
                "date_refus":   m.updated_at.strftime("%d/%m/%Y") if m.updated_at else "—",
                "relance_sent": getattr(m, "relance_sent", False) or False,
            }
            for m in medecins
        ]

    @staticmethod
    async def supprimer_dossier_refuse(db: AsyncSession, medecin_id: str) -> dict:
        """Supprime définitivement un dossier refusé."""
        result  = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
        medecin = result.scalar_one_or_none()

        if not medecin:
            raise HTTPException(status_code=404, detail="Dossier introuvable.")
        if medecin.statut != "rejete":
            raise HTTPException(status_code=400, detail="Ce dossier n'est pas refusé.")

        await db.delete(medecin)
        await db.commit()
        return {"message": f"Dossier de {medecin.prenom} {medecin.nom} supprimé définitivement."}

    @staticmethod
    async def relancer_medecin(db: AsyncSession, medecin_id: str, message: str, admin_id: str) -> dict:
        """Envoie un e-mail de relance au médecin refusé via Brevo."""
        result  = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
        medecin = result.scalar_one_or_none()

        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin introuvable.")
        if medecin.statut != "rejete":
            raise HTTPException(status_code=400, detail="Ce médecin n'est pas dans l'état refusé.")
        if getattr(medecin, "relance_sent", False):
            raise HTTPException(status_code=400, detail="Une relance a déjà été envoyée.")

        import httpx
        brevo_payload = {
            "sender": {"name": "PneumoIA", "email": settings.ADMIN_EMAIL},
            "to":     [{"email": medecin.email, "name": f"{medecin.prenom} {medecin.nom}"}],
            "subject": "Votre demande d'inscription PneumoIA — Relance",
            "htmlContent": f"""
                <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px">
                  <h2 style="color:#0f766e">PneumoIA — Relance d'inscription</h2>
                  <p>Bonjour <strong>{medecin.prenom} {medecin.nom}</strong>,</p>
                  <p>{message.replace(chr(10), "<br/>")}</p>
                  <div style="margin:24px 0">
                    <a href="{settings.FRONTEND_URL}/inscription"
                       style="background:#0f766e;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:bold">
                      Soumettre une nouvelle demande
                    </a>
                  </div>
                  <p style="color:#6b7280;font-size:12px">Motif du refus : <em>{medecin.motif_rejet}</em></p>
                </div>
            """,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.brevo.com/v3/smtp/email",
                json=brevo_payload,
                headers={"api-key": settings.BREVO_API_KEY, "Content-Type": "application/json"},
                timeout=10,
            )
            if resp.status_code not in (200, 201):
                raise HTTPException(502, f"Échec envoi e-mail Brevo : {resp.text}")

        medecin.relance_sent = True
        medecin.relance_at   = datetime.utcnow()
        await db.commit()

        await log_admin_action(db, admin_id, "relance_envoyee", medecin_id=medecin.id,
            details={"email": medecin.email})

        return {"message": f"E-mail de relance envoyé à {medecin.email}.", "relance_sent": True}

    # ─────────────────────────────────────────────────────────────────────────
    # 10. SUSPENDRE UN MÉDECIN
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def suspendre_medecin(
        db: AsyncSession, medecin_id: str,
        raison: str, duree: str, message: str, admin_id: str,
    ) -> dict:
        """Suspend un médecin — statut passe à 'suspendu' + email Brevo."""
        result  = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
        medecin = result.scalar_one_or_none()

        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin introuvable.")
        if medecin.statut == "suspendu":
            raise HTTPException(status_code=400, detail="Ce médecin est déjà suspendu.")

        medecin.statut            = "suspendu"
        medecin.suspension_raison = raison
        medecin.suspension_duree  = duree
        medecin.suspension_par    = admin_id
        medecin.suspension_le     = datetime.utcnow()
        await db.commit()

        try:
            import httpx
            brevo_payload = {
                "sender": {"name": "PneumoIA", "email": settings.ADMIN_EMAIL},
                "to":     [{"email": medecin.email, "name": f"{medecin.prenom} {medecin.nom}"}],
                "subject": "Votre accès PneumoIA a été suspendu",
                "htmlContent": f"""
                    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px">
                      <h2 style="color:#ea580c">PneumoIA — Suspension de compte</h2>
                      <p>Bonjour <strong>{medecin.prenom} {medecin.nom}</strong>,</p>
                      <p>Votre accès a été <strong>suspendu</strong>.</p>
                      <div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;padding:16px;margin:16px 0">
                        <p style="margin:0;color:#c2410c"><strong>Motif :</strong> {raison}</p>
                        <p style="margin:8px 0 0;color:#c2410c"><strong>Durée :</strong> {duree}</p>
                        {f'<p style="margin:8px 0 0;color:#92400e">{message}</p>' if message else ''}
                      </div>
                      <p>Pour contester cette décision, contactez l'administration.</p>
                    </div>
                """,
            }
            async with httpx.AsyncClient() as client:
                await client.post("https://api.brevo.com/v3/smtp/email", json=brevo_payload,
                    headers={"api-key": settings.BREVO_API_KEY, "Content-Type": "application/json"}, timeout=10)
        except Exception:
            pass

        await log_admin_action(db, admin_id, "medecin_suspendu", medecin_id=medecin.id,
            details={"medecin_nom": f"{medecin.prenom} {medecin.nom}", "raison": raison, "duree": duree})

        return {"message": f"Médecin suspendu pour : {raison} — {duree}.", "statut": "suspendu"}

    # ─────────────────────────────────────────────────────────────────────────
    # 11. RÉACTIVER UN MÉDECIN
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def reactiver_medecin(db: AsyncSession, medecin_id: str, admin_id: str) -> dict:
        """Réactive un médecin suspendu — statut repasse à 'valide' + email Brevo."""
        result  = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
        medecin = result.scalar_one_or_none()

        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin introuvable.")
        if medecin.statut != "suspendu":
            raise HTTPException(status_code=400, detail="Ce médecin n'est pas suspendu.")

        raison_initiale           = medecin.suspension_raison or "—"
        medecin.statut            = "valide"
        medecin.suspension_raison = None
        medecin.suspension_duree  = None
        medecin.suspension_par    = None
        medecin.suspension_le     = None
        await db.commit()

        try:
            import httpx
            brevo_payload = {
                "sender": {"name": "PneumoIA", "email": settings.ADMIN_EMAIL},
                "to":     [{"email": medecin.email, "name": f"{medecin.prenom} {medecin.nom}"}],
                "subject": "Votre compte PneumoIA a été réactivé",
                "htmlContent": f"""
                    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px">
                      <h2 style="color:#0f766e">PneumoIA — Réactivation de compte</h2>
                      <p>Bonjour <strong>{medecin.prenom} {medecin.nom}</strong>,</p>
                      <p>Votre accès a été <strong>réactivé</strong> par l'administration.</p>
                      <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:16px;margin:16px 0">
                        <p style="margin:0;color:#065f46"><strong>Motif initial de la suspension :</strong> {raison_initiale}</p>
                      </div>
                      <div style="margin:24px 0">
                        <a href="{settings.FRONTEND_URL}/connexion"
                           style="background:#0f766e;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:bold">
                          Se connecter
                        </a>
                      </div>
                    </div>
                """,
            }
            async with httpx.AsyncClient() as client:
                await client.post("https://api.brevo.com/v3/smtp/email", json=brevo_payload,
                    headers={"api-key": settings.BREVO_API_KEY, "Content-Type": "application/json"}, timeout=10)
        except Exception:
            pass

        await log_admin_action(db, admin_id, "medecin_reactive", medecin_id=medecin.id,
            details={"medecin_nom": f"{medecin.prenom} {medecin.nom}", "email": medecin.email})

        return {"message": "Médecin réactivé avec succès. Notification envoyée.", "statut": "valide"}

    # ─────────────────────────────────────────────────────────────────────────
    # 12. SUPPRIMER UN MÉDECIN (soft delete → corbeille)
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def supprimer_medecin(db: AsyncSession, medecin_id: str, admin_id: str) -> dict:
        """
        Déplace le médecin en corbeille (statut = 'corbeille').
        Conserve statut_precedent pour permettre la restauration.
        La suppression définitive se fait depuis /corbeille/{id}.
        """
        result  = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
        medecin = result.scalar_one_or_none()

        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin introuvable.")
        if medecin.statut == "corbeille":
            raise HTTPException(status_code=400, detail="Ce médecin est déjà dans la corbeille.")

        # Sauvegarde du statut pour restauration future
        medecin.statut_precedent = medecin.statut
        medecin.statut           = "corbeille"
        medecin.supprime_le      = datetime.utcnow()
        medecin.supprime_par     = admin_id
        await db.commit()

        await log_admin_action(db, admin_id, "medecin_corbeille", medecin_id=medecin.id,
            details={"medecin_nom": f"{medecin.prenom} {medecin.nom}", "statut_precedent": medecin.statut_precedent})

        return {
            "message": f"{medecin.prenom} {medecin.nom} déplacé en corbeille. Restaurable sous 30 jours.",
            "statut":  "corbeille",
        }

    # ─────────────────────────────────────────────────────────────────────────
    # 13. RESET MOT DE PASSE ADMIN
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def request_password_reset(db: AsyncSession, email: str, phone: str) -> str:
        """Génère un OTP 6 chiffres valable 10 min, stocké sur l'admin."""
        result = await db.execute(select(Admin).where(Admin.email == email))
        admin  = result.scalar_one_or_none()

        if not admin:
            raise HTTPException(status_code=400, detail="Aucun compte trouvé avec cet email.")
        if not admin.phone:
            raise HTTPException(status_code=400, detail="Aucun numéro associé à ce compte.")
        if admin.phone != phone:
            raise HTTPException(status_code=400, detail="Numéro de téléphone incorrect.")

        otp = "".join(random.choices("0123456789", k=6))
        admin.reset_otp  = otp
        admin.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        await db.commit()
        return otp

    @staticmethod
    async def send_otp_sms(otp: str, phone: str) -> None:
        """Envoie l'OTP par SMS via Twilio."""
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=f"PneumoIA — Votre code de réinitialisation : {otp}\nValide 10 minutes.",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone,
        )

    @staticmethod
    async def verify_and_update_password(
        db: AsyncSession, email: str, otp: str, new_password: str
    ) -> None:
        """Vérifie l'OTP et met à jour le mot de passe de l'admin."""
        result = await db.execute(select(Admin).where(Admin.email == email))
        admin  = result.scalar_one_or_none()

        if not admin or admin.reset_otp != otp:
            raise HTTPException(status_code=400, detail="Code OTP invalide.")
        if admin.otp_expiry and datetime.utcnow() > admin.otp_expiry:
            raise HTTPException(status_code=400, detail="Code OTP expiré. Recommencez la procédure.")

        admin.password_hash = hash_password(new_password)
        admin.reset_otp     = None
        admin.otp_expiry    = None
        await db.commit()

    # ─────────────────────────────────────────────────────────────────────────
    # 14. FAQ — QUESTIONS DES MÉDECINS
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_questions(
        db:        AsyncSession,
        statut:    Optional[str] = None,
        categorie: Optional[str] = None,
        ville:     Optional[str] = None,
    ) -> list[dict]:
        """Retourne les questions posées par les médecins avec filtres optionnels."""
        from app.models.faq import FaqQuestion  # adapte si nécessaire

        query = select(FaqQuestion).order_by(FaqQuestion.created_at.desc())
        if statut:    query = query.where(FaqQuestion.statut == statut)
        if categorie: query = query.where(FaqQuestion.categorie == categorie)
        if ville:     query = query.where(FaqQuestion.ville.ilike(f"%{ville}%"))

        result = await db.execute(query)
        return [
            {
                "id":         q.id,
                "question":   q.question,
                "auteur":     q.auteur or "Médecin",
                "email":      q.email,
                "ville":      q.ville,
                "categorie":  q.categorie,
                "statut":     q.statut,
                "reponse":    q.reponse,
                "created_at": q.created_at.isoformat() if q.created_at else None,
            }
            for q in result.scalars().all()
        ]

    @staticmethod
    async def repondre_question(
        db: AsyncSession, question_id: str, reponse: str, admin_id: str
    ) -> dict:
        """Enregistre la réponse à une question médecin."""
        from app.models.faq import FaqQuestion

        result = await db.execute(select(FaqQuestion).where(FaqQuestion.id == question_id))
        q      = result.scalar_one_or_none()
        if not q:
            raise HTTPException(404, "Question introuvable.")

        q.reponse    = reponse
        q.statut     = "repondu"
        q.repondu_le = datetime.utcnow()
        await db.commit()

        await log_admin_action(db, admin_id, "faq_repondu",
            details={"question_id": question_id})
        return {"message": "Réponse enregistrée."}

    # ─────────────────────────────────────────────────────────────────────────
    # 15. FAQ — PUBLIÉES PAR L'ADMIN
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_faq(db: AsyncSession) -> list[dict]:
        """Retourne toutes les entrées FAQ (publiées + brouillons)."""
        from app.models.faq import FaqPublie

        result = await db.execute(select(FaqPublie).order_by(FaqPublie.created_at.desc()))
        return [
            {
                "id":         f.id,
                "question":   f.question,
                "reponse":    f.reponse,
                "categorie":  f.categorie,
                "publie":     f.publie,
                "created_at": f.created_at.isoformat() if f.created_at else None,
            }
            for f in result.scalars().all()
        ]

    @staticmethod
    async def creer_faq(
        db: AsyncSession,
        question: str, reponse: str,
        categorie: str, publie: bool, admin_id: str,
    ) -> dict:
        """Crée une nouvelle entrée FAQ publiée."""
        from app.models.faq import FaqPublie

        faq = FaqPublie(
            id=str(uuid.uuid4()), question=question, reponse=reponse,
            categorie=categorie, publie=publie, created_by=admin_id,
            created_at=datetime.utcnow(),
        )
        db.add(faq)
        await db.commit()
        await db.refresh(faq)
        return {"message": "FAQ créée.", "id": faq.id}

    @staticmethod
    async def modifier_faq(
        db: AsyncSession, faq_id: str,
        question: str, reponse: str,
        categorie: str, publie: bool, admin_id: str,
    ) -> dict:
        """Modifie une entrée FAQ existante."""
        from app.models.faq import FaqPublie

        result = await db.execute(select(FaqPublie).where(FaqPublie.id == faq_id))
        faq    = result.scalar_one_or_none()
        if not faq:
            raise HTTPException(404, "FAQ introuvable.")

        faq.question  = question
        faq.reponse   = reponse
        faq.categorie = categorie
        faq.publie    = publie
        faq.updated_at = datetime.utcnow()
        await db.commit()
        return {"message": "FAQ mise à jour."}

    @staticmethod
    async def toggle_faq_publie(db: AsyncSession, faq_id: str, admin_id: str) -> dict:
        """Bascule l'état publié/brouillon d'une entrée FAQ."""
        from app.models.faq import FaqPublie

        result = await db.execute(select(FaqPublie).where(FaqPublie.id == faq_id))
        faq    = result.scalar_one_or_none()
        if not faq:
            raise HTTPException(404, "FAQ introuvable.")

        faq.publie = not faq.publie
        await db.commit()
        return {"publie": faq.publie}

    @staticmethod
    async def vider_faq(db: AsyncSession, admin_id: str) -> dict:
        """Supprime toutes les entrées FAQ définitivement."""
        from app.models.faq import FaqPublie

        result = await db.execute(select(FaqPublie))
        faqs   = result.scalars().all()
        for f in faqs:
            await db.delete(f)
        await db.commit()
        return {"message": f"{len(faqs)} entrée(s) FAQ supprimées."}

    @staticmethod
    async def supprimer_faq(db: AsyncSession, faq_id: str, admin_id: str) -> dict:
        """Supprime définitivement une entrée FAQ."""
        from app.models.faq import FaqPublie

        result = await db.execute(select(FaqPublie).where(FaqPublie.id == faq_id))
        faq    = result.scalar_one_or_none()
        if not faq:
            raise HTTPException(404, "FAQ introuvable.")
        await db.delete(faq)
        await db.commit()
        return {"message": "FAQ supprimée."}

    # ─────────────────────────────────────────────────────────────────────────
    # 16. STATISTIQUES
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_kpis(db: AsyncSession) -> dict:
        """
        4 KPIs principaux du dashboard.
        Retourne : { medecins_actifs, demandes_en_attente, consultations_total, precision_ia }
        """
        from app.models.consultation import Consultation  # adapte l'import

        medecins_actifs     = await db.scalar(select(func.count()).select_from(Medecin).where(Medecin.statut == "valide"))        or 0
        demandes_en_attente = await db.scalar(select(func.count()).select_from(Medecin).where(Medecin.statut == "en_attente"))    or 0
        consultations_total = await db.scalar(select(func.count()).select_from(Consultation))                                     or 0

        # Précision IA — moyenne de maladies[0]["pct"] sur les 100 dernières consultations
        try:
            from app.models.diagnostic_ia import DiagnosticIA
            recentes = (await db.execute(
                select(DiagnosticIA).order_by(DiagnosticIA.created_at.desc()).limit(100)
            )).scalars().all()
            scores = []
            for d in recentes:
                maladies = d.maladies or []
                if isinstance(maladies, list) and maladies:
                    pct = maladies[0].get("pct")
                    if pct is not None:
                        scores.append(float(pct))
            precision_ia = round(sum(scores) / len(scores)) if scores else 0
        except Exception:
            precision_ia = 0

        return {
            "medecins_actifs":     medecins_actifs,
            "demandes_en_attente": demandes_en_attente,
            "consultations_total": consultations_total,
            "precision_ia":        precision_ia,
        }

    @staticmethod
    async def get_consultations_semaine(db: AsyncSession) -> dict:
        """
        Consultations par jour sur les 30 derniers jours.
        Retourne : { jours: [{ j: "Lun", c: 432 }, ...] }
        """
        from app.models.consultation import Consultation

        JOURS_FR = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        result = []

        for i in range(29, -1, -1):
            d     = (datetime.utcnow() - timedelta(days=i)).date()
            count = await db.scalar(
                select(func.count()).select_from(Consultation)
                .where(cast(Consultation.date_consultation, Date) == d)
            ) or 0
            result.append({"j": JOURS_FR[d.weekday()], "c": count})

        return {"jours": result}

    @staticmethod
    async def get_consultations_annee(db: AsyncSession, year: int) -> dict:
        """
        Consultations agrégées par mois pour une année.
        Retourne : { mois: [4820, 5200, 0, 0, ...] } — 12 valeurs, 0 pour les mois futurs.
        """
        from app.models.consultation import Consultation

        mois_data = []
        for m in range(1, 13):
            debut = datetime(year, m, 1)
            fin   = datetime(year, m, calendar.monthrange(year, m)[1], 23, 59, 59)
            count = await db.scalar(
                select(func.count()).select_from(Consultation)
                .where(
                    Consultation.date_consultation >= debut,
                    Consultation.date_consultation <= fin,
                )
            ) or 0
            mois_data.append(count)

        return {"mois": mois_data}

    @staticmethod
    async def get_consultations_total(
        db: AsyncSession, from_date: str, to_date: str
    ) -> dict:
        """
        KPIs consultations sur une période : total, moyenne/jour, pic, variation vs période précédente.
        Retourne : { total, moyenne_par_jour, pic, variation_vs_mois_precedent }
        """
        from app.models.consultation import Consultation
        from datetime import date as date_type

        d_from = datetime.strptime(from_date, "%Y-%m-%d").date()
        d_to   = datetime.strptime(to_date,   "%Y-%m-%d").date()

        # Nombre de consultations par jour sur la période
        rows = (await db.execute(
            select(
                cast(Consultation.date_consultation, Date).label("jour"),
                func.count().label("nb"),
            )
            .where(
                Consultation.date_consultation >= datetime.combine(d_from, datetime.min.time()),
                Consultation.date_consultation <= datetime.combine(d_to,   datetime.max.time()),
            )
            .group_by("jour")
        )).all()

        total    = sum(r.nb for r in rows)
        nb_jours = (d_to - d_from).days + 1
        pic      = max((r.nb for r in rows), default=0)
        moyenne  = round(total / nb_jours) if nb_jours else 0

        # Variation vs même durée le mois précédent
        delta      = timedelta(days=nb_jours)
        prec_to    = d_from - timedelta(days=1)
        prec_from  = prec_to - delta + timedelta(days=1)
        total_prec = await db.scalar(
            select(func.count()).select_from(Consultation)
            .where(
                Consultation.date_consultation >= datetime.combine(prec_from, datetime.min.time()),
                Consultation.date_consultation <= datetime.combine(prec_to,   datetime.max.time()),
            )
        ) or 0
        variation = round((total - total_prec) / total_prec * 100) if total_prec else 0

        return {
            "total":                       total,
            "moyenne_par_jour":            moyenne,
            "pic":                         pic,
            "variation_vs_mois_precedent": variation,
        }

    @staticmethod
    async def get_repartition_geo(
        db: AsyncSession,
        mois:  Optional[int] = None,
        annee: Optional[int] = None,
    ) -> dict:
        """
        Médecins validés groupés par ville + couverture par région.
        Retourne : { villes: [...], regions: [...] }
        """
        from app.models.consultation import Consultation

        now   = datetime.utcnow()
        m     = mois  or now.month
        y     = annee or now.year
        debut = datetime(y, m, 1)
        fin   = datetime(y, m, calendar.monthrange(y, m)[1], 23, 59, 59)

        result   = await db.execute(select(Medecin).where(Medecin.statut == "valide"))
        medecins = result.scalars().all()

        # Agrégation par ville (adresse = ville ou adresse complète)
        ville_map: dict[str, dict] = {}
        for md in medecins:
            ville  = (md.adresse or "Inconnue").split(",")[-1].strip()
            region = getattr(md, "region", "") or ""
            if ville not in ville_map:
                ville_map[ville] = {"ville": ville, "region": region, "medecins": 0, "consultations": 0}
            ville_map[ville]["medecins"] += 1
            count = await db.scalar(
                select(func.count()).select_from(Consultation)
                .where(
                    Consultation.medecin_id == md.id,
                    Consultation.date_consultation >= debut,
                    Consultation.date_consultation <= fin,
                )
            ) or 0
            ville_map[ville]["consultations"] += count

        villes = [
            {"ville": v["ville"], "region": v["region"],
             "medecins": v["medecins"], "consultations": v["consultations"], "patients": 0}
            for v in ville_map.values()
        ]

        # Couverture par région (10 régions du Cameroun)
        REGIONS_CAMEROUN = [
            "Littoral", "Centre", "Ouest", "Nord", "Est",
            "Sud", "Adamaoua", "Extrême-Nord", "Nord-Ouest", "Sud-Ouest",
        ]
        region_md: dict[str, int] = {}
        for md in medecins:
            reg = getattr(md, "region", None) or ""
            if reg:
                region_md[reg] = region_md.get(reg, 0) + 1

        total_md = len(medecins) or 1
        regions  = [
            {
                "region":     r,
                "medecins":   region_md.get(r, 0),
                "couverture": round(region_md.get(r, 0) / total_md * 100),
            }
            for r in REGIONS_CAMEROUN
        ]

        return {"villes": villes, "regions": regions}

    @staticmethod
    async def get_top_medecins_concordance(db: AsyncSession, limit: int = 5) -> list[dict]:
        """
        Top N médecins triés par concordance IA décroissante.
        Retourne : [{ id, nom, prenom, specialite, photo_url, concordance_ia, nb_consultations }]
        """
        result = await db.execute(
            select(Medecin)
            .where(Medecin.statut == "valide")
            .options(selectinload(Medecin.consultations).selectinload("diagnostic"))
        )
        medecins = result.scalars().all()

        enriched = []
        for md in medecins:
            consultations = md.consultations or []
            scores = []
            for c in sorted(consultations, key=lambda x: x.created_at or datetime.min, reverse=True)[:30]:
                if c.diagnostic and c.diagnostic.maladies:
                    maladies = c.diagnostic.maladies
                    if isinstance(maladies, list) and maladies:
                        pct = maladies[0].get("pct")
                        if pct is not None:
                            scores.append(float(pct))
            if not scores:
                continue
            enriched.append({
                "id":               md.id,
                "nom":              md.nom,
                "prenom":           md.prenom,
                "specialite":       md.specialite,
                "photo_url":        build_url(md.photo_url),
                "concordance_ia":   round(sum(scores) / len(scores)),
                "nb_consultations": len(consultations),
                "tendance":         "+",  # à calculer si tu as des données historiques
            })

        enriched.sort(key=lambda x: x["concordance_ia"], reverse=True)
        return enriched[:limit]

    # ─────────────────────────────────────────────────────────────────────────
    # 17. PARAMÈTRES
    # ─────────────────────────────────────────────────────────────────────────

    # Valeurs par défaut utilisées si la table est vide
    _PARAMS_DEFAULTS = {
        "inscriptions_ouvertes":    True,
        "validation_manuelle":      True,
        "delai_inactivite_jours":   14,
        "duree_corbeille_jours":    30,
        "relance_autorisee":        True,
        "notif_nouvelle_demande":   True,
        "notif_nouveau_commentaire": True,
        "notif_nouvelle_faq":       True,
        "notif_expiration_corbeille": True,
        "notif_medecin_inactif":    True,
        "fuseau_horaire":           "Africa/Douala",
        "format_date":              "DD/MM/YYYY",
        "format_heure":             "24h",
        "langue":                   "fr",
        "double_auth":              True,
        "session_max":              True,
        "audit_complet":            True,
        "email_bienvenue":          True,
        "notif_refus":              True,
        "notif_suspension":         True,
    }

    @staticmethod
    async def get_parametres(db: AsyncSession) -> dict:
        """Retourne les paramètres globaux, avec fallback sur les valeurs par défaut."""
        from app.models.parametre import Parametre  # adapte si nécessaire

        try:
            result = await db.execute(select(Parametre).where(Parametre.cle == "global"))
            param  = result.scalar_one_or_none()
            if param and param.valeur:
                return {**AdminService._PARAMS_DEFAULTS, **param.valeur}
        except Exception:
            pass
        return AdminService._PARAMS_DEFAULTS.copy()

    @staticmethod
    async def update_parametres(db: AsyncSession, body: dict, admin_id: str) -> dict:
        """Met à jour les paramètres globaux (upsert sur la clé "global")."""
        from app.models.parametre import Parametre

        try:
            result = await db.execute(select(Parametre).where(Parametre.cle == "global"))
            param  = result.scalar_one_or_none()

            if param:
                param.valeur     = body
                param.updated_at = datetime.utcnow()
            else:
                param = Parametre(id=str(uuid.uuid4()), cle="global", valeur=body, updated_at=datetime.utcnow())
                db.add(param)

            await db.commit()
        except Exception:
            pass  # Table absente → fonctionne en mode sans persistance

        await log_admin_action(db, admin_id, "parametres_mis_a_jour",
            details={"champs": list(body.keys())})
        return {"message": "Paramètres mis à jour avec succès."}

    # ─────────────────────────────────────────────────────────────────────────
    # 18. JOURNAL D'AUDIT
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_audit_logs(
        db:     AsyncSession,
        type:   Optional[str] = None,
        statut: Optional[str] = None,
    ) -> dict:
        """
        Retourne les entrées du journal d'audit avec filtres optionnels.
        Retourne : { logs: [{ id, action, acteur, date, statut, type }] }
        """
        from app.models.audit_log import AuditLog  # adapte si nécessaire

        query = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(200)
        if type:   query = query.where(AuditLog.type   == type)
        if statut: query = query.where(AuditLog.statut == statut)

        result = await db.execute(query)
        logs   = result.scalars().all()

        return {
            "logs": [
                {
                    "id":     l.id,
                    "action": l.action,
                    "acteur": l.acteur or "Système",
                    "date":   l.created_at.isoformat() if l.created_at else None,
                    "statut": l.statut or "info",
                    "type":   l.type   or "info",
                }
                for l in logs
            ]
        }

    @staticmethod
    async def purger_audit_logs(db: AsyncSession, days: int, admin_id: str) -> dict:
        """Supprime les entrées du journal antérieures à N jours (0 = tout purger)."""
        from app.models.audit_log import AuditLog

        cutoff = datetime.utcnow() - timedelta(days=days) if days > 0 else datetime.max
        if days == 0:
            # Purge complète
            result = await db.execute(select(AuditLog))
        else:
            result = await db.execute(select(AuditLog).where(AuditLog.created_at < cutoff))

        old_logs = result.scalars().all()
        count    = len(old_logs)

        for log in old_logs:
            await db.delete(log)
        await db.commit()

        await log_admin_action(db, admin_id, "audit_purge",
            details={"jours": days, "supprimes": count})

        return {"message": f"{count} entrée(s) supprimée(s) ({f'> {days} jours' if days else 'tout'}).", "count": count}

    # ─────────────────────────────────────────────────────────────────────────
    # 19. CORBEILLE
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_corbeille(db: AsyncSession) -> list[dict]:
        """
        Retourne les médecins en corbeille (soft delete, restaurables).
        Inclut le nombre de jours restants avant suppression définitive automatique.
        """
        result = await db.execute(
            select(Medecin)
            .where(Medecin.statut == "corbeille")
            .options(selectinload(Medecin.documents))
            .order_by(Medecin.supprime_le.desc())
        )
        medecins = result.scalars().all()

        now = datetime.utcnow()
        return [
            {
                **format_medecin(m),
                "statut_precedent":   getattr(m, "statut_precedent", "valide"),
                "supprime_le":        m.supprime_le.isoformat() if m.supprime_le else None,
                "supprime_par":       getattr(m, "supprime_par", None),
                # Jours restants avant suppression auto (30j par défaut)
                "jours_restants":     max(0, 30 - (now - m.supprime_le).days) if m.supprime_le else 30,
            }
            for m in medecins
        ]

    @staticmethod
    async def restaurer_medecin(db: AsyncSession, medecin_id: str, admin_id: str) -> dict:
        """Restaure un médecin depuis la corbeille — reprend son statut précédent."""
        result  = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
        medecin = result.scalar_one_or_none()

        if not medecin:
            raise HTTPException(404, "Médecin introuvable.")
        if medecin.statut != "corbeille":
            raise HTTPException(400, "Ce médecin n'est pas dans la corbeille.")

        statut_restaure = getattr(medecin, "statut_precedent", None) or "valide"
        medecin.statut           = statut_restaure
        medecin.statut_precedent = None
        medecin.supprime_le      = None
        medecin.supprime_par     = None
        await db.commit()

        await log_admin_action(db, admin_id, "medecin_restaure", medecin_id=medecin.id,
            details={"medecin_nom": f"{medecin.prenom} {medecin.nom}", "statut_restaure": statut_restaure})

        return {
            "message": f"{medecin.prenom} {medecin.nom} restauré avec le statut '{statut_restaure}'.",
            "statut":  statut_restaure,
        }

    @staticmethod
    async def supprimer_definitif(db: AsyncSession, medecin_id: str, admin_id: str) -> dict:
        """Supprime définitivement un médecin depuis la corbeille + email Brevo."""
        result  = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
        medecin = result.scalar_one_or_none()

        if not medecin:
            raise HTTPException(404, "Médecin introuvable.")
        if medecin.statut != "corbeille":
            raise HTTPException(400, "Ce médecin n'est pas dans la corbeille.")

        email, prenom, nom_med = medecin.email, medecin.prenom, medecin.nom
        await db.delete(medecin)
        await db.commit()

        try:
            import httpx
            brevo_payload = {
                "sender": {"name": "PneumoIA", "email": settings.ADMIN_EMAIL},
                "to":     [{"email": email, "name": f"{prenom} {nom_med}"}],
                "subject": "Votre compte PneumoIA a été supprimé",
                "htmlContent": f"""
                    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px">
                      <h2 style="color:#dc2626">PneumoIA — Suppression de compte</h2>
                      <p>Bonjour <strong>{prenom} {nom_med}</strong>,</p>
                      <p>Votre compte PneumoIA a été <strong>supprimé définitivement</strong>.</p>
                      <div style="background:#fef2f2;border:1px solid #fca5a5;border-radius:8px;padding:16px;margin:16px 0">
                        <p style="margin:0;color:#dc2626">Toutes vos données ont été effacées de notre système.</p>
                      </div>
                      <p>Pour toute question, contactez l'administration PneumoIA.</p>
                    </div>
                """,
            }
            async with httpx.AsyncClient() as client:
                await client.post("https://api.brevo.com/v3/smtp/email", json=brevo_payload,
                    headers={"api-key": settings.BREVO_API_KEY, "Content-Type": "application/json"}, timeout=10)
        except Exception:
            pass

        await log_admin_action(db, admin_id, "medecin_supprime",
            details={"medecin_nom": f"{prenom} {nom_med}", "email": email})

        return {"message": "Compte médecin supprimé définitivement."}

    # ─────────────────────────────────────────────────────────────────────────
    # 20. AVIS / COMMENTAIRES
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_avis(db: AsyncSession) -> list[dict]:
        """
        Retourne tous les avis publiés par les médecins.
        Retourne : [{ id, prenom, nom, photo_url, specialite, hopital, ville, note, commentaire, created_at, vu }]
        """
        from app.models.avis import Avis  # adapte si nécessaire

        result = await db.execute(select(Avis).order_by(Avis.created_at.desc()))
        return [
            {
                "id":          a.id,
                "prenom":      a.prenom,
                "nom":         a.nom,
                "photo_url":   build_url(a.photo_url),
                "specialite":  a.specialite,
                "hopital":     getattr(a, "hopital",  None),
                "ville":       getattr(a, "ville",    None),
                "note":        a.note,
                "commentaire": a.commentaire,
                "created_at":  a.created_at.isoformat() if a.created_at else None,
                "vu":          a.vu,
            }
            for a in result.scalars().all()
        ]

    @staticmethod
    async def supprimer_avis(db: AsyncSession, avis_id: str, admin_id: str) -> dict:
        """Supprime un avis médecin."""
        from app.models.avis import Avis

        result = await db.execute(select(Avis).where(Avis.id == avis_id))
        avis   = result.scalar_one_or_none()
        if not avis:
            raise HTTPException(404, "Avis introuvable.")

        await db.delete(avis)
        await db.commit()

        await log_admin_action(db, admin_id, "avis_supprime",
            details={"avis_id": avis_id})
        return {"message": "Avis supprimé."}

    @staticmethod
    async def marquer_avis_vus(db: AsyncSession) -> dict:
        """Marque tous les avis non vus comme vus."""
        from app.models.avis import Avis

        result = await db.execute(select(Avis).where(Avis.vu == False))
        avis   = result.scalars().all()
        count  = len(avis)

        for a in avis:
            a.vu = True
        await db.commit()

        return {"message": f"{count} avis marqué(s) comme vu(s).", "count": count}

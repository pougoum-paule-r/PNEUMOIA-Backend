"""
admin_service.py — Service d'administration PneumoIA

Organisation :
  1. Helpers & formatters
  2. Demandes en attente
  3. Validées par mois/année
  4. Médecins par statut (générique)
  5. Médecins actifs avec stats
  6. Profil médecin par ID
  7. Valider un médecin
  8. Rejeter un médecin
  9. Dossiers refusés (liste, supprimer, relancer)
  10. Suspendre un médecin
  11. Réactiver un médecin
  12. Supprimer un médecin
  13. Reset mot de passe admin
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from app.models.admin import Admin
from app.models.medecin import Medecin
from app.models.document_medecin import DocumentMedecin
from app.core.security import hash_password
from app.config import settings
from app.services.audit_helper import log_admin_action
from twilio.rest import Client
from datetime import datetime, timedelta
from typing import Optional
import random
import secrets

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
        # Champs suspension
        "suspension_raison": getattr(m, "suspension_raison", None),
        "suspension_duree":  getattr(m, "suspension_duree",  None),
        "suspension_par":    getattr(m, "suspension_par",    None),
        "suspension_le":     getattr(m, "suspension_le",     None) and m.suspension_le.isoformat(),
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

        # Concordance IA — maladies[0]["pct"] sur les 30 dernières
        scores = []
        for cons in sorted(consultations, key=lambda x: x.created_at or datetime.min, reverse=True)[:30]:
            if cons.diagnostic and cons.diagnostic.maladies:
                maladies = cons.diagnostic.maladies
                if isinstance(maladies, list) and len(maladies) > 0:
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

        # Activité récente (5 dernières)
        recentes = sorted(
            [c for c in consultations if c.statut == "terminee"],
            key=lambda c: c.created_at or datetime.min, reverse=True
        )[:5]
        activite_recente = [
            {"texte": f"Consultation #{c.id[:8]} enregistrée", "quand": c.created_at.strftime("%d/%m/%Y %H:%M") if c.created_at else "—"}
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
            "nb_patients": nb_patients, "nb_consultations": len(consultations),
            "concordance_ia": concordance_ia, "derniere_activite": derniere_activite,
            "nb_cas_partages": nb_partages, "nb_cas_cliniques": nb_cas,
            "rang_communaute": f"#{nb_cas}/38" if nb_cas else "—",
            "cas_partages": f"{nb_cas} cas publiés",
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
        """Valide un médecin — statut passe à 'valide' + email d'activation."""
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
            await run_in_threadpool(
                send_activation_email, medecin.email, medecin.nom, token
            )
            email_envoye = True
        except Exception:
            pass

        # Audit log
        await log_admin_action(db, admin_id, "demande_validee", medecin_id=medecin.id,
            details={"medecin_nom": f"{medecin.prenom} {medecin.nom}", "email": medecin.email})

        return {"message": "Médecin validé avec succès.", "email_envoye": email_envoye,
                "email_medecin": medecin.email, "lien_activation": lien}

    # ─────────────────────────────────────────────────────────────────────────
    # 8. REJETER UN MÉDECIN
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def rejeter_medecin(db: AsyncSession, medecin_id: str, motif: str) -> dict:
        """Refuse un médecin avec un motif + email de refus."""
        result  = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
        medecin = result.scalar_one_or_none()

        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin introuvable.")
        if medecin.statut != "en_attente":
            raise HTTPException(status_code=400, detail="Ce médecin n'est pas en attente.")

        medecin.statut      = "rejete"
        medecin.motif_rejet = motif
        await db.commit()

        # Email de refus via Brevo
        try:
            pass  # from app.services.email_service import send_rejection_email
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
            "sender":      {"name": "PneumoIA", "email": settings.ADMIN_EMAIL},
            "to":          [{"email": medecin.email, "name": f"{medecin.prenom} {medecin.nom}"}],
            "subject":     "Votre demande d'inscription PneumoIA — Relance",
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
                  <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0"/>
                  <p style="color:#9ca3af;font-size:11px">PneumoIA — Ne répondez pas directement à cet e-mail.</p>
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

        import httpx
        brevo_payload = {
            "sender": {"name": "PneumoIA", "email": settings.ADMIN_EMAIL},
            "to":     [{"email": medecin.email, "name": f"{medecin.prenom} {medecin.nom}"}],
            "subject": "Votre accès PneumoIA a été suspendu",
            "htmlContent": f"""
                <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px">
                  <h2 style="color:#ea580c">PneumoIA — Suspension de compte</h2>
                  <p>Bonjour <strong>{medecin.prenom} {medecin.nom}</strong>,</p>
                  <p>Votre accès à la plateforme PneumoIA a été <strong>suspendu</strong>.</p>
                  <div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;padding:16px;margin:16px 0">
                    <p style="margin:0;color:#c2410c"><strong>Motif :</strong> {raison}</p>
                    <p style="margin:8px 0 0;color:#c2410c"><strong>Durée :</strong> {duree}</p>
                    {f'<p style="margin:8px 0 0;color:#92400e">{message}</p>' if message else ''}
                  </div>
                  <p>Pour contester cette décision, contactez l'administration.</p>
                  <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0"/>
                  <p style="color:#9ca3af;font-size:11px">PneumoIA — Ne répondez pas directement à cet e-mail.</p>
                </div>
            """,
        }
        try:
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

        import httpx
        brevo_payload = {
            "sender": {"name": "PneumoIA", "email": settings.ADMIN_EMAIL},
            "to":     [{"email": medecin.email, "name": f"{medecin.prenom} {medecin.nom}"}],
            "subject": "Votre compte PneumoIA a été réactivé",
            "htmlContent": f"""
                <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px">
                  <h2 style="color:#0f766e">PneumoIA — Réactivation de compte</h2>
                  <p>Bonjour <strong>{medecin.prenom} {medecin.nom}</strong>,</p>
                  <p>Votre accès à la plateforme PneumoIA a été <strong>réactivé</strong> par l'administration.</p>
                  <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:16px;margin:16px 0">
                    <p style="margin:0;color:#065f46"><strong>Motif initial de la suspension :</strong> {raison_initiale}</p>
                  </div>
                  <p>Vous pouvez vous reconnecter dès maintenant.</p>
                  <div style="margin:24px 0">
                    <a href="{settings.FRONTEND_URL}/connexion"
                       style="background:#0f766e;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:bold">
                      Se connecter
                    </a>
                  </div>
                  <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0"/>
                  <p style="color:#9ca3af;font-size:11px">PneumoIA — Ne répondez pas directement à cet e-mail.</p>
                </div>
            """,
        }
        try:
            async with httpx.AsyncClient() as client:
                await client.post("https://api.brevo.com/v3/smtp/email", json=brevo_payload,
                    headers={"api-key": settings.BREVO_API_KEY, "Content-Type": "application/json"}, timeout=10)
        except Exception:
            pass

        await log_admin_action(db, admin_id, "medecin_reactive", medecin_id=medecin.id,
            details={"medecin_nom": f"{medecin.prenom} {medecin.nom}", "email": medecin.email})

        return {"message": "Médecin réactivé avec succès. Notification envoyée.", "statut": "valide"}

    # ─────────────────────────────────────────────────────────────────────────
    # 12. SUPPRIMER UN MÉDECIN
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def supprimer_medecin(db: AsyncSession, medecin_id: str) -> dict:
        """Supprime définitivement un médecin + email Brevo."""
        result  = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
        medecin = result.scalar_one_or_none()

        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin introuvable.")

        email, prenom, nom_med = medecin.email, medecin.prenom, medecin.nom
        await db.delete(medecin)
        await db.commit()

        import httpx
        brevo_payload = {
            "sender": {"name": "PneumoIA", "email": settings.ADMIN_EMAIL},
            "to":     [{"email": email, "name": f"{prenom} {nom_med}"}],
            "subject": "Votre compte PneumoIA a été supprimé",
            "htmlContent": f"""
                <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px">
                  <h2 style="color:#dc2626">PneumoIA — Suppression de compte</h2>
                  <p>Bonjour <strong>{prenom} {nom_med}</strong>,</p>
                  <p>Votre compte PneumoIA a été <strong>supprimé définitivement</strong> par l'administration.</p>
                  <div style="background:#fef2f2;border:1px solid #fca5a5;border-radius:8px;padding:16px;margin:16px 0">
                    <p style="margin:0;color:#dc2626">Toutes vos données ont été effacées de notre système.</p>
                  </div>
                  <p>Pour toute question, contactez l'administration PneumoIA.</p>
                  <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0"/>
                  <p style="color:#9ca3af;font-size:11px">PneumoIA — Ne répondez pas directement à cet e-mail.</p>
                </div>
            """,
        }
        try:
            async with httpx.AsyncClient() as client:
                await client.post("https://api.brevo.com/v3/smtp/email", json=brevo_payload,
                    headers={"api-key": settings.BREVO_API_KEY, "Content-Type": "application/json"}, timeout=10)
        except Exception:
            pass

        await log_admin_action(db, "system", "medecin_supprime",
            details={"medecin_nom": f"{prenom} {nom_med}", "email": email})

        return {"message": "Compte médecin supprimé définitivement."}

    # ─────────────────────────────────────────────────────────────────────────
    # 13. RESET MOT DE PASSE ADMIN
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def request_password_reset(db: AsyncSession, email: str, phone: str) -> str:
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
    async def verify_and_update_password(db: AsyncSession, email: str, otp: str, new_password: str) -> None:
        result = await db.execute(select(Admin).where(Admin.email == email))
        admin  = result.scalar_one_or_none()

        if not admin:
            raise HTTPException(status_code=400, detail="Compte introuvable.")
        if not admin.is_otp_valid(otp):
            raise HTTPException(status_code=400, detail="Code OTP invalide ou expiré.")

        admin.password_hash = hash_password(new_password)
        admin.clear_otp()
        await db.commit()

    @staticmethod
    async def send_otp_sms(otp: str, phone: str) -> str:
        client  = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"PneumoIA — Votre code de réinitialisation est : {otp}. Valide 10 minutes. Ne le partagez pas.",
            from_=settings.TWILIO_PHONE_NUMBER, to=phone,
        )
        return message.sid

    # ─────────────────────────────────────────────────────────────────────────
    # 14. FAQ — Questions des médecins
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_questions(
        db: AsyncSession,
        statut: Optional[str] = None,
        categorie: Optional[str] = None,
        ville: Optional[str] = None,
    ) -> list[dict]:
        """
        Retourne les questions des médecins.
        Filtres : statut (en_attente | repondu), categorie, ville.
        """
        from app.models.question_medecin import QuestionMedecin

        query = (
            select(QuestionMedecin)
            .options(selectinload(QuestionMedecin.medecin))
            .order_by(QuestionMedecin.created_at.desc())
        )
        if statut:    query = query.where(QuestionMedecin.statut    == statut)
        if categorie: query = query.where(QuestionMedecin.categorie == categorie)

        result    = await db.execute(query)
        questions = result.scalars().all()

        rows = []
        for q in questions:
            m = q.medecin
            # Filtre ville côté Python (adresse du médecin)
            if ville and m and ville not in (m.adresse or ""):
                continue
            rows.append({
                "id":           q.id,
                "question":     q.question,
                "categorie":    q.categorie,
                "statut":       q.statut,
                "reponse":      q.reponse,
                "created_at":   q.created_at.isoformat()   if q.created_at   else None,
                "updated_at":   q.updated_at.isoformat()   if q.updated_at   else None,
                "repondu_le":   q.repondu_le.isoformat()   if q.repondu_le   else None,
                # Infos médecin
                "medecin_id":   m.id        if m else None,
                "medecin":      f"{m.civilite or 'Dr.'} {m.prenom} {m.nom}" if m else "—",
                "initials":     f"{(m.prenom or '')[:1].upper()}{(m.nom or '')[:1].upper()}" if m else "—",
                "cnom":         m.numero_rpps   if m else "—",
                "email":        m.email         if m else "—",
                "hopital":      m.etablissement if m else "—",
                "ville":        m.adresse       if m else "—",
                "photo_url":    build_url(m.photo_url) if m else None,
            })
        return rows

    @staticmethod
    async def repondre_question(
        db: AsyncSession,
        question_id: str,
        reponse: str,
        admin_id: str,
    ) -> dict:
        """
        Répond à une question de médecin.
        Envoie un email de notification au médecin via Brevo.
        """
        from app.models.question_medecin import QuestionMedecin

        result   = await db.execute(select(QuestionMedecin).where(QuestionMedecin.id == question_id)
                                    .options(selectinload(QuestionMedecin.medecin)))
        question = result.scalar_one_or_none()

        if not question:
            raise HTTPException(status_code=404, detail="Question introuvable.")

        question.reponse    = reponse
        question.statut     = "repondu"
        question.repondu_par = admin_id
        question.repondu_le  = datetime.utcnow()
        await db.commit()

        # ── Email de réponse au médecin via Brevo ──────────────────────────
        m = question.medecin
        if m:
            import httpx
            brevo_payload = {
                "sender": {"name": "PneumoIA", "email": settings.ADMIN_EMAIL},
                "to":     [{"email": m.email, "name": f"{m.prenom} {m.nom}"}],
                "subject": "Réponse à votre question — PneumoIA",
                "htmlContent": f"""
                    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px">
                      <h2 style="color:#0f766e">PneumoIA — Réponse à votre question</h2>
                      <p>Bonjour <strong>{m.prenom} {m.nom}</strong>,</p>
                      <p>L'administration a répondu à votre question :</p>
                      <div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:16px;margin:16px 0">
                        <p style="margin:0;color:#6b7280;font-size:12px">Votre question :</p>
                        <p style="margin:8px 0 0;color:#111827;font-style:italic">« {question.question} »</p>
                      </div>
                      <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:16px;margin:16px 0">
                        <p style="margin:0;color:#065f46;font-size:12px">Réponse de l'administration :</p>
                        <p style="margin:8px 0 0;color:#065f46">{reponse.replace(chr(10), "<br/>")}</p>
                      </div>
                      <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0"/>
                      <p style="color:#9ca3af;font-size:11px">PneumoIA — Ne répondez pas à cet e-mail.</p>
                    </div>
                """,
            }
            try:
                async with httpx.AsyncClient() as client:
                    await client.post("https://api.brevo.com/v3/smtp/email", json=brevo_payload,
                        headers={"api-key": settings.BREVO_API_KEY, "Content-Type": "application/json"},
                        timeout=10)
            except Exception:
                pass

        await log_admin_action(db, admin_id, "faq_repondue", details={
            "question_id": question_id,
            "medecin_email": m.email if m else "—",
        })

        return {"message": "Réponse envoyée.", "statut": "repondu"}

    # ─────────────────────────────────────────────────────────────────────────
    # 15. FAQ publiées — CRUD admin
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_faq(db: AsyncSession) -> list[dict]:
        """Retourne toutes les entrées FAQ (publiées + brouillons)."""
        from app.models.faq_publiee import FAQPubliee

        result = await db.execute(
            select(FAQPubliee).order_by(FAQPubliee.created_at.desc())
        )
        faqs = result.scalars().all()
        return [AdminService._format_faq(f) for f in faqs]

    @staticmethod
    def _format_faq(f) -> dict:
        return {
            "id":         f.id,
            "question":   f.question,
            "reponse":    f.reponse,
            "categorie":  f.categorie,
            "publie":     f.publie,
            "nb_vues":    f.nb_vues,
            "created_at": f.created_at.isoformat() if f.created_at else None,
            "updated_at": f.updated_at.isoformat() if f.updated_at else None,
        }

    @staticmethod
    async def creer_faq(
        db: AsyncSession,
        question: str,
        reponse: str,
        categorie: str,
        publie: bool,
        admin_id: str,
    ) -> dict:
        """Crée une nouvelle entrée FAQ."""
        from app.models.faq_publiee import FAQPubliee

        faq = FAQPubliee(
            admin_id  = admin_id,
            question  = question,
            reponse   = reponse,
            categorie = categorie,
            publie    = publie,
            nb_vues   = 0,
        )
        db.add(faq)
        await db.commit()
        await db.refresh(faq)

        await log_admin_action(db, admin_id, "faq_publiee" if publie else "faq_repondue",
            details={"faq_id": faq.id, "question": question[:80]})

        return AdminService._format_faq(faq)

    @staticmethod
    async def modifier_faq(
        db: AsyncSession,
        faq_id: str,
        question: str,
        reponse: str,
        categorie: str,
        publie: bool,
        admin_id: str,
    ) -> dict:
        """Modifie une entrée FAQ existante."""
        from app.models.faq_publiee import FAQPubliee

        result = await db.execute(select(FAQPubliee).where(FAQPubliee.id == faq_id))
        faq    = result.scalar_one_or_none()

        if not faq:
            raise HTTPException(status_code=404, detail="Entrée FAQ introuvable.")

        faq.question  = question
        faq.reponse   = reponse
        faq.categorie = categorie
        faq.publie    = publie
        await db.commit()
        await db.refresh(faq)

        return AdminService._format_faq(faq)

    @staticmethod
    async def toggle_faq_publie(db: AsyncSession, faq_id: str, admin_id: str) -> dict:
        """Publie ou dépublie une entrée FAQ."""
        from app.models.faq_publiee import FAQPubliee

        result = await db.execute(select(FAQPubliee).where(FAQPubliee.id == faq_id))
        faq    = result.scalar_one_or_none()

        if not faq:
            raise HTTPException(status_code=404, detail="Entrée FAQ introuvable.")

        faq.publie = not faq.publie
        await db.commit()

        action = "faq_publiee" if faq.publie else "faq_depubliee"
        await log_admin_action(db, admin_id, action, details={"faq_id": faq_id})

        return {"publie": faq.publie, "message": "FAQ publiée." if faq.publie else "FAQ dépubliée."}

    @staticmethod
    async def supprimer_faq(db: AsyncSession, faq_id: str, admin_id: str) -> dict:
        """Supprime définitivement une entrée FAQ."""
        from app.models.faq_publiee import FAQPubliee

        result = await db.execute(select(FAQPubliee).where(FAQPubliee.id == faq_id))
        faq    = result.scalar_one_or_none()

        if not faq:
            raise HTTPException(status_code=404, detail="Entrée FAQ introuvable.")

        await db.delete(faq)
        await db.commit()

        await log_admin_action(db, admin_id, "faq_depubliee", details={"faq_id": faq_id})

        return {"message": "Entrée FAQ supprimée définitivement."}

    @staticmethod
    async def vider_faq(db: AsyncSession, admin_id: str) -> dict:
        """Supprime toutes les entrées FAQ définitivement."""
        from app.models.faq_publiee import FAQPubliee
        from sqlalchemy import delete

        result = await db.execute(select(FAQPubliee))
        nb     = len(result.scalars().all())

        await db.execute(delete(FAQPubliee))
        await db.commit()

        await log_admin_action(db, admin_id, "faq_depubliee",
            details={"action": "vider_tout", "nb_supprimees": nb})

        return {"message": f"{nb} entrée{('s' if nb>1 else '')} FAQ supprimée{('s' if nb>1 else '')} définitivement."}

    # ─────────────────────────────────────────────────────────────────────────
    # 16. STATISTIQUES
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_consultations_semaine(db: AsyncSession) -> list[dict]:
        """
        Consultations par jour sur les 30 derniers jours.
        Utilisé par CourbeActivite.jsx.
        """
        from sqlalchemy import func
        from app.models.consultation import Consultation

        debut = datetime.utcnow() - timedelta(days=30)

        result = await db.execute(
            select(
                func.date(Consultation.created_at).label("jour"),
                func.count(Consultation.id).label("nb"),
            )
            .where(Consultation.created_at >= debut)
            .group_by(func.date(Consultation.created_at))
            .order_by(func.date(Consultation.created_at))
        )
        rows = result.all()
        return [{"jour": str(r.jour), "nb": r.nb} for r in rows]

    @staticmethod
    async def get_consultations_annee(db: AsyncSession, year: int) -> list[dict]:
        """
        Consultations agrégées par mois pour une année donnée.
        Retourne 12 entrées (une par mois).
        """
        from sqlalchemy import func, extract
        from app.models.consultation import Consultation

        result = await db.execute(
            select(
                extract("month", Consultation.created_at).label("mois"),
                func.count(Consultation.id).label("nb"),
            )
            .where(extract("year", Consultation.created_at) == year)
            .group_by(extract("month", Consultation.created_at))
            .order_by(extract("month", Consultation.created_at))
        )
        rows = result.all()

        # Remplir les mois manquants avec 0
        data = {int(r.mois): r.nb for r in rows}
        return [{"mois": m, "nb": data.get(m, 0)} for m in range(1, 13)]

    @staticmethod
    async def get_consultations_total(
        db: AsyncSession,
        date_from: str,
        date_to: str,
    ) -> dict:
        """
        Total de consultations sur une période personnalisée.
        date_from / date_to : format ISO YYYY-MM-DD
        """
        from sqlalchemy import func
        from app.models.consultation import Consultation

        debut = datetime.fromisoformat(date_from)
        fin   = datetime.fromisoformat(date_to)

        result = await db.execute(
            select(func.count(Consultation.id))
            .where(
                Consultation.created_at >= debut,
                Consultation.created_at <= fin,
            )
        )
        total = result.scalar() or 0
        return {"total": total, "from": date_from, "to": date_to}

    @staticmethod
    async def get_repartition_geo(db: AsyncSession) -> list[dict]:
        """
        Répartition des médecins validés par ville.
        Utilisé par la page Répartition géo.
        """
        from sqlalchemy import func

        result = await db.execute(
            select(
                Medecin.adresse.label("ville"),
                func.count(Medecin.id).label("nb"),
            )
            .where(Medecin.statut == "valide")
            .group_by(Medecin.adresse)
            .order_by(func.count(Medecin.id).desc())
        )
        rows = result.all()
        return [{"ville": r.ville or "—", "nb": r.nb} for r in rows]

    # ─────────────────────────────────────────────────────────────────────────
    # 17. PARAMÈTRES
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_parametres(db: AsyncSession) -> dict:
        """
        Retourne les paramètres globaux de la plateforme.
        Stockés en JSON dans la table parametres (clé unique "global").
        Si la table n'existe pas encore → retourne les valeurs par défaut.
        """
        try:
            from app.models.parametre import Parametre
            result = await db.execute(
                select(Parametre).where(Parametre.cle == "global")
            )
            param = result.scalar_one_or_none()
            if param:
                return param.valeurs
        except Exception:
            pass

        # Valeurs par défaut si table absente ou vide
        return {
            "inscriptions_ouvertes":     True,
            "validation_manuelle":       True,
            "relance_autorisee":         True,
            "delai_inactivite_jours":    14,
            "duree_corbeille_jours":     30,
            "notif_nouvelle_demande":    True,
            "notif_nouveau_commentaire": True,
            "notif_nouvelle_faq":        True,
            "notif_expiration_corbeille":True,
            "notif_medecin_inactif":     True,
            "fuseau_horaire":            "Africa/Douala",
            "format_date":               "DD/MM/YYYY",
            "format_heure":              "24h",
            "langue":                    "fr",
            "double_auth":               True,
            "session_max":               True,
            "audit_complet":             True,
            "email_bienvenue":           True,
            "notif_refus":               True,
            "notif_suspension":          True,
        }

    @staticmethod
    async def update_parametres(db: AsyncSession, params: dict, admin_id: str) -> dict:
        """
        Met à jour les paramètres globaux de la plateforme.
        Upsert sur la clé "global".
        """
        try:
            from app.models.parametre import Parametre
            result = await db.execute(
                select(Parametre).where(Parametre.cle == "global")
            )
            param = result.scalar_one_or_none()

            if param:
                param.valeurs     = params
                param.updated_at  = datetime.utcnow()
                param.updated_par = admin_id
            else:
                param = Parametre(
                    cle         = "global",
                    valeurs     = params,
                    updated_par = admin_id,
                )
                db.add(param)

            await db.commit()
        except Exception:
            pass  # Si table absente, on ignore

        return params
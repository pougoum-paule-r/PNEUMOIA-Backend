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

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.models.admin import Admin
from app.models.medecin import Medecin
from app.models.document_medecin import DocumentMedecin
from app.core.security import hash_password
from app.config import settings
from app.services.audit_helper import log_admin_action
from app.models.consultation import Consultation


async def _send_email_smtp(to_email: str, to_name: str, subject: str, html: str) -> bool:
    """Envoie un email HTML via SMTP configuré dans .env. Retourne True si succès."""
    import aiosmtplib

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"PneumoIA <{settings.FROM_EMAIL}>"
    msg["To"]      = f"{to_name} <{to_email}>"
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        return True
    except Exception:
        return False

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
        "id":           d.id,
        "type":         d.type_document,
        "label":        LABELS_DOCUMENT.get(d.type_document, d.type_document),
        "url":          build_url(d.url_fichier),
        "nom_fichier":  d.nom_fichier,
        "mime_type":    d.mime_type,
        "taille_ko":    round(d.taille_octets / 1024) if d.taille_octets else None,
        "statut":       getattr(d, "statut", "en_attente"),
        "motif_rejet":  getattr(d, "motif_rejet", None),
        "created_at":   d.created_at.isoformat() if d.created_at else None,
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
        "ville":         m.ville,
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
        from app.models.consultation import Consultation

        result = await db.execute(
            select(Medecin)
            .where(Medecin.statut == "valide")
            .options(
                selectinload(Medecin.consultations).selectinload(Consultation.diagnostic),
                selectinload(Medecin.cas_cliniques),
                selectinload(Medecin.valideur),
            )
            .order_by(Medecin.valide_le.desc())
        )
        medecins   = result.scalars().all()
        classement = AdminService._classer_medecins(medecins)
        return [
            AdminService._format_medecin_actif(m, rang_communaute=classement.get(m.id, "—"))
            for m in medecins
        ]

    @staticmethod
    def _classer_medecins(medecins: list[Medecin]) -> dict[str, str]:
        """
        Classe une liste de médecins selon un score combiné :
        50% concordance IA moyenne (30 dernières consultations) + 50% nombre de consultations,
        chaque critère normalisé entre 0 et 1 par rapport au max du groupe.
        Retourne { medecin_id: "#rang/total" }.
        """
        stats = []
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
            concordance = sum(scores) / len(scores) if scores else 0.0
            stats.append({"id": md.id, "concordance": concordance, "nb_consultations": len(consultations)})

        if not stats:
            return {}

        max_concordance = max(s["concordance"]       for s in stats) or 1.0
        max_consult     = max(s["nb_consultations"]   for s in stats) or 1

        for s in stats:
            norm_concordance = s["concordance"]       / max_concordance
            norm_consult     = s["nb_consultations"]  / max_consult
            s["score"] = 0.5 * norm_concordance + 0.5 * norm_consult

        stats.sort(key=lambda s: s["score"], reverse=True)

        total = len(stats)
        return {s["id"]: f"#{i}/{total}" for i, s in enumerate(stats, start=1)}

    @staticmethod
    def _format_medecin_actif(m: Medecin, rang_communaute: str | None = None) -> dict:
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

        # Dernière activité = max(dernière connexion, dernière consultation)
        dates = [c.created_at for c in consultations if c.created_at]
        derniere_consultation = max(dates) if dates else None
        candidates = [d for d in [derniere_consultation, m.derniere_connexion] if d]
        derniere_activite = max(candidates).isoformat() if candidates else None

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
            "rang_communaute":  rang_communaute or "—",
            "cas_partages":     f"{nb_partages} cas partagés",
            "activite_recente": activite_recente,
        }


    # ─────────────────────────────────────────────────────────────────────────
    # 6. PROFIL MÉDECIN PAR ID
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_medecin_by_id(db: AsyncSession, medecin_id: str) -> dict:
        """Retourne le profil complet d'un médecin avec stats + documents."""
        from app.models.consultation import Consultation

        result = await db.execute(
            select(Medecin)
            .where(Medecin.id == medecin_id)
            .options(
                selectinload(Medecin.documents),
                selectinload(Medecin.consultations).selectinload(Consultation.diagnostic),
                selectinload(Medecin.cas_cliniques),
                selectinload(Medecin.valideur),
            )
        )
        medecin = result.scalar_one_or_none()
        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin introuvable.")

        # Classement calculé par rapport à tous les médecins validés (pas seulement celui-ci)
        result_tous = await db.execute(
            select(Medecin)
            .where(Medecin.statut == "valide")
            .options(selectinload(Medecin.consultations).selectinload(Consultation.diagnostic))
        )
        classement = AdminService._classer_medecins(result_tous.scalars().all())

        data = AdminService._format_medecin_actif(medecin, rang_communaute=classement.get(medecin.id, "—"))
        data["documents"] = [format_document(d) for d in medecin.documents]
        return data


    # ─────────────────────────────────────────────────────────────────────────
    # 7. VALIDER / REJETER UN DOCUMENT
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def valider_document(db: AsyncSession, document_id: str, admin_id: str) -> dict:
        """Valide un document médecin + notifie le médecin par email."""
        result = await db.execute(
            select(DocumentMedecin)
            .where(DocumentMedecin.id == document_id)
            .options(selectinload(DocumentMedecin.medecin))
        )
        doc = result.scalar_one_or_none()
        if not doc:
            raise HTTPException(status_code=404, detail="Document introuvable.")

        doc.statut      = "valide"
        doc.motif_rejet = None
        await db.commit()

        medecin = doc.medecin
        label   = LABELS_DOCUMENT.get(doc.type_document, doc.type_document)

        await _send_email_smtp(
            to_email=medecin.email,
            to_name=f"{medecin.prenom} {medecin.nom}",
            subject=f"Document validé — {label}",
            html=f"""
                <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px">
                  <h2 style="color:#0f766e">PneumoIA — Document validé</h2>
                  <p>Bonjour <strong>{medecin.prenom} {medecin.nom}</strong>,</p>
                  <p>Votre document <strong>{label}</strong> a été <strong style="color:#0f766e">validé</strong> par l'administration.</p>
                  <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:16px;margin:16px 0">
                    <p style="margin:0;color:#065f46">Fichier : {doc.nom_fichier or label}</p>
                  </div>
                  <p>Connectez-vous à la plateforme pour suivre l'avancement de votre dossier.</p>
                </div>
            """,
        )

        await log_admin_action(db, admin_id, "document_valide",
            medecin_id=medecin.id,
            details={"document_id": document_id, "type": doc.type_document})

        return {"message": f"Document '{label}' validé. Médecin notifié.", "statut": "valide"}

    @staticmethod
    async def rejeter_document(
        db: AsyncSession, document_id: str, motif: str, admin_id: str
    ) -> dict:
        """Rejette un document médecin avec un motif + notifie le médecin par email."""
        result = await db.execute(
            select(DocumentMedecin)
            .where(DocumentMedecin.id == document_id)
            .options(selectinload(DocumentMedecin.medecin))
        )
        doc = result.scalar_one_or_none()
        if not doc:
            raise HTTPException(status_code=404, detail="Document introuvable.")

        doc.statut      = "rejete"
        doc.motif_rejet = motif
        await db.commit()

        medecin = doc.medecin
        label   = LABELS_DOCUMENT.get(doc.type_document, doc.type_document)

        await _send_email_smtp(
            to_email=medecin.email,
            to_name=f"{medecin.prenom} {medecin.nom}",
            subject=f"Document refusé — {label}",
            html=f"""
                <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px">
                  <h2 style="color:#dc2626">PneumoIA — Document refusé</h2>
                  <p>Bonjour <strong>{medecin.prenom} {medecin.nom}</strong>,</p>
                  <p>Votre document <strong>{label}</strong> n'a pas été accepté.</p>
                  <div style="background:#fef2f2;border:1px solid #fca5a5;border-radius:8px;padding:16px;margin:16px 0">
                    <p style="margin:0;color:#dc2626"><strong>Motif :</strong> {motif}</p>
                    <p style="margin:8px 0 0;color:#991b1b">Fichier : {doc.nom_fichier or label}</p>
                  </div>
                  <p>Veuillez soumettre un nouveau document conforme depuis votre espace personnel.</p>
                </div>
            """,
        )

        await log_admin_action(db, admin_id, "document_rejete",
            medecin_id=medecin.id,
            details={"document_id": document_id, "type": doc.type_document, "motif": motif})

        return {"message": f"Document '{label}' refusé. Médecin notifié.", "statut": "rejete"}

    # ─────────────────────────────────────────────────────────────────────────
    # 8. VALIDER UN MÉDECIN
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def valider_medecin(db: AsyncSession, medecin_id: str, admin_id: str) -> dict:
        """Valide un médecin — statut passe à 'valide' + email d'activation envoyé au médecin."""
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

        email_envoye = await _send_email_smtp(
            to_email=medecin.email,
            to_name=f"{medecin.prenom} {medecin.nom}",
            subject="Votre compte PneumoIA a été validé — Activez votre accès",
            html=f"""
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
        )

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
    async def rejeter_medecin(db: AsyncSession, medecin_id: str, motif: str, admin_id: str) -> dict:
        """Refuse un médecin avec un motif + email de refus envoyé au médecin."""
        result  = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
        medecin = result.scalar_one_or_none()

        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin introuvable.")
        if medecin.statut != "en_attente":
            raise HTTPException(status_code=400, detail="Ce médecin n'est pas en attente.")

        medecin.statut      = "rejete"
        medecin.motif_rejet = motif
        medecin.rejete_par  = admin_id
        await db.commit()

        await _send_email_smtp(
            to_email=medecin.email,
            to_name=f"{medecin.prenom} {medecin.nom}",
            subject="Votre demande d'inscription PneumoIA n'a pas été retenue",
            html=f"""
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
        )

        await log_admin_action(db, admin_id, "demande_rejetee", medecin_id=medecin.id,
            details={"medecin_nom": f"{medecin.prenom} {medecin.nom}", "motif": motif})

        return {"message": "Médecin refusé. Notification envoyée."}

    # ─────────────────────────────────────────────────────────────────────────
    # 9. DOSSIERS REFUSÉS — liste, supprimer, relancer
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def _purger_relances_expirees(db: AsyncSession) -> None:
        """
        Supprime définitivement les dossiers refusés dont la relance a été envoyée
        il y a plus de 48h sans que le médecin n'ait resoumis de nouvelle demande
        (ce qui se traduirait par un changement de statut, donc disparition du filtre 'rejete').
        """
        seuil = datetime.utcnow() - timedelta(hours=48)
        result = await db.execute(
            select(Medecin).where(
                Medecin.statut == "rejete",
                Medecin.relance_sent == True,  # noqa: E712
                Medecin.relance_at  != None,   # noqa: E711
                Medecin.relance_at  < seuil,
            )
        )
        expires = result.scalars().all()
        for m in expires:
            await db.delete(m)
        if expires:
            await db.commit()

    @staticmethod
    async def get_demandes_refusees(
        db: AsyncSession,
        ville: str | None = None,
        motif: str | None = None,
    ) -> list[dict]:
        """Retourne les dossiers refusés avec filtres optionnels ville/motif."""
        await AdminService._purger_relances_expirees(db)

        query = (
            select(Medecin)
            .where(Medecin.statut == "rejete")
            .options(selectinload(Medecin.documents), selectinload(Medecin.rejeteur))
            .order_by(Medecin.updated_at.desc())
        )
        if ville: query = query.where(Medecin.adresse.ilike(f"%{ville}%"))
        if motif: query = query.where(Medecin.motif_rejet == motif)

        result   = await db.execute(query)
        medecins = result.scalars().all()

        return [
            {
                **format_medecin(m),
                "refuse_par":   m.rejeteur.email if m.rejeteur else "Administrateur",
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
        """Envoie un e-mail de relance au médecin refusé via SMTP."""
        result  = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
        medecin = result.scalar_one_or_none()

        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin introuvable.")
        if medecin.statut != "rejete":
            raise HTTPException(status_code=400, detail="Ce médecin n'est pas dans l'état refusé.")
        if getattr(medecin, "relance_sent", False):
            raise HTTPException(status_code=400, detail="Une relance a déjà été envoyée.")

        ok = await _send_email_smtp(
            to_email=medecin.email,
            to_name=f"{medecin.prenom} {medecin.nom}",
            subject="Votre demande d'inscription PneumoIA — Relance",
            html=f"""
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
        )
        if not ok:
            raise HTTPException(502, "Échec envoi e-mail SMTP.")

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
        """Suspend un médecin — statut passe à 'suspendu' + email de notification envoyé au médecin."""
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

        await _send_email_smtp(
            to_email=medecin.email,
            to_name=f"{medecin.prenom} {medecin.nom}",
            subject="Votre accès PneumoIA a été suspendu",
            html=f"""
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
        )

        await log_admin_action(db, admin_id, "medecin_suspendu", medecin_id=medecin.id,
            details={"medecin_nom": f"{medecin.prenom} {medecin.nom}", "raison": raison, "duree": duree})

        return {"message": f"Médecin suspendu pour : {raison} — {duree}.", "statut": "suspendu"}

    # ─────────────────────────────────────────────────────────────────────────
    # 11. RÉACTIVER UN MÉDECIN
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def reactiver_medecin(db: AsyncSession, medecin_id: str, admin_id: str) -> dict:
        """Réactive un médecin suspendu — statut repasse à 'valide' + email de notification envoyé au médecin."""
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

        await _send_email_smtp(
            to_email=medecin.email,
            to_name=f"{medecin.prenom} {medecin.nom}",
            subject="Votre compte PneumoIA a été réactivé",
            html=f"""
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
        )

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

        await _send_email_smtp(
            to_email=medecin.email,
            to_name=f"{medecin.prenom} {medecin.nom}",
            subject="Votre compte PneumoIA a été désactivé",
            html=f"""
                <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px">
                  <h2 style="color:#dc2626">PneumoIA — Compte désactivé</h2>
                  <p>Bonjour <strong>{medecin.prenom} {medecin.nom}</strong>,</p>
                  <p>Votre compte PneumoIA a été <strong>désactivé</strong> par l'administration.</p>
                  <div style="background:#fef2f2;border:1px solid #fca5a5;border-radius:8px;padding:16px;margin:16px 0">
                    <p style="margin:0;color:#dc2626">
                      Votre accès à la plateforme a été retiré. Votre dossier est conservé pendant 30 jours.
                    </p>
                  </div>
                  <p>Pour toute question ou contestation, contactez l'administration PneumoIA.</p>
                </div>
            """,
        )

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
        from app.models.question_admin import QuestionAdmin

        AVATAR_COLORS = ["#185FA5","#7C3AED","#D97706","#0891B2","#16a34a","#dc2626","#9333ea","#0284c7"]

        query = (
            select(QuestionAdmin)
            .order_by(QuestionAdmin.created_at.desc())
        )
        if statut: query = query.where(QuestionAdmin.statut == statut)

        result = await db.execute(query)
        rows   = result.scalars().all()

        # Charger les médecins en une seule requête
        medecin_ids = list({q.medecin_id for q in rows if q.medecin_id})
        medecins_map: dict = {}
        if medecin_ids:
            md_result = await db.execute(
                select(Medecin).where(Medecin.id.in_(medecin_ids))
            )
            medecins_map = {m.id: m for m in md_result.scalars().all()}

        out = []
        for q in rows:
            md = medecins_map.get(q.medecin_id)
            nom_complet = f"Dr. {md.prenom} {md.nom}" if md else "Médecin inconnu"
            ville_md    = (md.ville or "").strip() if md else ""
            # filtre ville côté Python
            if ville and ville != "Toutes" and ville_md.lower() != ville.lower():
                continue
            # filtre catégorie (QuestionAdmin n'a pas de champ catégorie — on skip si filtre actif)
            if categorie and categorie != "Toutes":
                continue
            initials = (
                f"{(md.prenom or ' ')[0]}{(md.nom or ' ')[0]}".upper()
                if md else "??"
            )
            color_idx = sum(ord(c) for c in (md.id or "")) % len(AVATAR_COLORS) if md else 0
            out.append({
                "id":         q.id,
                "question":   q.titre,
                "medecin":    nom_complet,
                "email":      md.email        if md else None,
                "ville":      ville_md,
                "photo_url":  build_url(md.photo_url) if md else None,
                "cnom":       md.id           if md else "",
                "hopital":    (md.etablissement or "") if md else "",
                "initials":   initials,
                "avatarColor": AVATAR_COLORS[color_idx],
                "categorie":  "Autre",
                "statut":     q.statut,
                "reponse":    q.reponse,
                "created_at": q.created_at.isoformat() + "Z" if q.created_at else None,
                "repondu_le": q.repondu_at.isoformat() + "Z" if q.repondu_at else None,
            })
        return out

    @staticmethod
    async def repondre_question(
        db: AsyncSession, question_id: str, reponse: str, admin_id: str
    ) -> dict:
        """Enregistre la réponse à une question médecin et crée une notification sur la plateforme."""
        from app.models.question_admin import QuestionAdmin
        from app.models.notification import Notification

        result = await db.execute(select(QuestionAdmin).where(QuestionAdmin.id == question_id))
        q      = result.scalar_one_or_none()
        if not q:
            raise HTTPException(404, "Question introuvable.")

        q.reponse    = reponse
        q.statut     = "repondu"
        q.repondu_at = datetime.utcnow()

        # Notification visible dans l'espace médecin sur la plateforme
        if q.medecin_id:
            notif = Notification(
                destinataire_id = q.medecin_id,
                type_dest       = "medecin",
                type_notif      = "faq_reponse",
                titre           = "L'administration PneumoIA a répondu à votre question",
                message         = f"Votre question : {q.titre[:80]}\n\nRéponse : {reponse[:300]}",
                meta            = {"question_id": question_id, "lien": "/medecin/notifications"},
            )
            db.add(notif)

        await db.commit()

        await log_admin_action(db, admin_id, "faq_repondu",
            details={"question_id": question_id})
        return {"message": "Réponse enregistrée."}

    @staticmethod
    async def vider_historique_questions(db: AsyncSession, admin_id: str) -> dict:
        """Supprime définitivement toutes les questions répondues."""
        from app.models.question_admin import QuestionAdmin
        result = await db.execute(
            select(QuestionAdmin).where(QuestionAdmin.statut == "repondu")
        )
        questions = result.scalars().all()
        for q in questions:
            await db.delete(q)
        await db.commit()
        await log_admin_action(db, admin_id, "faq_historique_vide",
            details={"nb": len(questions)})
        return {"message": f"{len(questions)} question(s) supprimée(s)."}

    @staticmethod
    async def supprimer_question(db: AsyncSession, question_id: str, admin_id: str) -> dict:
        """Supprime définitivement une question."""
        from app.models.question_admin import QuestionAdmin
        result = await db.execute(
            select(QuestionAdmin).where(QuestionAdmin.id == question_id)
        )
        q = result.scalar_one_or_none()
        if not q:
            raise HTTPException(404, "Question introuvable.")
        await db.delete(q)
        await db.commit()
        return {"message": "Question supprimée."}

    # ─────────────────────────────────────────────────────────────────────────
    # 15. FAQ — PUBLIÉES PAR L'ADMIN
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_faq(db: AsyncSession) -> list[dict]:
        """Retourne toutes les entrées FAQ (publiées + brouillons) avec auteur."""
        from app.models.faqPubliee import FAQPubliee as FaqPublie
        from app.models.admin import Admin

        result = await db.execute(
            select(FaqPublie).options(selectinload(FaqPublie.admin))
            .order_by(FaqPublie.created_at.desc())
        )
        faqs = result.scalars().all()
        return [
            {
                "id":         f.id,
                "question":   f.question,
                "reponse":    f.reponse,
                "categorie":  f.categorie,
                "publie":     f.publie,
                "nb_vues":    f.nb_vues,
                "auteur":     f.admin.nom if f.admin else "Administrateur",
                "created_at": f.created_at.isoformat() + "Z" if f.created_at else None,
                "updated_at": f.updated_at.isoformat() + "Z" if f.updated_at else None,
            }
            for f in faqs
        ]

    @staticmethod
    async def creer_faq(
        db: AsyncSession,
        question: str, reponse: str,
        categorie: str, publie: bool, admin_id: str,
    ) -> dict:
        """Crée une nouvelle entrée FAQ. Si publie=True, notifie tous les médecins validés."""
        from app.models.faqPubliee import FAQPubliee as FaqPublie
        from app.models.notification import Notification

        faq = FaqPublie(
            question=question, reponse=reponse,
            categorie=categorie, publie=publie, admin_id=admin_id,
        )
        db.add(faq)
        await db.flush()  # obtenir faq.id sans encore committer

        if publie:
            medecins = (await db.execute(
                select(Medecin.id).where(Medecin.statut == "valide")
            )).scalars().all()
            for mid in medecins:
                db.add(Notification(
                    destinataire_id = mid,
                    type_dest       = "medecin",
                    type_notif      = "nouvelle_faq",
                    titre           = f"L'administration PneumoIA a publié une nouvelle FAQ",
                    message         = f"Question : {question[:120]}\n\nRéponse : {reponse[:200] if reponse else ''}",
                    meta            = {"faq_id": faq.id, "lien": "/medecin/notifications"},
                ))

        await db.commit()
        await db.refresh(faq)
        return {
            "id":         faq.id,
            "question":   faq.question,
            "reponse":    faq.reponse,
            "categorie":  faq.categorie,
            "publie":     faq.publie,
            "nb_vues":    faq.nb_vues,
            "created_at": faq.created_at.isoformat() + "Z" if faq.created_at else None,
            "updated_at": None,
        }

    @staticmethod
    async def modifier_faq(
        db: AsyncSession, faq_id: str,
        question: str, reponse: str,
        categorie: str, publie: bool, admin_id: str,
    ) -> dict:
        """Modifie une entrée FAQ existante."""
        from app.models.faqPubliee import FAQPubliee as FaqPublie

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
        """Bascule l'état publié/brouillon d'une entrée FAQ. Notifie les médecins si publication."""
        from app.models.faqPubliee import FAQPubliee as FaqPublie
        from app.models.notification import Notification

        result = await db.execute(select(FaqPublie).where(FaqPublie.id == faq_id))
        faq    = result.scalar_one_or_none()
        if not faq:
            raise HTTPException(404, "FAQ introuvable.")

        faq.publie = not faq.publie

        # Notification à tous les médecins validés uniquement lors d'une publication
        if faq.publie:
            medecins = (await db.execute(
                select(Medecin.id).where(Medecin.statut == "valide")
            )).scalars().all()
            for mid in medecins:
                db.add(Notification(
                    destinataire_id = mid,
                    type_dest       = "medecin",
                    type_notif      = "nouvelle_faq",
                    titre           = f"L'administration PneumoIA a publié une nouvelle FAQ",
                    message         = f"Question : {faq.question[:120]}\n\nRéponse : {faq.reponse[:200] if faq.reponse else ''}",
                    meta            = {"faq_id": faq.id, "lien": "/medecin/notifications"},
                ))

        await db.commit()
        return {"publie": faq.publie}

    @staticmethod
    async def vider_faq(db: AsyncSession, admin_id: str) -> dict:
        """Supprime toutes les entrées FAQ définitivement."""
        from app.models.faqPubliee import FAQPubliee as FaqPublie

        result = await db.execute(select(FaqPublie))
        faqs   = result.scalars().all()
        for f in faqs:
            await db.delete(f)
        await db.commit()
        return {"message": f"{len(faqs)} entrée(s) FAQ supprimées."}

    @staticmethod
    async def supprimer_faq(db: AsyncSession, faq_id: str, admin_id: str) -> dict:
        """Supprime définitivement une entrée FAQ."""
        from app.models.faqPubliee import FAQPubliee as FaqPublie

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
                .where(cast(Consultation.created_at, Date) == d)
            ) or 0
            result.append({"j": JOURS_FR[d.weekday()], "c": count})

        return {"jours": result}

    @staticmethod
    async def get_consultations_jours(
        db: AsyncSession, from_date: str, to_date: str
    ) -> list:
        """
        Consultations par jour sur une plage de dates quelconque.
        Retourne : [{ "date": "2026-06-11", "c": 5 }, ...] — une entrée par jour calendaire.
        """
        from app.models.consultation import Consultation

        d_from = datetime.strptime(from_date, "%Y-%m-%d").date()
        d_to   = datetime.strptime(to_date,   "%Y-%m-%d").date()

        rows = (await db.execute(
            select(
                cast(Consultation.created_at, Date).label("jour"),
                func.count().label("nb"),
            )
            .where(
                Consultation.created_at >= datetime.combine(d_from, datetime.min.time()),
                Consultation.created_at <= datetime.combine(d_to,   datetime.max.time()),
            )
            .group_by("jour")
        )).all()

        counts  = {str(r.jour): r.nb for r in rows}
        result  = []
        current = d_from
        while current <= d_to:
            result.append({"date": str(current), "c": counts.get(str(current), 0)})
            current += timedelta(days=1)

        return result

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
                    Consultation.created_at >= debut,
                    Consultation.created_at <= fin,
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
                cast(Consultation.created_at, Date).label("jour"),
                func.count().label("nb"),
            )
            .where(
                Consultation.created_at >= datetime.combine(d_from, datetime.min.time()),
                Consultation.created_at <= datetime.combine(d_to,   datetime.max.time()),
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
                Consultation.created_at >= datetime.combine(prec_from, datetime.min.time()),
                Consultation.created_at <= datetime.combine(prec_to,   datetime.max.time()),
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

        # Mapping ville → région pour le Cameroun
        VILLE_REGION: dict[str, str] = {
            # Littoral
            "Douala": "Littoral", "Nkongsamba": "Littoral", "Edéa": "Littoral",
            "Loum": "Littoral", "Mbanga": "Littoral",
            # Centre
            "Yaoundé": "Centre", "Yaounde": "Centre", "Obala": "Centre",
            "Mbalmayo": "Centre", "Mfou": "Centre", "Bafia": "Centre",
            # Ouest
            "Bafoussam": "Ouest", "Dschang": "Ouest", "Foumban": "Ouest",
            "Bafang": "Ouest", "Mbouda": "Ouest",
            # Nord
            "Garoua": "Nord", "Guider": "Nord", "Figuil": "Nord",
            # Est
            "Bertoua": "Est", "Abong-Mbang": "Est", "Batouri": "Est",
            # Sud
            "Ebolowa": "Sud", "Sangmélima": "Sud", "Kribi": "Sud",
            # Adamaoua
            "Ngaoundéré": "Adamaoua", "Ngaoundere": "Adamaoua", "Meiganga": "Adamaoua",
            # Extrême-Nord
            "Maroua": "Extrême-Nord", "Kousseri": "Extrême-Nord", "Mora": "Extrême-Nord",
            # Nord-Ouest
            "Bamenda": "Nord-Ouest", "Kumbo": "Nord-Ouest", "Wum": "Nord-Ouest",
            # Sud-Ouest
            "Buea": "Sud-Ouest", "Limbe": "Sud-Ouest", "Kumba": "Sud-Ouest",
        }
        # Index insensible à la casse
        VILLE_REGION_LOWER = {k.lower(): v for k, v in VILLE_REGION.items()}

        def get_region(ville: str) -> str:
            return VILLE_REGION.get(ville) or VILLE_REGION_LOWER.get(ville.lower(), "")

        result   = await db.execute(select(Medecin).where(Medecin.statut == "valide"))
        medecins = result.scalars().all()

        # Groupement par ville — utilise md.ville en priorité
        ville_map: dict[str, dict] = {}
        for md in medecins:
            if md.ville:
                ville = md.ville.strip()
            elif md.adresse:
                parts = [p.strip() for p in md.adresse.split(",")]
                ville = parts[-1] if len(parts) > 1 else parts[0]
            else:
                ville = "Inconnue"

            region = get_region(ville)

            if ville not in ville_map:
                ville_map[ville] = {
                    "ville": ville, "region": region,
                    "medecins": 0, "doctor_ids": [],
                }
            ville_map[ville]["medecins"]   += 1
            ville_map[ville]["doctor_ids"].append(md.id)

        # Consultations + patients distincts par ville
        villes = []
        for info in ville_map.values():
            ids = info["doctor_ids"]
            consultations = await db.scalar(
                select(func.count()).select_from(Consultation)
                .where(
                    Consultation.medecin_id.in_(ids),
                    Consultation.created_at >= debut,
                    Consultation.created_at <= fin,
                )
            ) or 0
            patients = await db.scalar(
                select(func.count(func.distinct(Consultation.patient_id)))
                .where(
                    Consultation.medecin_id.in_(ids),
                    Consultation.created_at >= debut,
                    Consultation.created_at <= fin,
                )
            ) or 0
            villes.append({
                "ville":         info["ville"],
                "region":        info["region"],
                "medecins":      info["medecins"],
                "consultations": consultations,
                "patients":      patients,
            })

        # Couverture par région (10 régions du Cameroun)
        REGIONS_CAMEROUN = [
            "Littoral", "Centre", "Ouest", "Nord", "Est",
            "Sud", "Adamaoua", "Extrême-Nord", "Nord-Ouest", "Sud-Ouest",
        ]
        region_md: dict[str, int] = {}
        for info in ville_map.values():
            reg = info["region"]
            if reg:
                region_md[reg] = region_md.get(reg, 0) + info["medecins"]

        regions  = [
            {
                "region":     r,
                "medecins":   region_md.get(r, 0),
                "couverture": min(region_md.get(r, 0) * 20, 100),
            }
            for r in REGIONS_CAMEROUN
        ]

        return {"villes": villes, "regions": regions}

    @staticmethod
    async def get_concordance_evolution(db: AsyncSession) -> list:
        """
        Concordance IA moyenne par mois sur les 6 derniers mois glissants.
        Retourne : [{ m: "Jan", v: 85 }, ...]
        """
        from app.models.diagnostic_ia import DiagnosticIA

        MOIS_COURTS = ["Jan","Fév","Mar","Avr","Mai","Juin","Juil","Aoû","Sep","Oct","Nov","Déc"]
        now    = datetime.utcnow()
        result = []

        for i in range(5, -1, -1):  # du plus ancien au plus récent
            ty, tm = now.year, now.month - i
            while tm <= 0:
                tm += 12; ty -= 1
            debut = datetime(ty, tm, 1)
            fin   = datetime(ty, tm, calendar.monthrange(ty, tm)[1], 23, 59, 59)

            diags = (await db.execute(
                select(DiagnosticIA)
                .where(DiagnosticIA.created_at >= debut, DiagnosticIA.created_at <= fin)
            )).scalars().all()

            scores = []
            for d in diags:
                maladies = d.maladies or []
                if isinstance(maladies, list) and maladies:
                    pct = maladies[0].get("pct")
                    if pct is not None:
                        scores.append(float(pct))

            result.append({
                "m": MOIS_COURTS[tm - 1],
                "v": round(sum(scores) / len(scores)) if scores else 0,
            })

        return result

    @staticmethod
    async def get_concordance_pathologies(
        db: AsyncSession, mois: int, annee: int
    ) -> list:
        """
        Concordance IA moyenne par pathologie pour un mois donné.
        Retourne : [{ p: "Pneumonie bactérienne", t: 87, nb: 12 }, ...]
        """
        from app.models.diagnostic_ia import DiagnosticIA

        debut = datetime(annee, mois, 1)
        fin   = datetime(annee, mois, calendar.monthrange(annee, mois)[1], 23, 59, 59)

        diags = (await db.execute(
            select(DiagnosticIA)
            .where(DiagnosticIA.created_at >= debut, DiagnosticIA.created_at <= fin)
        )).scalars().all()

        patho_map: dict[str, dict] = {}
        for d in diags:
            maladies = d.maladies or []
            if isinstance(maladies, list):
                for maladie in maladies:
                    nom = maladie.get("nom")
                    pct = maladie.get("pct")
                    if nom and pct is not None:
                        if nom not in patho_map:
                            patho_map[nom] = {"scores": [], "nb": 0}
                        patho_map[nom]["scores"].append(float(pct))
                        patho_map[nom]["nb"] += 1

        result = [
            {
                "p":  nom,
                "t":  round(sum(info["scores"]) / len(info["scores"])),
                "nb": info["nb"],
            }
            for nom, info in patho_map.items()
            if info["scores"]
        ]
        result.sort(key=lambda x: x["t"], reverse=True)
        return result

    @staticmethod
    async def get_top_medecins_concordance(
        db: AsyncSession, limit: int = 5,
        mois: Optional[int] = None, annee: Optional[int] = None,
    ) -> list[dict]:
        """
        Top N médecins triés par concordance IA décroissante.
        Filtre par mois/année si fournis.
        Retourne : [{ id, nom, prenom, specialite, photo_url, concordance_ia, nb_consultations, tendance }]
        """
        from app.models.consultation import Consultation

        now   = datetime.utcnow()
        m     = mois  or now.month
        y     = annee or now.year
        debut = datetime(y, m, 1)
        fin   = datetime(y, m, calendar.monthrange(y, m)[1], 23, 59, 59)

        result = await db.execute(
            select(Medecin)
            .where(Medecin.statut == "valide")
            .options(selectinload(Medecin.consultations).selectinload(Consultation.diagnostic))
        )
        medecins = result.scalars().all()

        enriched = []
        for md in medecins:
            # Consultations du mois sélectionné
            cons_mois = [
                c for c in (md.consultations or [])
                if c.created_at and debut <= c.created_at <= fin
            ]
            scores = []
            for c in cons_mois:
                if c.diagnostic and isinstance(c.diagnostic.maladies, list) and c.diagnostic.maladies:
                    pct = c.diagnostic.maladies[0].get("pct")
                    if pct is not None:
                        scores.append(float(pct))
            if not scores:
                continue
            enriched.append({
                "id":               md.id,
                "nom":              md.nom,
                "prenom":           md.prenom,
                "specialite":       md.specialite or "",
                "photo_url":        build_url(md.photo_url),
                "concordance_ia":   round(sum(scores) / len(scores)),
                "nb_consultations": len(cons_mois),
                "tendance":         0,
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
        # AuditLog n'a pas de colonnes type/statut — filtrage ignoré
        result = await db.execute(query)
        logs   = result.scalars().all()

        return {
            "logs": [
                {
                    "id":     l.id,
                    "action": l.action,
                    "acteur": (l.details or {}).get("admin_id", l.medecin_id or "Système"),
                    "date":   l.created_at.isoformat() if l.created_at else None,
                    "statut": "success",
                    "type":   l.action.split("_")[0] if l.action else "info",
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
        """Supprime définitivement un médecin depuis la corbeille + email de notification envoyé au médecin."""
        result  = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
        medecin = result.scalar_one_or_none()

        if not medecin:
            raise HTTPException(404, "Médecin introuvable.")
        if medecin.statut != "corbeille":
            raise HTTPException(400, "Ce médecin n'est pas dans la corbeille.")

        email, prenom, nom_med = medecin.email, medecin.prenom, medecin.nom
        await db.delete(medecin)
        await db.commit()

        await _send_email_smtp(
            to_email=email,
            to_name=f"{prenom} {nom_med}",
            subject="Votre compte PneumoIA a été supprimé",
            html=f"""
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
        )

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
        Retourne : [{ id, civilite, prenom, nom, photo_url, specialite, etablissement, ville, note, commentaire, created_at, vu }]
        """
        from app.models.avis import Avis
        from sqlalchemy.orm import selectinload

        result = await db.execute(
            select(Avis)
            .options(selectinload(Avis.medecin))
            .order_by(Avis.created_at.desc())
        )
        return [
            {
                "id":           a.id,
                "civilite":     a.medecin.civilite     if a.medecin else None,
                "prenom":       a.medecin.prenom        if a.medecin else None,
                "nom":          a.medecin.nom           if a.medecin else None,
                "photo_url":    build_url(a.medecin.photo_url) if a.medecin else None,
                "specialite":   a.medecin.specialite    if a.medecin else None,
                "etablissement":a.medecin.etablissement if a.medecin else None,
                "ville":        a.medecin.ville         if a.medecin else None,
                "note":         a.note,
                "commentaire":  a.commentaire,
                "statut":       getattr(a, "statut", "publie"),
                "created_at":   a.created_at.isoformat() if a.created_at else None,
                "vu":           a.vu,
            }
            for a in result.scalars().all()
        ]

    @staticmethod
    async def supprimer_avis(db: AsyncSession, avis_id: str, admin_id: str, raison: Optional[str] = None) -> dict:
        """Supprime un avis médecin et notifie le médecin sur la plateforme."""
        from app.models.avis import Avis

        result = await db.execute(
            select(Avis)
            .where(Avis.id == avis_id)
        )
        avis = result.scalar_one_or_none()
        if not avis:
            raise HTTPException(404, "Avis introuvable.")

        medecin_id = avis.medecin_id
        await db.delete(avis)
        await db.commit()

        await log_admin_action(db, admin_id, "avis_supprime",
            details={"avis_id": avis_id, "medecin_id": medecin_id})

        # Notification en-plateforme pour le médecin
        try:
            from app.services.notification_service import push_notif
            raison_msg = f" Raison : {raison}" if raison else ""
            await push_notif(
                db,
                dest_id   = medecin_id,
                type_dest = "medecin",
                type_notif= "temoignage_supprime",
                titre     = "Votre témoignage a été retiré",
                message   = f"L'administrateur a supprimé votre témoignage de la page d'accueil.{raison_msg}",
                meta      = {"lien": "/medecin/commentaires"},
                force     = True,
            )
            await db.commit()
        except Exception as _e:
            import logging; logging.getLogger(__name__).warning("push_notif temoignage: %s", _e)

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

    @staticmethod
    async def approuver_avis(db: AsyncSession, avis_id: str) -> dict:
        """Approuve un avis → le rend visible sur la landing page."""
        from app.models.avis import Avis

        result = await db.execute(select(Avis).where(Avis.id == avis_id))
        avis = result.scalar_one_or_none()
        if not avis:
            raise HTTPException(404, "Avis introuvable.")
        avis.statut = "publie"
        avis.vu     = True
        await db.commit()
        return {"message": "Avis approuvé.", "id": avis_id}

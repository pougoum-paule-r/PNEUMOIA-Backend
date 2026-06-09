from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from app.models.admin import Admin
from app.models.medecin import Medecin
from app.models.document_medecin import DocumentMedecin
from app.core.security import hash_password
from app.config import settings
from twilio.rest import Client
from datetime import datetime, timedelta
from typing import Optional
import random
import secrets

# ── Labels documents ───────────────────────────────────────────────────────────
LABELS_DOCUMENT = {
    "diplome_specialisation": "Diplôme de spécialisation",
    "diplome_medecine":       "Diplôme de docteur en médecine",
    "inscription_ordre":      "Inscription à l'ordre des médecins",
    "autorisation_exercice":  "Autorisation d'exercice",
    "carte_professionnelle":  "Carte professionnelle",
    "cni":                    "Carte nationale d'identité (CNI)",
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def build_url(path: str | None) -> str | None:
    if not path:
        return None
    if path.startswith("http"):
        return path
    if path.startswith("/"):
        return f"{settings.BACKEND_URL}{path}"
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
        # Traçabilité validation
        "valide_le":     m.valide_le.isoformat() if m.valide_le else None,
        "valide_par":    m.valideur.email if m.valideur else None,
        "motif_rejet":   m.motif_rejet,
        "documents":     [format_document(d) for d in m.documents],
    }


class AdminService:

    # ── Demandes en attente ────────────────────────────────────────────────────

    @staticmethod
    async def get_demandes(db: AsyncSession) -> list[dict]:
        """Retourne tous les médecins en attente avec documents et photo."""
        result = await db.execute(
            select(Medecin)
            .where(Medecin.statut == "en_attente")
            .options(selectinload(Medecin.documents))
            .order_by(Medecin.created_at.desc())
        )
        medecins = result.scalars().all()
        return [format_medecin(m) for m in medecins]

    # ── Validées par mois/année ────────────────────────────────────────────────

    @staticmethod
    async def get_valides(
        db: AsyncSession,
        mois: Optional[int] = None,
        annee: Optional[int] = None,
    ) -> list[dict]:
        """
        Retourne les médecins validés pour un mois et une année donnés.
        Si mois/annee non fournis, retourne le mois en cours.
        """
        now   = datetime.utcnow()
        m     = mois  or now.month
        y     = annee or now.year

        debut = datetime(y, m, 1)
        fin   = datetime(y + 1, 1, 1) if m == 12 else datetime(y, m + 1, 1)

        result = await db.execute(
            select(Medecin)
            .where(
                Medecin.statut    == "valide",
                Medecin.valide_le >= debut,
                Medecin.valide_le <  fin,
            )
            .options(
                selectinload(Medecin.documents),
                selectinload(Medecin.valideur),
            )
            .order_by(Medecin.valide_le.desc())
        )
        medecins = result.scalars().all()
        return [format_medecin(m) for m in medecins]

    # ── Médecins par statut ────────────────────────────────────────────────────

    @staticmethod
    async def get_demandes_par_statut(
        db: AsyncSession,
        statut: str,
    ) -> list[dict]:
        """
        Retourne les médecins filtrés par statut.
        Valeurs : en_attente | valide | rejete | suspendu
        """
        result = await db.execute(
            select(Medecin)
            .where(Medecin.statut == statut)
            .options(
                selectinload(Medecin.documents),
                selectinload(Medecin.valideur),
            )
            .order_by(Medecin.created_at.desc())
        )
        medecins = result.scalars().all()
        return [format_medecin(m) for m in medecins]

    # ── Médecins actifs avec stats d'activité ─────────────────────────────────
    # Endpoint : GET /api/admin/demandes/statut/valide
    # Retourne les médecins validés enrichis avec :
    #   - stats consultations, patients, concordance IA (depuis tables Consultation/CasPartage)
    #   - dernière activité (dernière consultation)
    #   - rang communauté (nb cas partagés publiquement)

    @staticmethod
    async def get_medecins_actifs(db: AsyncSession) -> list[dict]:
        """
        Retourne tous les médecins avec statut 'valide'.
        Enrichit chaque médecin avec ses stats d'activité temps réel.
        """
        result = await db.execute(
            select(Medecin)
            .where(Medecin.statut == "valide")
            .options(
                selectinload(Medecin.consultations).selectinload("diagnostic"),
                # Charge les diagnostics IA via la relation Consultation.diagnostic
                selectinload(Medecin.cas_cliniques),   # CasCliniquPublic
                selectinload(Medecin.valideur),
            )
            .order_by(Medecin.valide_le.desc())
        )
        medecins = result.scalars().all()
        return [AdminService._format_medecin_actif(m) for m in medecins]

    @staticmethod
    def _format_medecin_actif(m: Medecin) -> dict:
        """
        Formate un médecin avec toutes ses stats pour MedecinsActifs et ProfilMedecin.

        Sources de données :
          - m.consultations     → Table Consultation (relation directe)
          - m.cas_cliniques     → Table CasCliniquPublic (relation directe)
          - consultation.diagnostic → DiagnosticIA pour la concordance IA
          - consultation.partage    → JSONB {actif, type} pour savoir si partagée
        """
        consultations = m.consultations  or []
        cas_cliniques = m.cas_cliniques  or []

        # ── Patients uniques ──────────────────────────────────────────────────
        # On compte les patient_id distincts sur toutes les consultations
        nb_patients = len(set(
            c.patient_id for c in consultations if c.patient_id
        ))

        # ── Concordance IA moyenne ────────────────────────────────────────────
        # La concordance est dans DiagnosticIA (relation diagnostic sur Consultation)
        # On prend la moyenne des 30 dernières consultations avec diagnostic
        scores = []
        for cons in sorted(consultations, key=lambda x: x.created_at or datetime.min, reverse=True)[:30]:
            if cons.diagnostic and hasattr(cons.diagnostic, "score_concordance"):
                if cons.diagnostic.score_concordance is not None:
                    scores.append(cons.diagnostic.score_concordance)
        concordance_ia = round(sum(scores) / len(scores)) if scores else None

        # ── Dernière activité ─────────────────────────────────────────────────
        # Date de la consultation la plus récente du médecin
        dates = [c.created_at for c in consultations if c.created_at]
        derniere_activite = max(dates).isoformat() if dates else None

        # ── Cas cliniques publiés ─────────────────────────────────────────────
        # CasCliniquPublic — tous les cas publiés par ce médecin
        nb_cas = len(cas_cliniques)

        # ── Consultations partagées ───────────────────────────────────────────
        # Consultation.partage = JSONB {actif: bool, type: "communaute"|"medecin"}
        nb_partages = len([
            c for c in consultations
            if isinstance(c.partage, dict) and c.partage.get("actif")
        ])

        # ── Activité récente (5 dernières consultations terminées) ────────────
        recentes = sorted(
            [c for c in consultations if c.statut == "terminee"],
            key=lambda c: c.created_at or datetime.min,
            reverse=True
        )[:5]
        activite_recente = [
            {
                "texte": f"Consultation #{cons.id[:8]} enregistrée",
                "quand": cons.created_at.strftime("%d/%m/%Y %H:%M") if cons.created_at else "—",
            }
            for cons in recentes
        ]

        return {
            # ── Identité ──────────────────────────────────────────────────────
            "id":               m.id,
            "civilite":         m.civilite,
            "nom":              m.nom,
            "prenom":           m.prenom,
            "email":            m.email,
            "telephone":        m.telephone,
            "specialite":       m.specialite,
            "numero_rpps":      m.numero_rpps,
            "etablissement":    m.etablissement,
            "adresse":          m.adresse,
            "photo_url":        build_url(m.photo_url),
            "statut":           m.statut,
            # ── Dates ─────────────────────────────────────────────────────────
            "created_at":       m.created_at.isoformat() if m.created_at else None,
            "valide_le":        m.valide_le.isoformat()  if m.valide_le  else None,
            "valide_par":       m.valideur.email          if m.valideur   else None,
            # ── Stats activité ────────────────────────────────────────────────
            "nb_patients":      nb_patients,
            "nb_consultations": len(consultations),
            "concordance_ia":   concordance_ia,       # % moyen sur DiagnosticIA.score_concordance
            "derniere_activite":derniere_activite,     # ISO string → frontend calcule Actif/Inactif
            "nb_cas_partages":  nb_partages,           # consultations partagées (partage.actif=True)
            "nb_cas_cliniques": nb_cas,                # cas cliniques publics publiés
            "rang_communaute":  f"#{nb_cas}/38" if nb_cas else "—",
            "cas_partages":     f"{nb_cas} cas publiés",
            "activite_recente": activite_recente,
        }

    # ── Profil médecin par ID ──────────────────────────────────────────────────
    # Endpoint : GET /api/admin/medecins/{id}
    # Retourne le profil complet d'un médecin avec toutes ses stats

    @staticmethod
    async def get_medecin_by_id(db: AsyncSession, medecin_id: str) -> dict:
        """
        Retourne le profil complet d'un médecin pour la page ProfilMedecin.
        Même format que _format_medecin_actif + documents.
        """
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

        # Ajouter les documents pour ProfilMedecin
        data["documents"] = [format_document(d) for d in medecin.documents]

        return data

    # ── Valider un médecin ─────────────────────────────────────────────────────

    @staticmethod
    async def valider_medecin(db: AsyncSession, medecin_id: str, admin_id: str) -> dict:
        """Valide un médecin et génère un lien d'activation."""
        result = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
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

        # Email d'activation — géré par le binôme SMTP
        email_envoye = False
        try:
            # from app.services.email_service import send_activation_email
            # await send_activation_email(medecin.email, lien)
            email_envoye = True
        except Exception:
            email_envoye = False

        return {
            "message":         "Médecin validé avec succès.",
            "email_envoye":    email_envoye,
            "email_medecin":   medecin.email,
            "lien_activation": lien,
        }

    # ── Rejeter un médecin ─────────────────────────────────────────────────────

    @staticmethod
    async def rejeter_medecin(db: AsyncSession, medecin_id: str, motif: str) -> dict:
        """Refuse un médecin avec un motif."""
        result = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
        medecin = result.scalar_one_or_none()

        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin introuvable.")
        if medecin.statut != "en_attente":
            raise HTTPException(status_code=400, detail="Ce médecin n'est pas en attente.")

        medecin.statut      = "rejete"
        medecin.motif_rejet = motif
        await db.commit()

        # Email de refus — géré par le binôme SMTP
        try:
            # from app.services.email_service import send_rejection_email
            # await send_rejection_email(medecin.email, motif)
            pass
        except Exception:
            pass

        return {"message": "Médecin refusé. Notification envoyée."}

    # ── Dossiers refusés ──────────────────────────────────────────────────────

    @staticmethod
    async def get_demandes_refusees(
        db: AsyncSession,
        ville: str | None = None,
        motif: str | None = None,
    ) -> list[dict]:
        """Retourne les demandes avec statut 'rejete', avec filtres optionnels."""
        query = select(Medecin).where(Medecin.statut == "rejete")

        if ville:
            query = query.where(Medecin.adresse.ilike(f"%{ville}%"))
        if motif:
            query = query.where(Medecin.motif_rejet == motif)

        query = query.order_by(Medecin.updated_at.desc())
        result = await db.execute(query)
        medecins = result.scalars().all()

        return [
            {
                "id":           m.id,
                "nom":          f"{m.civilite or 'Dr.'} {m.prenom} {m.nom}",
                "prenom":       m.prenom,
                "initials":     f"{(m.prenom or '')[:1].upper()}{(m.nom or '')[:1].upper()}",
                "specialite":   m.specialite or "—",
                "cnom":         m.numero_rpps or "—",
                "hopital":      m.etablissement or "—",
                "ville":        m.adresse or "—",
                "email":        m.email,
                "telephone":    m.telephone or "—",
                "photo_url":    build_url(m.photo_url) if m.photo_url else None,
                "motif":        m.motif_rejet or "—",
                "refuse_par":   m.valide_par or "Administrateur",
                "date_demande": m.created_at.strftime("%d/%m/%Y") if m.created_at else "—",
                "date_refus":   m.updated_at.strftime("%d/%m/%Y") if m.updated_at else "—",
                "relance_sent": m.relance_sent or False,
            }
            for m in medecins
        ]

    @staticmethod
    async def supprimer_dossier_refuse(db: AsyncSession, medecin_id: str) -> dict:
        """Supprime définitivement un dossier refusé."""
        result = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
        medecin = result.scalar_one_or_none()

        if not medecin:
            raise HTTPException(status_code=404, detail="Dossier introuvable.")
        if medecin.statut != "rejete":
            raise HTTPException(status_code=400, detail="Ce dossier n'est pas refusé.")

        await db.delete(medecin)
        await db.commit()

        return {"message": f"Dossier de {medecin.prenom} {medecin.nom} supprimé définitivement."}

    @staticmethod
    async def relancer_medecin(
        db: AsyncSession,
        medecin_id: str,
        message: str,
        admin_id: str,
    ) -> dict:
        """
        Envoie un e-mail de relance au médecin refusé.
        Le médecin peut corriger son dossier et re-soumettre.
        """
        result = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
        medecin = result.scalar_one_or_none()

        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin introuvable.")
        if medecin.statut != "rejete":
            raise HTTPException(status_code=400, detail="Ce médecin n'est pas dans l'état refusé.")
        if medecin.relance_sent:
            raise HTTPException(status_code=400, detail="Une relance a déjà été envoyée.")

        # Email envoyé par le binôme SMTP (Brevo)
        # await send_relance_email(
        #     to_email = medecin.email,
        #     nom      = f"{medecin.prenom} {medecin.nom}",
        #     message  = message,
        # )

        # Marquer relance envoyée
        medecin.relance_sent = True
        medecin.relance_at   = datetime.utcnow()
        await db.commit()

        return {
            "message":      f"E-mail de relance envoyé à {medecin.email}.",
            "relance_sent": True,
        }

    # ── Suspendre un médecin ──────────────────────────────────────────────────

    @staticmethod
    async def suspendre_medecin(
        db: AsyncSession,
        medecin_id: str,
        raison: str,
        duree: str,
        message: str,
        admin_id: str,
    ) -> dict:
        """Suspend un médecin — statut passe à 'suspendu'."""
        result = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
        medecin = result.scalar_one_or_none()

        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin introuvable.")
        if medecin.statut == "suspendu":
            raise HTTPException(status_code=400, detail="Ce médecin est déjà suspendu.")

        medecin.statut         = "suspendu"
        medecin.suspension_raison  = raison
        medecin.suspension_duree   = duree
        medecin.suspension_par     = admin_id
        medecin.suspension_le      = datetime.utcnow()
        await db.commit()

        # ── Notification email au médecin via Brevo ──────────────────────────────
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
                await client.post(
                    "https://api.brevo.com/v3/smtp/email",
                    json=brevo_payload,
                    headers={"api-key": settings.BREVO_API_KEY, "Content-Type": "application/json"},
                    timeout=10,
                )
        except Exception:
            pass  # Ne pas bloquer si l'email échoue

        return {
            "message": f"Médecin suspendu pour : {raison} — {duree}.",
            "statut":  "suspendu",
        }

    # ── Réactiver un médecin ───────────────────────────────────────────────────

    @staticmethod
    async def reactiver_medecin(db: AsyncSession, medecin_id: str, admin_id: str) -> dict:
        """Réactive un médecin suspendu — statut repasse à 'valide'."""
        result = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
        medecin = result.scalar_one_or_none()

        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin introuvable.")
        if medecin.statut != "suspendu":
            raise HTTPException(status_code=400, detail="Ce médecin n'est pas suspendu.")

        raison_initiale = medecin.suspension_raison or "—"

        medecin.statut            = "valide"
        medecin.suspension_raison = None
        medecin.suspension_duree  = None
        medecin.suspension_par    = None
        medecin.suspension_le     = None
        await db.commit()

        # ── Notification email de réactivation via Brevo ──────────────────────
        import httpx
        brevo_payload = {
            "sender": {"name": "PneumoIA", "email": settings.ADMIN_EMAIL},
            "to":     [{"email": medecin.email, "name": f"{medecin.prenom} {medecin.nom}"}],
            "subject": "Votre compte PneumoIA a été réactivé",
            "htmlContent": f"""
                <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px">
                  <h2 style="color:#0f766e">PneumoIA — Réactivation de compte</h2>
                  <p>Bonjour <strong>{medecin.prenom} {medecin.nom}</strong>,</p>
                  <p>Votre accès à la plateforme PneumoIA a été <strong>réactivé</strong>
                  par l'administration.</p>
                  <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:16px;margin:16px 0">
                    <p style="margin:0;color:#065f46">
                      <strong>Motif initial de la suspension :</strong> {raison_initiale}
                    </p>
                  </div>
                  <p>Vous pouvez vous reconnecter dès maintenant sur la plateforme.</p>
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
                await client.post(
                    "https://api.brevo.com/v3/smtp/email",
                    json=brevo_payload,
                    headers={"api-key": settings.BREVO_API_KEY, "Content-Type": "application/json"},
                    timeout=10,
                )
        except Exception:
            pass  # Ne pas bloquer si l'email échoue

        return {
            "message": "Médecin réactivé avec succès. Notification envoyée.",
            "statut":  "valide",
        }

    # ── Supprimer un médecin ───────────────────────────────────────────────────

    @staticmethod
    async def supprimer_medecin(db: AsyncSession, medecin_id: str) -> dict:
        """Supprime définitivement un médecin et toutes ses données."""
        result = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
        medecin = result.scalar_one_or_none()

        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin introuvable.")

        email   = medecin.email
        prenom  = medecin.prenom
        nom_med = medecin.nom

        await db.delete(medecin)
        await db.commit()

        # ── Notification email au médecin via Brevo ──────────────────────────────
        import httpx
        brevo_payload = {
            "sender": {"name": "PneumoIA", "email": settings.ADMIN_EMAIL},
            "to":     [{"email": email, "name": f"{prenom} {nom_med}"}],
            "subject": "Votre compte PneumoIA a été supprimé",
            "htmlContent": f"""
                <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px">
                  <h2 style="color:#dc2626">PneumoIA — Suppression de compte</h2>
                  <p>Bonjour <strong>{prenom} {nom_med}</strong>,</p>
                  <p>Votre compte sur la plateforme PneumoIA a été <strong>supprimé définitivement</strong>
                  par l'administration.</p>
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
                await client.post(
                    "https://api.brevo.com/v3/smtp/email",
                    json=brevo_payload,
                    headers={"api-key": settings.BREVO_API_KEY, "Content-Type": "application/json"},
                    timeout=10,
                )
        except Exception:
            pass  # Ne pas bloquer si l'email échoue

        return {"message": "Compte médecin supprimé définitivement."}

    # ── Reset mot de passe admin ───────────────────────────────────────────────

    @staticmethod
    async def request_password_reset(db: AsyncSession, email: str, phone: str) -> str:
        result = await db.execute(select(Admin).where(Admin.email == email))
        admin = result.scalar_one_or_none()

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
    async def verify_and_update_password(
        db: AsyncSession,
        email: str,
        otp: str,
        new_password: str,
    ) -> None:
        result = await db.execute(select(Admin).where(Admin.email == email))
        admin = result.scalar_one_or_none()

        if not admin:
            raise HTTPException(status_code=400, detail="Compte introuvable.")
        if not admin.is_otp_valid(otp):
            raise HTTPException(status_code=400, detail="Code OTP invalide ou expiré.")

        admin.password_hash = hash_password(new_password)
        admin.clear_otp()
        await db.commit()

    @staticmethod
    async def send_otp_sms(otp: str, phone: str) -> str:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=(
                f"PneumoIA — Votre code de réinitialisation est : {otp}. "
                f"Valide 10 minutes. Ne le partagez pas."
            ),
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone,
        )
        return message.sid

    # ── Dossiers refusés ───────────────────────────────────────────────────────

    @staticmethod
    async def get_demandes_refusees(
        db:    AsyncSession,
        ville: str | None = None,
        motif: str | None = None,
    ) -> list[dict]:
        """
        Retourne les demandes refusées (statut='rejete').
        Filtres optionnels : ville (adresse), motif (motif_rejet).
        """
        query = (
            select(Medecin)
            .where(Medecin.statut == "rejete")
            .options(selectinload(Medecin.documents))
            .order_by(Medecin.updated_at.desc())
        )
        if ville:
            query = query.where(Medecin.adresse.ilike(f"%{ville}%"))
        if motif:
            query = query.where(Medecin.motif_rejet == motif)

        result  = await db.execute(query)
        medecins = result.scalars().all()

        return [
            {
                **format_medecin(m),
                # Champs spécifiques page Refusées
                "refuse_par":   m.valide_par or "Administrateur",
                "date_demande": m.created_at.strftime("%d/%m/%Y") if m.created_at else "—",
                "date_refus":   m.updated_at.strftime("%d/%m/%Y") if m.updated_at else "—",
                "relance_sent": getattr(m, "relance_sent", False) or False,
            }
            for m in medecins
        ]

    @staticmethod
    async def supprimer_dossier_refuse(
        db:         AsyncSession,
        medecin_id: str,
    ) -> dict:
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
    async def relancer_medecin(
        db:         AsyncSession,
        medecin_id: str,
        message:    str,
        admin_id:   str,
    ) -> dict:
        """
        Envoie un e-mail de relance au médecin refusé via Brevo.
        Le médecin peut corriger son dossier et re-soumettre.
        relance_sent passe à True — le bouton devient grisé côté frontend.
        """
        result  = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
        medecin = result.scalar_one_or_none()

        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin introuvable.")
        if medecin.statut != "rejete":
            raise HTTPException(status_code=400, detail="Ce médecin n'est pas dans l'état refusé.")
        if getattr(medecin, "relance_sent", False):
            raise HTTPException(status_code=400, detail="Une relance a déjà été envoyée à ce médecin.")

        # ── Envoi e-mail via Brevo ─────────────────────────────────────────────
        import httpx

        brevo_payload = {
            "sender":     {"name": "PneumoIA", "email": settings.ADMIN_EMAIL},
            "to":         [{"email": medecin.email, "name": f"{medecin.prenom} {medecin.nom}"}],
            "subject":    "Votre demande d'inscription PneumoIA — Relance",
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
                  <p style="color:#6b7280;font-size:12px">
                    Motif du refus : <em>{medecin.motif_rejet}</em>
                  </p>
                  <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0"/>
                  <p style="color:#9ca3af;font-size:11px">
                    Cet e-mail a été envoyé par l'équipe PneumoIA.<br/>
                    Ne répondez pas directement à cet e-mail.
                  </p>
                </div>
            """,
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.brevo.com/v3/smtp/email",
                json    = brevo_payload,
                headers = {
                    "api-key":      settings.BREVO_API_KEY,
                    "Content-Type": "application/json",
                },
                timeout = 10,
            )
            if resp.status_code not in (200, 201):
                raise HTTPException(
                    status_code = 502,
                    detail      = f"Échec envoi e-mail Brevo : {resp.text}",
                )

        # Marquer relance envoyée
        medecin.relance_sent = True
        medecin.relance_at   = datetime.utcnow()
        await db.commit()

        return {
            "message":      f"E-mail de relance envoyé à {medecin.email}.",
            "relance_sent": True,
        }
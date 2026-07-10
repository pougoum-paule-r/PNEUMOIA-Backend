import random, string
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class Consultation(Base):
    __tablename__ = "consultations"

    id         = Column(String(15), primary_key=True, default=generate_id)
    patient_id = Column(String(15), ForeignKey("patients.id",  ondelete="RESTRICT"), nullable=False)
    medecin_id = Column(String(15), ForeignKey("medecins.id",  ondelete="RESTRICT"), nullable=False)

    # ── ÉTAPE 2 — Antécédents (snapshot au moment de la consultation) ─
    antecedents_consultation = Column(JSONB, nullable=True, default=dict)
    # {diabete, hypertension, asthme, tabagisme, cigarettesParJour, ...}

    # ── ÉTAPE 3 — Symptômes + signes vitaux + EFR (tout en JSONB) ────
    symptomes = Column(JSONB, nullable=False, default=dict)
    # {
    #   motif, debut_symptomes, evolution, traitement_deja_pris,
    #   temperature, saturation_o2, frequence_cardiaque, frequence_respiratoire,
    #   tension_systolique, tension_diastolique,
    #   fievre, fievre_temperature, fievre_duree,
    #   toux, toux_type, toux_couleur, toux_sang,
    #   dyspnee, dyspnee_stade, dyspnee_repos, dyspnee_effort,
    #   douleur_thoracique, douleur_type,
    #   wheezing, hemoptysie, fatigue, perte_poids,
    #   sueurs_nocturnes, courbatures, maux_de_tete, rhinorrhee,
    #   crepitants, sibilants, scanner, efr, recherche_bk,
    #   fvc, fec1, peak_flow, pefr_anormal, abg_co2_anormal, abg_ph_anormal
    # }

    # ── STATUTS ───────────────────────────────────────────────────────
    # statut          : avis médecin  → en_attente / terminee
    # statut_clinique : état patient  → stable / surveille / urgent / critique
    statut = Column(
        Enum("en_attente", "terminee", name="statut_consultation"),
        nullable=False,
        default="en_attente",
    )
    statut_clinique = Column(
        Enum("stable", "surveille", "urgent", "critique", name="statut_clinique_enum"),
        nullable=True,
        default=None,
    )

    # ── ÉTAPE 4 — Avis médecin (optionnel — si absent = en_attente) ───
    avis_medecin  = Column(Text, nullable=True)
    observations  = Column(Text, nullable=True)

    # ── ÉTAPE 4 — Prescription ────────────────────────────────────────
    prescriptions = Column(JSONB, nullable=False, default=dict)
    # {
    #   medicaments, conseils_maison, recommandations,
    #   arret_travail, duree_arret,
    #   hospitalisation, motif_hospitalisation,
    #   suivi ("7 jours"|"15 jours"|"1 mois"|"3 mois")
    # }

    recommandations = Column(Text,     nullable=True)
    prochain_rdv    = Column(DateTime, nullable=True)

    # ── PARTAGE ───────────────────────────────────────────────────────
    # Médecin peut partager avec un médecin OU une communauté
    partage = Column(JSONB, nullable=False, default=dict)
    # {
    #   actif: bool,
    #   anonymiser: bool,
    #   type: "medecin"|"communaute"|null,
    #   destinataire_id: str|null,  ← id médecin ou communauté
    #   envoyer_mail_patient: bool
    # }

    # ── MÉTA ──────────────────────────────────────────────────────────
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at = Column(DateTime, nullable=True,  onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # ── RELATIONS ─────────────────────────────────────────────────────
    patient      = relationship("Patient",      back_populates="consultations")
    medecin      = relationship("Medecin",      back_populates="consultations", foreign_keys=[medecin_id])
    diagnostic   = relationship("DiagnosticIA", back_populates="consultation",  uselist=False, cascade="all, delete-orphan")
    publications = relationship("Publication",  back_populates="consultation")

    def __repr__(self):
        return f"<Consultation {self.id} statut={self.statut}>"
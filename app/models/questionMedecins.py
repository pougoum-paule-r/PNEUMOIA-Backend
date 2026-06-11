"""
question_medecin.py — Questions posées par les médecins à l'administration

Multiplicité :
  - Un médecin peut poser plusieurs questions       (one-to-many : Medecin → QuestionMedecin)
  - Un admin peut répondre à plusieurs questions    (one-to-many : Admin   → QuestionMedecin)
  - Une question a au plus une réponse              (one-to-one  : QuestionMedecin.reponse)

Cycle de vie :
  en_attente → repondu (après réponse admin)
  Archivage automatique après 90 jours (cron job)
"""

import random
import string
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class QuestionMedecin(Base):
    __tablename__ = "questions_medecins"

    id = Column(String(15), primary_key=True, default=generate_id)

    # ── Auteur de la question ─────────────────────────────────────────────────
    # Nullable en cas de suppression du médecin (SET NULL)
    medecin_id = Column(
        String(15),
        ForeignKey("medecins.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Contenu ───────────────────────────────────────────────────────────────
    question  = Column(Text,        nullable=False)
    categorie = Column(String(50),  nullable=False, default="Autre")
    # Valeurs : Compte | IA | Technique | Exportation | Inscription | Autre

    # ── Statut ────────────────────────────────────────────────────────────────
    statut = Column(
        Enum("en_attente", "repondu", name="statut_question"),
        nullable=False,
        default="en_attente",
    )

    # ── Réponse de l'administrateur ───────────────────────────────────────────
    reponse    = Column(Text,        nullable=True)   # contenu de la réponse
    repondu_par = Column(
        String(15),
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True,
    )
    repondu_le = Column(DateTime, nullable=True)      # date de la réponse

    # ── Méta ──────────────────────────────────────────────────────────────────
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True,  onupdate=datetime.utcnow)

    # ── Relations ─────────────────────────────────────────────────────────────
    medecin   = relationship(
        "Medecin",
        back_populates="questions",
        foreign_keys=[medecin_id],
    )
    repondant = relationship(
        "Admin",
        back_populates="questions_repondues",
        foreign_keys=[repondu_par],
    )

    def __repr__(self):
        return f"<QuestionMedecin {self.id} statut={self.statut} medecin={self.medecin_id}>"
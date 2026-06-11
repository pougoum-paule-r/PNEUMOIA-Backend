"""
faq_publiee.py — FAQ publiées par l'administrateur

Multiplicité :
  - Un admin peut créer plusieurs entrées FAQ       (one-to-many : Admin → FAQPubliee)
  - Une FAQ peut être vue par plusieurs médecins    (compteur nb_vues)

Cycle de vie :
  brouillon (publie=False) → publiée (publie=True) → dépubliée (publie=False)
  L'admin peut vider toute la FAQ (suppression définitive en BD)
  L'admin peut supprimer individuellement
"""

import random
import string
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class FAQPubliee(Base):
    __tablename__ = "faq_publiees"

    id = Column(String(15), primary_key=True, default=generate_id)

    # ── Auteur (admin qui a créé la FAQ) ─────────────────────────────────────
    # Nullable en cas de suppression de l'admin (SET NULL)
    admin_id = Column(
        String(15),
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Contenu ───────────────────────────────────────────────────────────────
    question  = Column(Text,       nullable=False)
    reponse   = Column(Text,       nullable=False)
    categorie = Column(String(50), nullable=False, default="Autre")
    # Valeurs : Compte | IA | Technique | Exportation | Inscription | Autre

    # ── Visibilité ────────────────────────────────────────────────────────────
    publie = Column(Boolean, nullable=False, default=False)
    # False = brouillon (visible uniquement par l'admin)
    # True  = publiée   (visible par tous les médecins connectés)

    # ── Statistiques ──────────────────────────────────────────────────────────
    nb_vues = Column(Integer, nullable=False, default=0)
    # Incrémenté chaque fois qu'un médecin consulte cette entrée FAQ

    # ── Méta ──────────────────────────────────────────────────────────────────
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True,  onupdate=datetime.utcnow)

    # ── Relations ─────────────────────────────────────────────────────────────
    admin = relationship(
        "Admin",
        back_populates="faq_publiees",
        foreign_keys=[admin_id],
    )

    def __repr__(self):
        return f"<FAQPubliee {self.id} publie={self.publie} categorie={self.categorie}>"
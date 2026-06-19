import random, string
from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class CasCliniquPublic(Base):
    __tablename__ = "cas_cliniques_publics"

    id                 = Column(String(15), primary_key=True, default=generate_id)
    titre              = Column(String(300), nullable=False)
    pathologie         = Column(String(200), nullable=True)
    description        = Column(Text,        nullable=True)
    tags               = Column(JSONB,       nullable=False, default=list)  # ["Pneumonie", "Pédiatrie", ...]
    pdf_url            = Column(String(500), nullable=True)                 # téléchargeable publiquement
    auteur_id          = Column(String(15),  ForeignKey("medecins.id", ondelete="SET NULL"), nullable=True)
    anonymise          = Column(Boolean,  nullable=False, default=True)
    nb_vues            = Column(Integer,  nullable=False, default=0)
    nb_telechargements = Column(Integer,  nullable=False, default=0)
    created_at         = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relations
    auteur = relationship("Medecin", back_populates="cas_cliniques")

    def __repr__(self):
        return f"<CasCliniquPublic {self.id} — '{self.titre}'>"

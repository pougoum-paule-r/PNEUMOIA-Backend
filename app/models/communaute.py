import random, string
from datetime import datetime

from sqlalchemy import Column, String, Text, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class Communaute(Base):
    __tablename__ = "communautes"

    id          = Column(String(15), primary_key=True, default=generate_id)
    nom         = Column(String(200), nullable=False)
    description = Column(Text,        nullable=True)
    type        = Column(
        Enum("publique", "privee", name="type_communaute"),
        nullable=False,
        default="publique",
    )
    specialite  = Column(String(100), nullable=True)
    avatar_url  = Column(String(500), nullable=True)
    createur_id = Column(String(15),  ForeignKey("medecins.id", ondelete="RESTRICT"), nullable=False)
    nb_membres  = Column(Integer,     nullable=False, default=1)
    nb_cas      = Column(Integer,     nullable=False, default=0)
    created_at  = Column(DateTime,    nullable=False, default=datetime.utcnow)

    # Relations
    createur     = relationship("Medecin",          back_populates="communautes_creees", foreign_keys=[createur_id])
    membres      = relationship("MembreCommunaute", back_populates="communaute", cascade="all, delete-orphan")
    publications = relationship("Publication",      back_populates="communaute", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Communaute {self.id} — {self.nom} ({self.type})>"

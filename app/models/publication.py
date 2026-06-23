import random, string
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class Publication(Base):
    __tablename__ = "publications"

    id              = Column(String(15), primary_key=True, default=generate_id)
    communaute_id   = Column(String(15), ForeignKey("communautes.id",        ondelete="SET NULL"), nullable=True)
    auteur_id       = Column(String(15), ForeignKey("medecins.id",           ondelete="RESTRICT"), nullable=False)
    consultation_id = Column(String(15), ForeignKey("consultations.id",      ondelete="SET NULL"), nullable=True)
    ressource_id    = Column(String(30), ForeignKey("ressources_medicales.id", ondelete="SET NULL"), nullable=True)
    titre           = Column(String(300), nullable=False)
    contenu         = Column(Text,        nullable=True)
    type            = Column(
        Enum("cas_clinique", "question", "article", "discussion", name="type_publication"),
        nullable=False,
    )
    tags            = Column(JSONB,    nullable=False, default=list)   # ["Tuberculose", "BPCO", ...]
    nb_commentaires = Column(Integer,  nullable=False, default=0)
    nb_reactions    = Column(Integer,  nullable=False, default=0)
    created_at      = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relations
    communaute   = relationship("Communaute",   back_populates="publications")
    auteur       = relationship("Medecin",      back_populates="publications")
    consultation = relationship("Consultation", back_populates="publications")
    commentaires = relationship("Commentaire",  back_populates="publication", cascade="all, delete-orphan")
    reactions    = relationship("Reaction",     back_populates="publication", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Publication {self.id} — '{self.titre}' type={self.type}>"

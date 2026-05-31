import random, string
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class Commentaire(Base):
    __tablename__ = "commentaires"

    id             = Column(String(15), primary_key=True, default=generate_id)
    publication_id = Column(String(15), ForeignKey("publications.id", ondelete="CASCADE"),  nullable=False)
    auteur_id      = Column(String(15), ForeignKey("medecins.id",     ondelete="RESTRICT"), nullable=False)
    contenu        = Column(Text,       nullable=False)
    created_at     = Column(DateTime,   nullable=False, default=datetime.utcnow)

    # Relations
    publication = relationship("Publication", back_populates="commentaires")
    auteur      = relationship("Medecin",     back_populates="commentaires")

    def __repr__(self):
        return f"<Commentaire {self.id} publication={self.publication_id}>"

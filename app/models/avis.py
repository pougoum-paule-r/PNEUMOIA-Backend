import random, string
from datetime import datetime

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class Avis(Base):
    """Témoignages/avis laissés par les médecins sur la plateforme (landing page)."""
    __tablename__ = "avis_medecins"

    id         = Column(String(15), primary_key=True, default=generate_id)
    medecin_id = Column(String(15), ForeignKey("medecins.id", ondelete="CASCADE"), nullable=False)
    note       = Column(Integer,  nullable=False)
    contenu    = Column(Text,     nullable=False)
    vu         = Column(Boolean,  nullable=False, default=False, server_default="false")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow())

    medecin = relationship("Medecin")

    def __repr__(self):
        return f"<Avis {self.id} medecin={self.medecin_id} note={self.note}>"

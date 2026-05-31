import random, string
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class MembreCommunaute(Base):
    __tablename__ = "membres_communaute"

    id            = Column(String(15), primary_key=True, default=generate_id)
    communaute_id = Column(String(15), ForeignKey("communautes.id", ondelete="CASCADE"), nullable=False)
    medecin_id    = Column(String(15), ForeignKey("medecins.id",    ondelete="CASCADE"), nullable=False)
    role          = Column(
        Enum("createur", "admin", "membre", name="role_membre"),
        nullable=False,
        default="membre",
    )
    statut        = Column(
        Enum("en_attente", "accepte", "refuse", name="statut_membre"),
        nullable=False,
        default="accepte",
    )
    joined_at     = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("communaute_id", "medecin_id", name="uq_membre_communaute"),
    )

    # Relations
    communaute = relationship("Communaute", back_populates="membres")
    medecin    = relationship("Medecin",    back_populates="memberships")

    def __repr__(self):
        return f"<MembreCommunaute {self.id} medecin={self.medecin_id} role={self.role}>"

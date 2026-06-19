import random, string
from datetime import datetime, timezone

from sqlalchemy import Column, Boolean, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class FeedbackIA(Base):
    __tablename__ = "feedbacks_ia"

    id               = Column(String(15), primary_key=True, default=generate_id)
    diagnostic_id    = Column(String(15), ForeignKey("diagnostics_ia.id", ondelete="CASCADE"), nullable=False)
    medecin_id       = Column(String(15), ForeignKey("medecins.id",       ondelete="CASCADE"), nullable=False)
    concordance      = Column(Boolean,     nullable=True)        # l'IA avait-elle raison ?
    diagnostic_final = Column(String(200), nullable=True)        # diagnostic retenu par le médecin
    commentaire      = Column(Text,        nullable=True)
    created_at       = Column(DateTime,    nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relations
    diagnostic = relationship("DiagnosticIA", back_populates="feedbacks")
    medecin    = relationship("Medecin",      back_populates="feedbacks")

    def __repr__(self):
        return f"<FeedbackIA {self.id} concordance={self.concordance}>"

import random, string
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class DiagnosticIA(Base):
    __tablename__ = "diagnostics_ia"

    id                 = Column(String(15), primary_key=True, default=generate_id)
    consultation_id    = Column(
        String(15),
        ForeignKey("consultations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,   # 1 diagnostic par consultation
    )
    maladies           = Column(JSONB,      nullable=False)
    # Exemple: [{nom: "Pneumonie bactérienne", pct: 87, criteres: [...]}, ...]
    recommandations    = Column(JSONB,      nullable=True)
    # Exemple: [{type: "traitement", detail: "Antibiothérapie..."}]
    etat_patient       = Column(
        Enum("stable", "surveille", "urgent", "critique", name="etat_patient"),
        nullable=True,
    )
    version_modele     = Column(String(20), nullable=True)   # ex : "v1.2.0"
    duree_inference_ms = Column(Integer,    nullable=True)
    created_at         = Column(DateTime,   nullable=False, default=datetime.utcnow)

    # Relations
    consultation = relationship("Consultation", back_populates="diagnostic")
    feedbacks    = relationship("FeedbackIA",   back_populates="diagnostic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DiagnosticIA {self.id} consultation={self.consultation_id} etat={self.etat_patient}>"

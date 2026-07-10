import random, string
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class AvisPatient(Base):
    __tablename__ = "avis_patient"

    id         = Column(String(15), primary_key=True, default=generate_id)
    patient_id = Column(String(15), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    medecin_id = Column(String(15), ForeignKey("medecins.id", ondelete="CASCADE"), nullable=False)
    contenu    = Column(Text,       nullable=False)
    created_at = Column(DateTime,   nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    patient = relationship("Patient")
    medecin = relationship("Medecin")

    def __repr__(self):
        return f"<AvisPatient {self.id} patient={self.patient_id}>"

import random, string
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class AccesPatient(Base):
    __tablename__ = "acces_patient"

    id                      = Column(String(15), primary_key=True, default=generate_id)
    patient_id              = Column(String(15), ForeignKey("patients.id",  ondelete="CASCADE"), nullable=False)
    medecin_demandeur_id    = Column(String(15), ForeignKey("medecins.id",  ondelete="CASCADE"), nullable=False)
    medecin_proprietaire_id = Column(String(15), ForeignKey("medecins.id",  ondelete="CASCADE"), nullable=False)
    statut                  = Column(
        Enum("en_attente", "accorde", "refuse", name="statut_acces"),
        nullable=False,
        default="en_attente",
    )
    justificatif_demande = Column(Text,     nullable=True)
    motif_refus          = Column(Text,     nullable=True)
    created_at           = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at           = Column(DateTime, nullable=True,  onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("patient_id", "medecin_demandeur_id", name="uq_acces_medecin_patient"),
    )

    # Relations
    patient              = relationship("Patient", back_populates="acces")
    medecin_demandeur    = relationship("Medecin", foreign_keys=[medecin_demandeur_id])
    medecin_proprietaire = relationship("Medecin", foreign_keys=[medecin_proprietaire_id])

    def __repr__(self):
        return f"<AccesPatient {self.id} patient={self.patient_id} statut={self.statut}>"

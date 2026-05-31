import random, string
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, INET
from sqlalchemy.orm import relationship

from app.database import Base


def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id         = Column(String(15), primary_key=True, default=generate_id)
    medecin_id = Column(String(15), ForeignKey("medecins.id", ondelete="SET NULL"), nullable=True)
    action     = Column(String(200), nullable=False)
    # Exemples : 'LOGIN', 'DIAGNOSTIC_IA', 'CONSULTATION_CREE', 'PATIENT_MODIFIE'
    details    = Column(JSONB,       nullable=False, default=dict)
    ip_address = Column(INET,        nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime,    nullable=False, default=datetime.utcnow)

    # Relations
    medecin = relationship("Medecin", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.id} action={self.action} medecin={self.medecin_id}>"

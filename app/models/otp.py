import random, string
from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class OTPCode(Base):
    __tablename__ = "otp_codes"

    id         = Column(String(15), primary_key=True, default=generate_id)
    medecin_id = Column(String(15), ForeignKey("medecins.id", ondelete="CASCADE"), nullable=False)
    code       = Column(String(6),  nullable=False)          # code à 6 chiffres
    expires_at = Column(DateTime,   nullable=False)          # expiration dans 5 min
    used       = Column(Boolean,    nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow())
    
    # Relations
    medecin = relationship("Medecin", back_populates="otp_codes")

    def __repr__(self):
        return f"<OTPCode {self.id} medecin={self.medecin_id} used={self.used}>"

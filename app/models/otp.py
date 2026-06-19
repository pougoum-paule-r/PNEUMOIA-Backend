import random, string
from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database import Base


def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class OTPCode(Base):
    __tablename__ = "otp_codes"

    id         = Column(String(15), primary_key=True, default=generate_id)
    medecin_id = Column(String(15), ForeignKey("medecins.id", ondelete="CASCADE"), nullable=False)
    code       = Column(String(6),  nullable=False)
    expires_at = Column(DateTime,   nullable=False)
    used       = Column(Boolean,    nullable=False, default=False)
    purpose    = Column(String(20), nullable=False, default='login')   # 'login' | 'reset'
    fail_count = Column(Integer,    nullable=False, default=0)         # tentatives incorrectes
    created_at = Column(DateTime,   nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    
    # Relations
    medecin = relationship("Medecin", back_populates="otp_codes")

    def __repr__(self):
        return f"<OTPCode {self.id} medecin={self.medecin_id} used={self.used}>"

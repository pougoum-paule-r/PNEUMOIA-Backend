import random, string
from datetime import datetime

from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class Admin(Base):
    __tablename__ = "admins"

    id            = Column(String(15), primary_key=True, default=generate_id)
    nom           = Column(String(100), nullable=False)
    email         = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone         = Column(String(20),  nullable=True)   # numéro SMS configurable
    created_at    = Column(DateTime,    nullable=False, default=datetime.utcnow)
    updated_at    = Column(DateTime,    nullable=True,  onupdate=datetime.utcnow)

    # Relations
    medecins_valides = relationship("Medecin", back_populates="valideur", foreign_keys="Medecin.valide_par")

    def __repr__(self):
        return f"<Admin {self.id} — {self.email}>"

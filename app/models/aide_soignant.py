import random, string
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base

def generate_aide_id():
    return f"AIDE-{''.join(random.choices(string.digits, k=7))}"

def generate_code_referent():
    chars = string.ascii_uppercase + string.digits
    return f"AS-{''.join(random.choices(chars, k=5))}"

class AideSoignant(Base):
    __tablename__ = "aides_soignants"

    id            = Column(String(15),  primary_key=True, default=generate_aide_id)
    medecin_id    = Column(String(15),  ForeignKey("medecins.id", ondelete="CASCADE"), nullable=False)
    nom           = Column(String(100), nullable=False)
    prenom        = Column(String(100), nullable=False)
    email         = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    telephone     = Column(String(20),  nullable=True)
    statut        = Column(String(20),  nullable=False, default="en_attente")

    # Permissions
    peut_creer_patient    = Column(Boolean, nullable=False, default=True)
    peut_lire_dossier     = Column(Boolean, nullable=False, default=True)
    peut_modifier_patient = Column(Boolean, nullable=False, default=True)
    peut_saisir_symptomes = Column(Boolean, nullable=False, default=True)
    peut_supprimer        = Column(Boolean, nullable=False, default=False)
    peut_voir_diagnostic  = Column(Boolean, nullable=False, default=False)
    peut_prescrire        = Column(Boolean, nullable=False, default=False)

    preferences = Column(JSONB, nullable=True, server_default='{}')

    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relations
    medecin = relationship("Medecin", back_populates="aides_soignants")

    def __repr__(self):
        return f"<AideSoignant {self.prenom} {self.nom} ({self.statut})>"
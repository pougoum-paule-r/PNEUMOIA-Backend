# app/models/ressource.py
import random, string
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

def generate_ressource_id():
    return f"RES-{''.join(random.choices(string.digits, k=7))}"

class RessourceMedicale(Base):
    __tablename__ = "ressources_medicales"

    id         = Column(String(15),  primary_key=True, default=generate_ressource_id)
    medecin_id = Column(String(15),  ForeignKey("medecins.id", ondelete="CASCADE"), nullable=False)
    titre      = Column(String(300), nullable=False)
    resume     = Column(Text,        nullable=False)
    contenu    = Column(Text,        nullable=True)
    pdf_url    = Column(String(500), nullable=True)
    pathologie = Column(String(100), nullable=True)
    tags       = Column(JSON,        nullable=False, default=list)
    niveau     = Column(String(50),  nullable=True, default="3ème année")
    nb_telechargements = Column(Integer, nullable=False, default=0)
    nb_vues            = Column(Integer, nullable=False, default=0)
    publie     = Column(Boolean,     nullable=False, default=False)
    created_at = Column(DateTime,    nullable=False, default=lambda: datetime.utcnow())
    updated_at = Column(DateTime,    nullable=True,  onupdate=lambda: datetime.utcnow())

    medecin = relationship("Medecin", back_populates="ressources")

    def __repr__(self):
        return f"<RessourceMedicale {self.titre[:30]} publie={self.publie}>"
import random, string
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class DocumentMedecin(Base):
    __tablename__ = "documents_medecin"

    id            = Column(String(15), primary_key=True, default=generate_id)
    medecin_id    = Column(String(15), ForeignKey("medecins.id", ondelete="CASCADE"), nullable=False)
    type_document = Column(
        Enum(
            "diplome_specialisation",
            "diplome_medecine",
            "inscription_ordre",
            "autorisation_exercice",
            "carte_professionnelle",
            "cni",
            name="type_document",
        ),
        nullable=False,
    )
    url_fichier   = Column(String(500), nullable=False)
    nom_fichier   = Column(String(255), nullable=True)
    taille_octets = Column(Integer,     nullable=True)
    mime_type     = Column(String(100), nullable=True)
    statut        = Column(String(20),  nullable=False, default="en_attente")
    motif_rejet   = Column(String(500), nullable=True)
    created_at    = Column(DateTime,    nullable=False, default=lambda: datetime.utcnow())
    
    # Relations
    medecin = relationship("Medecin", back_populates="documents")

    def __repr__(self):
        return f"<DocumentMedecin {self.type_document} — {self.nom_fichier}>"

import random, string
from datetime import datetime

from sqlalchemy import Column, String, Date, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class Patient(Base):
    __tablename__ = "patients"

    id      = Column(String(15), primary_key=True, default=generate_id)
    nom     = Column(String(100), nullable=False)
    prenom  = Column(String(100), nullable=False)

    # ── Identité ─────────────────────────────────────────────────
    civilite       = Column(String(10),  nullable=True)   # "M" | "Mme"
    date_naissance = Column(Date,        nullable=True)
    sexe           = Column(Enum("M", "F", "autre", name="sexe_patient"), nullable=True)
    groupe_sanguin = Column(String(5),   nullable=True)
    religion       = Column(String(100), nullable=True)

    # ── Contact ──────────────────────────────────────────────────
    telephone  = Column(String(20),  nullable=True)
    email      = Column(String(150), nullable=True)
    adresse    = Column(String(300), nullable=True)
    profession = Column(String(150), nullable=True)

    # ── Urgence ──────────────────────────────────────────────────
    personne_a_contacter = Column(String(150), nullable=True)
    telephone_urgence    = Column(String(20),  nullable=True)

    # ── Données médicales (JSONB) ─────────────────────────────────
    allergies   = Column(JSONB, nullable=False, default=list)
    antecedents = Column(JSONB, nullable=False, default=dict)
    # Structure antecedents :
    # {
    #   diabete, hypertension, asthme, bpco, tuberculose, vih,
    #   hepatiteB, hepatiteC, cancerPoumon, tabagisme,
    #   cigarettesParJour, dureeTabagisme, alcool,
    #   traitementEnCours, allergieMedicaments,
    #   professionRisque, expositionProfessionnelle
    # }

    # ── Méta ─────────────────────────────────────────────────────
    created_by = Column(String(15), ForeignKey("medecins.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime,   nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime,   nullable=True,  onupdate=datetime.utcnow)

    # ── Soft-delete ───────────────────────────────────────────────
    deleted_at = Column(DateTime,   nullable=True, default=None)
    deleted_by = Column(String(15), ForeignKey("medecins.id", ondelete="SET NULL"), nullable=True)

    # ── Relations ─────────────────────────────────────────────────
    createur      = relationship("Medecin",      back_populates="patients_crees", foreign_keys=[created_by])
    consultations = relationship("Consultation", back_populates="patient")
    acces         = relationship("AccesPatient", back_populates="patient", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Patient {self.id} — {self.civilite} {self.prenom} {self.nom}>"
    
        # def __hello__(self):
        #     return f"Patient {self.id} — {self.civilite} {self.prenom} {self.nom}"
import random, string
from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


def generate_pneu_id():
    chiffres = ''.join(random.choices(string.digits, k=7))
    return f"PNEU-{chiffres}"


def generate_code_referent():
    chars = string.ascii_uppercase + string.digits
    return f"AS-{''.join(random.choices(chars, k=5))}"


class Medecin(Base):
    __tablename__ = "medecins"

    id            = Column(String(15), primary_key=True, default=generate_pneu_id)
    civilite      = Column(String(10),  nullable=True)
    nom           = Column(String(100), nullable=False)
    prenom        = Column(String(100), nullable=False)
    email         = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    specialite    = Column(String(100), nullable=True)
    numero_rpps   = Column(String(20),  unique=True, nullable=True)
    etablissement = Column(String(200), nullable=True)
    photo_url     = Column(String(500), nullable=True)
    telephone     = Column(String(30),  nullable=True)
    adresse       = Column(String(300), nullable=True)
    bio           = Column(Text,        nullable=True)
    linkedin      = Column(String(300), nullable=True)
    website       = Column(String(300), nullable=True)
    statut        = Column(
        Enum("en_attente", "valide", "rejete", "suspendu", name="statut_medecin"),
        nullable=False,
        default="en_attente",
    )
    motif_rejet        = Column(Text,       nullable=True)
    valide_par         = Column(String(15), ForeignKey("admins.id", ondelete="SET NULL"), nullable=True)
    valide_le          = Column(DateTime,   nullable=True)
    activation_token   = Column(String(255), nullable=True)
    activation_expires = Column(DateTime,   nullable=True)
    code_referent       = Column(String(10),  unique=True, nullable=True, default=generate_code_referent)
    code_referent_actif = Column(Boolean,     nullable=False, default=True)
    preferences         = Column(JSONB,       nullable=True,  server_default='{}')
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow())


    # Relations
    valideur           = relationship("Admin",            back_populates="medecins_valides", foreign_keys=[valide_par])
    documents          = relationship("DocumentMedecin",  back_populates="medecin",    cascade="all, delete-orphan")
    patients_crees     = relationship("Patient",          back_populates="createur",   foreign_keys="Patient.created_by")
    consultations      = relationship("Consultation",     back_populates="medecin",    foreign_keys="Consultation.medecin_id")
    feedbacks          = relationship("FeedbackIA",       back_populates="medecin")
    communautes_creees = relationship("Communaute",       back_populates="createur",   foreign_keys="Communaute.createur_id")
    memberships        = relationship("MembreCommunaute", back_populates="medecin")
    publications       = relationship("Publication",      back_populates="auteur")
    commentaires       = relationship("Commentaire",      back_populates="auteur")
    reactions          = relationship("Reaction",         back_populates="medecin")
    otp_codes          = relationship("OTPCode",          back_populates="medecin",    cascade="all, delete-orphan")
    audit_logs         = relationship("AuditLog",         back_populates="medecin")
    cas_cliniques      = relationship("CasCliniquPublic", back_populates="auteur")
    aides_soignants    = relationship("AideSoignant",     back_populates="medecin", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Medecin {self.id} — {self.prenom} {self.nom} ({self.statut})>"
    

    ressources = relationship("RessourceMedicale", back_populates="medecin", cascade="all, delete-orphan")
    questions  = relationship("QuestionMedecin",   back_populates="medecin", foreign_keys="QuestionMedecin.medecin_id")

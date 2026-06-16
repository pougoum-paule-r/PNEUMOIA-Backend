import random
import string
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


def generate_id() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=12))


class Admin(Base):
    __tablename__ = "admins"

    # ── Profil ─────────────────────────────────────────────────────────────────
    id            = Column(String(15),  primary_key=True, default=generate_id)
    nom           = Column(String(100), nullable=True)
    email         = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    # phone nullable=False : requis pour le reset OTP
    # Si la migration existe déjà avec nullable=True, faire :
    # ALTER TABLE admins ALTER COLUMN phone SET NOT NULL;
    phone = Column(String(20), index=True, nullable=True)

    # ── Reset mot de passe OTP ────────────────────────────────────────────────
    reset_otp     = Column(String(6),   nullable=True)   # ex: "849201"
    otp_expiry    = Column(DateTime,    nullable=True)   # expiration dans 10 min

    # ── Audit ──────────────────────────────────────────────────────────────────
    created_at    = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at    = Column(DateTime, nullable=True,  onupdate=datetime.utcnow)

    # ── Relations ──────────────────────────────────────────────────────────────
    # cascade="all, delete-orphan" signifie que si l'admin est supprimé,
    # ses médecins validés sont aussi supprimés — à revoir selon la logique métier
    medecins_valides = relationship(
        "Medecin",
        back_populates="valideur",
        foreign_keys="Medecin.valide_par",
        cascade="save-update, merge",  # retiré delete-orphan : un médecin validé
        # ne doit pas être supprimé si l'admin est supprimé
    )

    questions_repondues = relationship("QuestionMedecin", back_populates="repondant",
                                   foreign_keys="QuestionMedecin.repondu_par")
                                   
    faq_publiees        = relationship("FAQPubliee", back_populates="admin")
    # ── Méthodes utilitaires ───────────────────────────────────────────────────
    def is_otp_valid(self, provided_otp: str) -> bool:
        """Vérifie si l'OTP est correct et non expiré."""
        if not self.reset_otp or not self.otp_expiry:
            return False
        if datetime.utcnow() > self.otp_expiry:
            return False
        return self.reset_otp == provided_otp

    def clear_otp(self) -> None:
        """Efface l'OTP après utilisation."""
        self.reset_otp  = None
        self.otp_expiry = None

    def __repr__(self) -> str:
        return f"<Admin(id='{self.id}', email='{self.email}')>"
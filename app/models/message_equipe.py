import random, string
from datetime import datetime

from sqlalchemy import (
    Column, String, Text, Integer, Boolean,
    DateTime, Enum, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.database import Base


def generate_msg_id():
    return f"MSG-{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}"

def generate_like_id():
    return f"LKM-{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}"


class MessageEquipe(Base):
    """
    Canal de communication partagé entre un médecin et ses aides soignants.
    L'équipe est définie par medecin_referent_id.
    Supporte les réponses imbriquées (parent_id) et les likes.
    """
    __tablename__ = "messages_equipe"

    id                  = Column(String(20), primary_key=True, default=generate_msg_id)
    medecin_referent_id = Column(String(15), ForeignKey("medecins.id", ondelete="CASCADE"),        nullable=False)
    auteur_type         = Column(Enum("medecin", "aide_soignant", name="auteur_type_msg"),         nullable=False)
    auteur_medecin_id   = Column(String(15), ForeignKey("medecins.id",       ondelete="SET NULL"), nullable=True)
    auteur_aide_id      = Column(String(15), ForeignKey("aides_soignants.id", ondelete="SET NULL"),nullable=True)
    parent_id           = Column(String(20), ForeignKey("messages_equipe.id", ondelete="CASCADE"), nullable=True)

    contenu     = Column(Text,    nullable=False)
    type_msg    = Column(Enum("rapport", "alerte", "info", name="type_message_equipe"), nullable=False, default="rapport")
    pinned      = Column(Boolean, nullable=False, default=False)
    likes_count = Column(Integer, nullable=False, default=0)
    created_at  = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relations
    medecin_referent = relationship("Medecin", foreign_keys=[medecin_referent_id], backref="equipe_messages_recus")
    auteur_medecin   = relationship("Medecin", foreign_keys=[auteur_medecin_id])
    auteur_aide      = relationship("AideSoignant", foreign_keys=[auteur_aide_id])
    parent           = relationship("MessageEquipe", remote_side="MessageEquipe.id", foreign_keys=[parent_id], backref="replies")
    likes            = relationship("LikeMessageEquipe", back_populates="message", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MessageEquipe {self.id} type={self.type_msg} ref={self.medecin_referent_id}>"


class LikeMessageEquipe(Base):
    """Suivi des likes sur les messages d'équipe (pour le toggle)."""
    __tablename__ = "likes_messages_equipe"

    id          = Column(String(20), primary_key=True, default=generate_like_id)
    message_id  = Column(String(20), ForeignKey("messages_equipe.id", ondelete="CASCADE"), nullable=False)
    auteur_type = Column(Enum("medecin", "aide_soignant", name="auteur_type_like_msg"), nullable=False)
    auteur_id   = Column(String(20), nullable=False)   # id du médecin ou de l'aide (pas de FK pour rester polymorphe)

    __table_args__ = (
        UniqueConstraint("message_id", "auteur_id", name="uq_like_msg_auteur"),
    )

    message = relationship("MessageEquipe", back_populates="likes")

    def __repr__(self):
        return f"<LikeMessageEquipe msg={self.message_id} by={self.auteur_type}:{self.auteur_id}>"

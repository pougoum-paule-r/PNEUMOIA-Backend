import random, string
from datetime import datetime

from sqlalchemy import Column, String, Text, Integer, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

def generate_like_id():
    return f"LKC-{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}"


class Commentaire(Base):
    __tablename__ = "commentaires"

    id             = Column(String(15), primary_key=True, default=generate_id)
    publication_id = Column(String(15), ForeignKey("publications.id",    ondelete="CASCADE"),  nullable=False)
    parent_id      = Column(String(15), ForeignKey("commentaires.id",    ondelete="CASCADE"),  nullable=True)

    # Auteur polymorphe : médecin OU aide soignant
    auteur_type    = Column(Enum("medecin", "aide_soignant", name="auteur_type_commentaire"), nullable=False, default="medecin")
    auteur_id      = Column(String(15), ForeignKey("medecins.id",       ondelete="RESTRICT"), nullable=True)
    auteur_aide_id = Column(String(15), ForeignKey("aides_soignants.id", ondelete="RESTRICT"),nullable=True)

    contenu     = Column(Text,    nullable=False)
    likes_count = Column(Integer, nullable=False, default=0)
    created_at  = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relations
    publication  = relationship("Publication",  back_populates="commentaires")
    auteur       = relationship("Medecin",       foreign_keys=[auteur_id],      back_populates="commentaires")
    auteur_aide  = relationship("AideSoignant",  foreign_keys=[auteur_aide_id])
    parent       = relationship("Commentaire",   remote_side="Commentaire.id",  foreign_keys=[parent_id], backref="replies")
    likes        = relationship("LikeCommentaire", back_populates="commentaire", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Commentaire {self.id} publication={self.publication_id} by={self.auteur_type}>"


class LikeCommentaire(Base):
    """Suivi des likes sur les commentaires (pour le toggle)."""
    __tablename__ = "likes_commentaires"

    id          = Column(String(20), primary_key=True, default=generate_like_id)
    commentaire_id = Column(String(15), ForeignKey("commentaires.id", ondelete="CASCADE"), nullable=False)
    auteur_type = Column(Enum("medecin", "aide_soignant", name="auteur_type_like_com"), nullable=False)
    auteur_id   = Column(String(20), nullable=False)  # polymorphe

    __table_args__ = (
        UniqueConstraint("commentaire_id", "auteur_id", name="uq_like_com_auteur"),
    )

    commentaire = relationship("Commentaire", back_populates="likes")

    def __repr__(self):
        return f"<LikeCommentaire com={self.commentaire_id} by={self.auteur_type}:{self.auteur_id}>"

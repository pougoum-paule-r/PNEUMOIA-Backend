import random, string

from sqlalchemy import Column, String, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class Reaction(Base):
    __tablename__ = "reactions"

    id             = Column(String(15), primary_key=True, default=generate_id)
    publication_id = Column(String(15), ForeignKey("publications.id", ondelete="CASCADE"), nullable=False)
    medecin_id     = Column(String(15), ForeignKey("medecins.id",     ondelete="CASCADE"), nullable=False)
    type           = Column(
        Enum("utile", "insightful", "accord", "desaccord", name="type_reaction"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("publication_id", "medecin_id", name="uq_reaction_medecin_publication"),
    )

    # Relations
    publication = relationship("Publication", back_populates="reactions")
    medecin     = relationship("Medecin",     back_populates="reactions")

    def __repr__(self):
        return f"<Reaction {self.id} type={self.type} publication={self.publication_id}>"

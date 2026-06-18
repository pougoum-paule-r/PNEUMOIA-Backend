import random
import string
from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


def _gen_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class Avis(Base):
    __tablename__ = "avis"

    id            = Column(String(15),  primary_key=True, default=_gen_id)
    medecin_id    = Column(String(15),  ForeignKey("medecins.id", ondelete="CASCADE"), nullable=False)

    prenom        = Column(String(100), nullable=False)
    nom           = Column(String(100), nullable=False)
    civilite      = Column(String(20),  nullable=True)
    specialite    = Column(String(150), nullable=True)
    etablissement = Column(String(200), nullable=True)
    ville         = Column(String(100), nullable=True)
    photo_url     = Column(String(500), nullable=True)

    note          = Column(Integer,     nullable=False, default=5)
    commentaire   = Column(Text,        nullable=False)
    statut        = Column(String(20),  nullable=False, default="publie")
    vu            = Column(Boolean,     nullable=False, default=False)
    created_at    = Column(DateTime,    nullable=False, default=datetime.utcnow)

    medecin = relationship("Medecin", lazy="select")

    def __repr__(self):
        return f"<Avis {self.id} médecin={self.medecin_id} note={self.note}>"

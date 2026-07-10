import random, string
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, DateTime, Enum
from app.database import Base


def _gen_id():
    return "REQ-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=10))


class RequeteMedecin(Base):
    __tablename__ = "requetes_medecins"

    id            = Column(String(20), primary_key=True, default=_gen_id)
    medecin_id    = Column(String(15), nullable=False)
    nom_medecin   = Column(String(300), nullable=True)
    email_medecin = Column(String(300), nullable=True)
    titre         = Column(String(300), nullable=False)
    categorie     = Column(
        Enum("bug_technique", "probleme_acces", "erreur_ia",
             "lenteur", "interface", "autre", name="categorie_requete"),
        nullable=False, default="autre",
    )
    description   = Column(Text, nullable=False)
    statut        = Column(
        Enum("en_attente", "en_cours", "resolu", "ferme", name="statut_requete"),
        nullable=False, default="en_attente",
    )
    action_admin  = Column(String(300), nullable=True)
    reponse_admin = Column(Text,        nullable=True)
    repondu_par   = Column(String(15),  nullable=True)
    repondu_le    = Column(DateTime,    nullable=True)
    created_at    = Column(DateTime,    nullable=False,
                           default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    traite_le     = Column(DateTime,    nullable=True)

    def __repr__(self):
        return f"<RequeteMedecin {self.id} {self.statut}>"

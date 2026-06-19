import random, string
from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, Text, DateTime, Enum
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base


def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class Notification(Base):
    __tablename__ = "notifications"

    id              = Column(String(15), primary_key=True, default=generate_id)
    destinataire_id = Column(String(15), nullable=False)   # medecin.id ou admin.id
    type_dest       = Column(
        Enum("medecin", "admin", "aide_soignant", name="type_destinataire"),
        nullable=False,
    )
    type_notif      = Column(String(100), nullable=False)
    # Exemples : 'acces_patient_demande', 'compte_valide', 'nouveau_commentaire'
    titre           = Column(String(300), nullable=False)
    message         = Column(Text,        nullable=True)
    meta            = Column(JSONB,       nullable=False, default=dict)
    # Exemple : {lien: "/patients/PAT-...", patient_id: "..."}
    lu              = Column(Boolean,     nullable=False, default=False)
    created_at      = Column(DateTime,    nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Pas de FK directe : destinataire peut être medecin ou admin
    def __repr__(self):
        return f"<Notification {self.id} {self.type_notif} → {self.type_dest} lu={self.lu}>"

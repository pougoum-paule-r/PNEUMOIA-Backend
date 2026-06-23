from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base


class Parametre(Base):
    __tablename__ = "parametres"

    id         = Column(String(36),  primary_key=True)
    cle        = Column(String(100), nullable=False, unique=True, index=True)
    valeur     = Column(JSONB,       nullable=False, default=dict)
    updated_at = Column(DateTime,    nullable=True,
                        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
                        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    def __repr__(self):
        return f"<Parametre cle={self.cle!r}>"

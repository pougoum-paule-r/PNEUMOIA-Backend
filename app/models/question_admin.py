import random, string
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


def _gen_id():
    return f"QST-{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}"


class QuestionAdmin(Base):
    """
    Question posée par un médecin à l'administrateur de la plateforme.
    L'admin peut répondre et optionnellement publier la question en FAQ.
    """
    __tablename__ = "questions_admin"

    id         = Column(String(20), primary_key=True, default=_gen_id)
    medecin_id = Column(String(15), ForeignKey("medecins.id", ondelete="CASCADE"), nullable=False)

    titre      = Column(String(200), nullable=False)
    message    = Column(Text,        nullable=False)
    statut     = Column(
        Enum("en_attente", "repondu", "publiee_faq", name="statut_question_admin"),
        nullable=False, default="en_attente"
    )
    reponse    = Column(Text, nullable=True)

    created_at  = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    repondu_at  = Column(DateTime, nullable=True)

    medecin = relationship("Medecin", foreign_keys=[medecin_id], lazy="noload")

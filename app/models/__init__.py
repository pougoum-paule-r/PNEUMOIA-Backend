# Importation de tous les modèles pour qu'Alembic et SQLAlchemy les détectent
from app.models.admin            import Admin
from app.models.medecin          import Medecin
from app.models.document_medecin import DocumentMedecin
from app.models.patient          import Patient
from app.models.acces_patient    import AccesPatient
from app.models.consultation     import Consultation
from app.models.diagnostic_ia    import DiagnosticIA
from app.models.feedback_ia      import FeedbackIA
from app.models.communaute       import Communaute
from app.models.membre_communaute import MembreCommunaute
from app.models.publication      import Publication
from app.models.commentaire      import Commentaire
from app.models.reaction         import Reaction
from app.models.otp              import OTPCode
from app.models.notification     import Notification
from app.models.audit_log        import AuditLog
from app.models.cas_clinique_public import CasCliniquPublic
from app.models.question_medecin import QuestionMedecin
from app.models.faq_publiee      import FAQPubliee

__all__ = [
    "Admin",
    "Medecin",
    "DocumentMedecin",
    "Patient",
    "AccesPatient",
    "Consultation",
    "DiagnosticIA",
    "FeedbackIA",
    "Communaute",
    "MembreCommunaute",
    "Publication",
    "Commentaire",
    "Reaction",
    "OTPCode",
    "Notification",
    "AuditLog",
    "CasCliniquPublic",
    "QuestionMedecin",
    "FAQPubliee"
]

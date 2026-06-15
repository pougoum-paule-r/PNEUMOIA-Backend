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
from app.models.questionMedecins import QuestionMedecin
from app.models.faqPubliee       import FAQPubliee
from app.models.aide_soignant       import AideSoignant
from app.models.avis_patient        import AvisPatient
from app.models.ressource           import RessourceMedicale
from app.models.message_equipe      import MessageEquipe, LikeMessageEquipe
from app.models.commentaire         import LikeCommentaire  # Commentaire already imported above
from app.models.question_admin      import QuestionAdmin

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
    "LikeCommentaire",
    "Reaction",
    "OTPCode",
    "Notification",
    "AuditLog",
    "CasCliniquPublic",
    "QuestionMedecin",
    "FAQPubliee"
    "AideSoignant",
    "AvisPatient",
    "RessourceMedicale",
    "MessageEquipe",
    "LikeMessageEquipe",
    "QuestionAdmin",
]

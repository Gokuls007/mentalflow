# Import all models here so that Alembic can detect them
from app.db.base_class import Base # noqa
from app.models.user import User, TokenBlacklist # noqa
from app.models.clinical import Activity, MoodLog, Assessment, GameSession # noqa
from app.models.rl import RLState # noqa
from app.models.audit import AuditLog # noqa
from app.models.chat_message import ChatMessage # noqa
from app.models.crisis_alert import CrisisAlert # noqa
from app.models.therapist import Therapist, ClinicalPrescription # noqa

import logging
import secrets

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User
from app.security.auth import hash_password

logger = logging.getLogger(__name__)


def seed_demo_user(db: Session) -> None:
    """
    Create the demo account on a fresh install so the demo frontend (user 1) works.
    Runs only when DEMO_MODE is on and the user table is empty, so it is idempotent.
    """
    if not settings.DEMO_MODE or db.query(User.id).first() is not None:
        return

    password = settings.DEMO_USER_PASSWORD
    generated = not password
    if generated:
        password = secrets.token_urlsafe(12)

    db.add(User(
        email=settings.DEMO_USER_EMAIL,
        password_hash=hash_password(password),
        first_name="Demo",
        last_name="User",
        role="patient",
    ))
    try:
        db.commit()
    except IntegrityError:
        # Another worker seeded it first
        db.rollback()
        return

    if generated:
        logger.warning(
            "Created demo account %s with generated password: %s "
            "(shown once; set DEMO_USER_PASSWORD to choose one, DEMO_MODE=false to disable)",
            settings.DEMO_USER_EMAIL, password,
        )
    else:
        logger.info("Created demo account %s (password from DEMO_USER_PASSWORD)", settings.DEMO_USER_EMAIL)

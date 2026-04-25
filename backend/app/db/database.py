from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings

# Build engine kwargs based on database type
engine_kwargs = {
    "echo": settings.DATABASE_ECHO,
}

# SQLite needs special handling for FastAPI's async threading
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_pre_ping"] = True

# Create database engine
engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency: Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

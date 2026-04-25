from sqlalchemy import Column, Integer, String, Boolean, DateTime, Index, func, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    age = Column(Integer)
    
    # Mental health profile
    anxiety_trigger = Column(String(50), default="general")
    baseline_phq9 = Column(Integer)
    baseline_gad7 = Column(Integer)
    
    # RL Configuration
    rl_model_trained = Column(Boolean, default=False)
    rl_model_path = Column(String(500))
    rl_last_updated = Column(DateTime)
    
    # Roles & Clinical Management
    role = Column(String(50), default="patient") # patient, professional, researcher
    assigned_professional_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    
    # Metadata
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime)
    
    # Relationships
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")
    mood_logs = relationship("MoodLog", back_populates="user", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="user", cascade="all, delete-orphan")
    game_sessions = relationship("GameSession", back_populates="user", cascade="all, delete-orphan")
    rl_state = relationship("RLState", back_populates="user", uselist=False, cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    crisis_alerts = relationship("CrisisAlert", back_populates="user", cascade="all, delete-orphan")
    
    # Professional-Patient mapping
    assigned_professional = relationship("User", remote_side=[id], backref="clients")
    
    __table_args__ = (
        CheckConstraint("age >= 18 AND age <= 120", name="check_age_range"),
        CheckConstraint("baseline_phq9 >= 0 AND baseline_phq9 <= 27", name="check_phq9_range"),
        CheckConstraint("baseline_gad7 >= 0 AND baseline_gad7 <= 21", name="check_gad7_range"),
        CheckConstraint("role IN ('patient', 'professional', 'researcher', 'admin')", name="check_valid_role"),
        Index('idx_user_email', email),
        Index('idx_user_created_at', created_at),
        Index('idx_user_is_active', is_active),
        Index('idx_user_role', role),
    )

class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    jti = Column(String(500), nullable=False, unique=True)
    user_id = Column(Integer, index=True) # Linked but not strictly FK for blacklist
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

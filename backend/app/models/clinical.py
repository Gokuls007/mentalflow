from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Date, Text, Boolean, func, JSON, Index, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

# Use JSON instead of JSONB for SQLite compatibility
try:
    from sqlalchemy.dialects.postgresql import JSONB
except ImportError:
    JSONB = JSON

# Always use generic JSON so SQLite works out of the box
JSONB = JSON

class Activity(Base):
    __tablename__ = "activity"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    
    type = Column(String(50), nullable=False, index=True) # exercise, social, creative, etc.
    difficulty = Column(Float, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    
    date_scheduled = Column(Date, index=True)
    date_completed = Column(Date)
    completed_at = Column(DateTime)
    
    title = Column(String(255))
    description = Column(Text)
    values = Column(JSONB) # Array of user values
    
    # Behavioral Activation (BA) Extensions
    source = Column(String(50), default="static", index=True) # static, rl, gan, ba_prescription
    is_micro_habit = Column(Boolean, default=False)
    ba_week = Column(Integer)
    clinical_explanation = Column(Text)
    
    completion_count = Column(Integer, default=0, nullable=False)
    last_completed = Column(DateTime)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    user = relationship("User", back_populates="activities")
    mood_logs = relationship("MoodLog", back_populates="activity")
    game_sessions = relationship("GameSession", back_populates="activity")
    
    __table_args__ = (
        CheckConstraint("difficulty >= 1.0 AND difficulty <= 10.0", name="check_activity_difficulty_range"),
        Index('idx_activity_user_type', user_id, type),
    )

class MoodLog(Base):
    __tablename__ = "mood_log"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    
    mood_score = Column(Integer, nullable=False)
    activity_id = Column(Integer, ForeignKey("activity.id", ondelete="SET NULL"), index=True)
    context = Column(String(100)) # before_activity, after_activity, general
    tags = Column(JSONB) # ["energy", "anxiety"]
    notes = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    
    user = relationship("User", back_populates="mood_logs")
    activity = relationship("Activity", back_populates="mood_logs")
    
    __table_args__ = (
        CheckConstraint("mood_score >= 1 AND mood_score <= 10", name="check_mood_score_range"),
    )

class Assessment(Base):
    __tablename__ = "assessment"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    
    type = Column(String(50), nullable=False, index=True) # phq9, gad7, bads
    score = Column(Integer, nullable=False, index=True)
    responses = Column(JSONB)
    severity = Column(String(50))
    
    date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    user = relationship("User", back_populates="assessments")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'type', 'date', name='uq_assessment_user_type_date'),
    )

class GameSession(Base):
    __tablename__ = "game_session"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_id = Column(Integer, ForeignKey("activity.id", ondelete="SET NULL"))
    
    difficulty_level = Column(String(20), nullable=False, index=True) # easy, medium, hard
    score = Column(Integer, default=0, nullable=False)
    completion_time = Column(Integer) # seconds
    completed = Column(Boolean, default=False, index=True)
    
    mood_before = Column(Integer)
    mood_after = Column(Integer)
    engagement_rating = Column(Integer)
    
    rl_reward = Column(Float)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    user = relationship("User", back_populates="game_sessions")
    activity = relationship("Activity", back_populates="game_sessions")
    
    __table_args__ = (
        CheckConstraint("mood_before >= 1 AND mood_before <= 10", name="check_game_mood_before"),
        CheckConstraint("mood_after >= 1 AND mood_after <= 10", name="check_game_mood_after"),
        CheckConstraint("engagement_rating >= 1 AND engagement_rating <= 10", name="check_game_engagement"),
    )

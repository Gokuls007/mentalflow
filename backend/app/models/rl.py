from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, func, Index, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class RLState(Base):
    __tablename__ = "rl_state"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # State vector (normalized 0-1)
    anxiety_level = Column(Float)
    phq9_normalized = Column(Float)
    gad7_normalized = Column(Float)
    activity_engagement = Column(Float)
    completion_rate = Column(Float)
    mood_trend = Column(Float)
    days_since_activity = Column(Float)
    
    # Last action & reward
    last_action = Column(Integer) # 0=easy, 1=medium, 2=hard
    last_reward = Column(Float)
    
    # Training metadata
    games_count = Column(Integer, default=0, nullable=False)
    last_updated = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    user = relationship("User", back_populates="rl_state")
    
    def to_numpy_array(self):
        """Convert state to numpy array for RL agent"""
        import numpy as np
        return np.array([
            self.anxiety_level or 0.0,
            self.phq9_normalized or 0.0,
            self.gad7_normalized or 0.0,
            self.activity_engagement or 0.0,
            self.completion_rate or 0.0,
            self.mood_trend or 0.0,
            self.days_since_activity or 0.0,
        ], dtype=np.float32)

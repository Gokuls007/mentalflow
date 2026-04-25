from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class CrisisAlert(Base):
    __tablename__ = "crisis_alert"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    
    risk_level = Column(String(50), nullable=False)  # LOW, MODERATE, HIGH, EXTREME
    trigger_message = Column(Text, nullable=False)
    
    detected_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    acknowledged = Column(Boolean, default=False, nullable=False, index=True)
    acknowledged_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="crisis_alerts")
    
    __table_args__ = (
        Index('idx_crisis_user_id_unacknowledged', user_id, acknowledged),
    )

from sqlalchemy import Column, Integer, String, DateTime, Text, func, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class AuditLog(Base):
    __tablename__ = "audit_log"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), index=True)
    action = Column(String(100), nullable=False) # login, assessment, etc.
    resource_type = Column(String(50)) # user, activity, assessment
    resource_id = Column(Integer)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    changes = Column(JSON) # What changed
    status = Column(String(20)) # success, failure
    error_message = Column(Text)
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    
    user = relationship("User", back_populates="audit_logs")
    
    __table_args__ = (
        Index('idx_audit_log_action_created', action, created_at),
    )

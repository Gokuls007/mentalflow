from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class ChatMessage(Base):
    __tablename__ = "chat_message"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    
    role = Column(String(50), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    intent = Column(String(50))  # CRISIS, ASSESSMENT, ACTIVITY, MOOD, SUPPORT, CHAT
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    
    user = relationship("User", back_populates="chat_messages")
    
    __table_args__ = (
        Index('idx_chat_user_id_created_at', user_id, created_at),
    )

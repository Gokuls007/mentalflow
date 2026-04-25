from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatMessageRequest(BaseModel):
    message: str

class ChatMessageResponse(BaseModel):
    content: str
    role: str
    intent: str
    timestamp: str

class ChatHistoryItem(BaseModel):
    id: int
    role: str
    content: str
    intent: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

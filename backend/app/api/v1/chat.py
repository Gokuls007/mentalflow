from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.models.user import User
from app.models.chat_message import ChatMessage
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse, ChatHistoryItem
from app.ai.clinical_chatbot import chatbot

router = APIRouter()

# Optional auth: tries token, falls back to None for demo mode
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.security.auth import decode_token

optional_security = HTTPBearer(auto_error=False)

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Try to get current user; return None if no/invalid token (demo mode)."""
    if credentials is None:
        return None
    token_data = decode_token(credentials.credentials)
    if token_data is None:
        return None
    user = db.query(User).filter(User.id == token_data.user_id).first()
    return user if user and user.is_active else None


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Send a message to the Clinical AI chatbot.
    Works with or without authentication (demo mode uses user_id=1).
    """
    user_id = current_user.id if current_user else 1
    try:
        result = chatbot.chat(db=db, user_id=user_id, message=request.message)
        return ChatMessageResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chatbot failed to process message: {str(e)}"
        )

@router.get("/history/{user_id}", response_model=List[ChatHistoryItem])
async def get_history(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get chat history for a user. No auth required in demo mode.
    """
    messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == user_id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    return messages

@router.delete("/history/{user_id}")
async def clear_history(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Clear chat history for a user. No auth required in demo mode.
    """
    db.query(ChatMessage).filter(ChatMessage.user_id == user_id).delete()
    db.commit()
    
    return {"status": "success", "message": "Chat history cleared"}

@router.get("/health")
async def chat_health():
    """
    Check if the chatbot is initialized properly.
    """
    from app.ai.clinical_chatbot import llm
    return {
        "status": "online" if llm is not None else "offline_fallback",
        "message": "Chat service is running."
    }

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.user import User
from app.models.chat_message import ChatMessage
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse, ChatHistoryItem
from app.ai.clinical_chatbot import chatbot

router = APIRouter()

# Auth is optional: without a token the request acts as the demo user (DEMO_MODE)
from app.security.auth import get_current_user_or_demo


def _check_history_access(user_id: int, current_user: User):
    """Only the owner may read or clear a chat history."""
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_demo)
):
    """
    Send a message to the Clinical AI chatbot.
    Works with or without authentication (demo mode uses the demo account).
    """
    user_id = current_user.id
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
    current_user: User = Depends(get_current_user_or_demo)
):
    """
    Get chat history for a user. No auth required in demo mode (demo user only).
    """
    _check_history_access(user_id, current_user)
    messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == user_id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    return messages

@router.delete("/history/{user_id}")
async def clear_history(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_demo)
):
    """
    Clear chat history for a user. No auth required in demo mode (demo user only).
    """
    _check_history_access(user_id, current_user)
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

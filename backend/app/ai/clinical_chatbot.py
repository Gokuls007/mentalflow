import os
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from app.models.chat_message import ChatMessage
from app.models.crisis_alert import CrisisAlert
from app.config import settings

logger = logging.getLogger(__name__)

class ClinicalChatbot:
    """
    Clinical AI Chatbot for Mental Health Support
    Includes intent classification and crisis detection.
    """
    
    def __init__(self):
        self.llm = self._initialize_llm()
        self.system_prompt = (
            "You are MentalFlow AI, a compassionate clinical mental health assistant. "
            "Your goal is to provide empathetic support, evidence-based coping strategies, "
            "and assist users with the MentalFlow platform. "
            "IMPORTANT: If you detect signs of self-harm or immediate crisis, you MUST "
            "trigger a CRISIS alert and provide 988 helpline resources immediately."
        )
        
    def _initialize_llm(self):
        try:
            api_key = settings.GROQ_API_KEY
            if not api_key or api_key == "YOUR_GROQ_API_KEY":
                logger.warning("GROQ_API_KEY not set. Using offline fallback mode.")
                return None
            return ChatGroq(temperature=0.3, model_name="llama3-70b-8192", groq_api_key=api_key)
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            return None

    def chat(self, db: Session, user_id: int, message: str) -> Dict[str, Any]:
        """
        Processes user message and returns AI response.
        """
        
        # 1. Detect Crisis (Simple Keywords for Safety)
        is_crisis = self._detect_crisis(message)
        
        # 2. Get Response
        if self.llm:
            try:
                response_text = self._get_ai_response(db, user_id, message)
            except Exception as e:
                logger.error(f"AI Response failed: {e}")
                response_text = self._get_fallback_response(message)
        else:
            response_text = self._get_fallback_response(message)
            
        # 3. Handle Crisis Logging
        if is_crisis:
            self._log_crisis(db, user_id, message)
            response_text = (
                "I'm concerned about what you're saying. Please know that you're not alone. "
                "If you're in immediate danger, please call 988 (Suicide & Crisis Lifeline) or "
                "emergency services immediately. \n\n" + response_text
            )

        # 4. Save to Database
        user_msg = ChatMessage(user_id=user_id, role="user", content=message)
        ai_msg = ChatMessage(user_id=user_id, role="assistant", content=response_text)
        db.add(user_msg)
        db.add(ai_msg)
        db.commit()
        
        return {
            "content": response_text,
            "role": "assistant",
            "intent": "CRISIS" if is_crisis else "SUPPORT",
            "timestamp": datetime.utcnow().isoformat()
        }

    def _detect_crisis(self, text: str) -> bool:
        keywords = ["suicide", "kill myself", "end it all", "die", "hurt myself", "self-harm"]
        return any(k in text.lower() for k in keywords)

    def _get_ai_response(self, db: Session, user_id: int, message: str) -> str:
        # Load recent history from DB
        history = db.query(ChatMessage).filter_by(user_id=user_id).order_by(ChatMessage.created_at.desc()).limit(5).all()
        chat_history = []
        for m in reversed(history):
            if m.role == "user":
                chat_history.append(HumanMessage(content=m.content))
            else:
                chat_history.append(AIMessage(content=m.content))
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])
        
        chain = prompt | self.llm
        result = chain.invoke({"input": message, "chat_history": chat_history})
        return result.content

    def _get_fallback_response(self, message: str) -> str:
        return "I'm currently in offline mode but I'm here to listen. How are you feeling today?"

    def _log_crisis(self, db: Session, user_id: int, content: str):
        alert = CrisisAlert(user_id=user_id, message_content=content, severity="HIGH")
        db.add(alert)
        db.commit()
        logger.warning(f"CRISIS ALERT for User {user_id}")

# Global instance
chatbot = ClinicalChatbot()
llm = chatbot.llm

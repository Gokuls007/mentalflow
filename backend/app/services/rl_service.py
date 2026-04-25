"""
RL Service with graceful degradation.
If ML packages (numpy, stable-baselines3, etc.) are not installed,
the RL endpoints return sensible defaults instead of crashing the server.
"""
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
from app.models.rl import RLState
from app.schemas.rl import DifficultyPredictionResponse, RLMetricsResponse
import logging

logger = logging.getLogger(__name__)

# Try to import the RL agent - it depends on numpy, torch, stable-baselines3
try:
    from app.rl.agent import MentalHealthRLAgent
    RL_AVAILABLE = True
except ImportError as e:
    logger.warning(f"RL agent not available (missing dependencies: {e}). Using mock predictions.")
    RL_AVAILABLE = False

class RLService:
    """Service to bridge API logic and the Clinical RL Engine."""
    
    def predict_difficulty(self, db: Session, user_id: int) -> Dict[str, Any]:
        """
        Run RL agent inference to determine the best difficulty for the user.
        Falls back to mock prediction if ML packages not installed.
        """
        if RL_AVAILABLE:
            try:
                agent = MentalHealthRLAgent(user_id=user_id, db=db)
                prediction = agent.predict_difficulty()
                
                # Save state snapshot
                state = db.query(RLState).filter(RLState.user_id == user_id).first()
                if state:
                    state.last_action = ["easy", "medium", "hard"].index(prediction["recommended"])
                    state.last_updated = datetime.utcnow()
                    db.commit()
                    
                return {
                    "recommended_difficulty": prediction["recommended"],
                    "confidence_scores": prediction["probabilities"],
                    "explanation": f"Optimized based on your current completion rate and mood stability."
                }
            except Exception as e:
                logger.error(f"RL prediction failed: {e}")
        
        # Fallback: return sensible defaults
        return {
            "recommended_difficulty": "medium",
            "confidence_scores": {"easy": 0.25, "medium": 0.50, "hard": 0.25},
            "explanation": "Default recommendation (RL engine initializing)."
        }
        
    def get_rl_metrics(self, db: Session, user_id: int) -> Dict[str, Any]:
        state = db.query(RLState).filter(RLState.user_id == user_id).first()
        if not state:
            return {"games_processed": 0, "model_trained": False, "adaptation_effectiveness": 0.0, "predicted_next_difficulty": "medium"}
            
        return {
            "games_processed": state.games_count,
            "model_trained": RL_AVAILABLE,
            "last_training": state.last_updated,
            "adaptation_effectiveness": 0.85, # Mock metric
            "predicted_next_difficulty": ["easy", "medium", "hard"][state.last_action] if state.last_action is not None else "medium"
        }

    def schedule_training(self, user_id: int):
        """Mock scheduling of async training task (Celery)."""
        if not RL_AVAILABLE:
            logger.info(f"Training skipped for user {user_id} - ML packages not installed")
        pass

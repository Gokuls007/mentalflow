from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.rl import RLState
from app.ai.rl_engine import rl_engine
from app.ai.gymnasium_env import MentalHealthEnv
import numpy as np
from datetime import datetime

router = APIRouter()

@router.get("/predict-difficulty/{user_id}")
async def predict_difficulty(user_id: int, db: Session = Depends(get_db)):
    """
    Get RL-predicted difficulty for user
    
    1. Get user's current state (anxiety, depression, engagement, etc)
    2. Run through trained PPO model
    3. Return predicted difficulty + confidence
    """
    
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user state
    env = MentalHealthEnv(user_id=user_id, db=db)
    state = env._get_state()
    
    # Predict with RL model
    prediction = rl_engine.predict_difficulty(state)
    
    # Save to database
    rl_state = db.query(RLState).filter_by(user_id=user_id).first()
    if not rl_state:
        rl_state = RLState(user_id=user_id)
        db.add(rl_state)
    
    # Update individual columns (based on gymnasium_env.py state vector)
    # [anxiety, depression, engagement, completion_rate, mood_trend, days_since_activity]
    rl_state.anxiety_level = float(state[0])
    # Mapping to PHQ9/GAD7 normalized if available, or just using the state slots
    rl_state.gad7_normalized = float(state[0])
    rl_state.phq9_normalized = float(state[1])
    rl_state.activity_engagement = float(state[2])
    rl_state.completion_rate = float(state[3])
    rl_state.mood_trend = float(state[4])
    rl_state.days_since_activity = float(state[5])
    
    rl_state.last_action = ["EASY", "MEDIUM", "HARD"].index(prediction["difficulty"])
    rl_state.last_updated = datetime.utcnow()
    
    db.commit()
    
    return {
        "user_id": user_id,
        "difficulty": prediction["difficulty"],
        "confidence": prediction["confidence"],
        "action_probabilities": {
            "easy": prediction["action_probs"][0],
            "medium": prediction["action_probs"][1],
            "hard": prediction["action_probs"][2]
        },
        "reasoning": "Based on user's clinical state, historical engagement, and longitudinal mood trends"
    }

@router.post("/train", status_code=status.HTTP_202_ACCEPTED)
async def train_rl_model(db: Session = Depends(get_db)):
    """
    Manually trigger RL model training for all active users
    """
    
    try:
        from app.ai.rl_training import train_all_users
        train_all_users(db)
        
        return {
            "status": "success",
            "message": "Global RL model retraining completed",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/{user_id}")
async def get_rl_metrics(user_id: int, db: Session = Depends(get_db)):
    """
    Get detailed RL metrics and state breakdown for user
    """
    
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    metrics = rl_engine.get_metrics(user_id, db)
    
    return metrics

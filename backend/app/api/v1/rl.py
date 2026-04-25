from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.rl import RLState
from app.ai.rl_engine import rl_engine
from app.ai.gymnasium_env import MentalHealthEnv
from app.schemas.rl import GameResultSubmit
from app.models.clinical import GameSession, Activity
from app.services.clinical import calculate_xp_and_impact
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
@router.post("/submit-game-results")
async def submit_game_results(
    result: GameResultSubmit,
    db: Session = Depends(get_db)
):
    """
    Submit results of a game session and update RL + Game Mechanics
    """
    
    # 1. Save GameSession record
    game_session = db.query(GameSession).filter_by(activity_id=result.activity_id, completed=False).order_by(GameSession.created_at.desc()).first()
    
    if not game_session:
        # Create new if not found
        game_session = GameSession(
            user_id=1, # In real app, get from current_user
            activity_id=result.activity_id
        )
        db.add(game_session)
    
    game_session.score = result.score
    game_session.completion_time = result.duration
    game_session.completed = result.completed
    game_session.mood_before = result.mood_before
    game_session.mood_after = result.mood_after
    game_session.engagement_rating = result.engagement_rating
    
    # 2. Mark Activity as completed
    activity = db.query(Activity).filter_by(id=result.activity_id).first()
    if activity:
        activity.completed_at = datetime.utcnow()
        activity.completion_count += 1
    
    # 3. Calculate REAL Clinical Impact (Symptom Reduction)
    from app.services.clinical_outcomes import ClinicalOutcomeTracker
    tracker = ClinicalOutcomeTracker(db)
    clinical_outcomes = tracker.calculate_clinical_impact(user.id, {
        "type": activity.type if activity else "SELF_CARE",
        "pre_mood": result.mood_before,
        "post_mood": result.mood_after,
        "engagement": result.engagement_rating,
        "completed": result.completed
    })
    
    # Still track XP for legacy gamification
    impact = calculate_xp_and_impact(user, game_session, db)
    
    # 4. Update RL Engine
    rl_engine.update_reward(
        user_id=user.id,
        activity_id=result.activity_id,
        completed=result.completed,
        pre_mood=result.mood_before,
        post_mood=result.mood_after,
        engagement=result.engagement_rating,
        db=db
    )
    
    db.commit()
    
    return {
        "status": "success",
        "impact": impact,
        "clinical_outcomes": clinical_outcomes,
        "xp_earned": impact["xp_earned"],
        "new_level": impact["new_level"]
    }

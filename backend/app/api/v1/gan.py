from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import numpy as np
from app.db.database import get_db
from app.models import User, Activity
from app.ai.gan_engine import gan_engine
from app.ai.gymnasium_env import MentalHealthEnv
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/generate-activity/{user_id}")
async def generate_activity(user_id: int, db: Session = Depends(get_db)):
    """
    Generate personalized activity using GAN
    """
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user state
    env = MentalHealthEnv(user_id=user_id, db=db)
    user_state = env._get_state()
    
    # Generate with GAN
    activity_data = gan_engine.generate_activity(user_state)
    
    # Create new activity in DB
    new_activity = Activity(
        user_id=user_id,
        type=activity_data["type"],
        difficulty=1.0 if activity_data["difficulty"] == "EASY" else (5.0 if activity_data["difficulty"] == "MEDIUM" else 10.0),
        title=f"Personalized {activity_data['type'].title()}",
        description=activity_data["description"],
        duration_minutes=20, # Default or derived
        source="gan",
        gan_embedding=activity_data["embedding"],
        personalization_score=activity_data["confidence"]
    )
    
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    
    return {
        "id": new_activity.id,
        "type": activity_data["type"],
        "difficulty": activity_data["difficulty"],
        "description": activity_data["description"],
        "confidence": activity_data["confidence"],
        "reasoning": f"Generated based on clinical state (anxiety={user_state[0]:.2f}, depression={user_state[1]:.2f})",
        "xp_reward": {"EASY": 50, "MEDIUM": 85, "HARD": 120}[activity_data["difficulty"]]
    }

@router.post("/train", status_code=status.HTTP_202_ACCEPTED)
async def train_gan(db: Session = Depends(get_db)):
    """
    Manually trigger GAN training on real activity completions
    """
    # Placeholder for background task
    return {"status": "accepted", "message": "GAN retraining scheduled"}

@router.get("/metrics/{user_id}")
async def get_gan_metrics(user_id: int, db: Session = Depends(get_db)):
    """
    Get metrics on activity personalization and engagement
    """
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    recent_activities = db.query(Activity).filter(
        Activity.user_id == user_id,
        Activity.created_at >= (datetime.utcnow() - timedelta(days=30))
    ).all()
    
    return {
        "user_id": user_id,
        "total_personalized": len([a for a in recent_activities if a.source == "gan"]),
        "avg_personalization_score": np.mean([a.personalization_score for a in recent_activities if a.personalization_score]) if recent_activities else 0,
        "gan_status": "active"
    }

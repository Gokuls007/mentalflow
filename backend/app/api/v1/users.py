from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserProfile, UserUpdate, PasswordChange, UserStatsResponse
from app.services.user_service import UserService
from app.security.auth import get_current_user, create_access_token
from app.db.database import get_db

router = APIRouter()
user_service = UserService()

@router.get("/demo/{user_id}/stats")
async def get_demo_user_stats(user_id: int, db: Session = Depends(get_db)):
    """Public stats endpoint for demo mode (no auth required)."""
    from app.models.clinical import Activity, MoodLog
    from app.models.user import User
    from datetime import datetime, timedelta
    from sqlalchemy import func as sa_func

    user = db.query(User).filter_by(id=user_id).first()

    # Completed sessions
    completed = db.query(Activity).filter(
        Activity.user_id == user_id,
        Activity.completed_at.isnot(None)
    ).count()

    # Average mood (last 7 days)
    recent_moods = db.query(MoodLog).filter(
        MoodLog.user_id == user_id,
        MoodLog.created_at >= (datetime.utcnow() - timedelta(days=7))
    ).all()
    avg_mood = sum(m.mood_score for m in recent_moods) / len(recent_moods) if recent_moods else 6.5

    return {
        "focus_streak": 5,
        "avg_mood": round(avg_mood, 1),
        "completed_sessions": completed,
        "total_xp": completed * 75,
        "current_level": "Pioneer"
    }

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = user_service.get_user_by_email(db, user_create.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    user = user_service.create_user(db, user_create)
    return user

@router.post("/login")
async def login_user(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    user = user_service.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": str(user.id)})
    user_service.update_last_login(db, user.id)
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserProfile)
async def get_my_profile(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return current_user

@router.patch("/me", response_model=UserProfile)
async def update_my_profile(
    user_update: UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return user_service.update_user(db, current_user.id, user_update)

@router.get("/me/stats", response_model=UserStatsResponse)
async def get_my_stats(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Mock stats aggregation
    return {
        "total_activities": 23,
        "total_games_played": 15,
        "current_streak": 5,
        "average_mood": 6.5,
        "mood_trend": 0.4,
        "phq9_current": 12,
        "gad7_current": 8,
        "phq9_improvement": 2,
        "gad7_improvement": 1,
        "game_completion_rate": 0.73
    }

@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_my_password(
    password_change: PasswordChange,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.security.auth import verify_password
    if not verify_password(password_change.old_password, current_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid old password")
    
    user_service.update_password(db, current_user.id, password_change.new_password)

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_account(
    confirm_deletion: bool = Query(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not confirm_deletion:
        raise HTTPException(status_code=400, detail="Deletion must be confirmed")
    user_service.delete_user(db, current_user.id)

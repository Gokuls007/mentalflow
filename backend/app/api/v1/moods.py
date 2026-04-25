from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.schemas.activity import MoodLogCreate, MoodLogResponse, MoodTrendResponse
from app.services.mood_service import MoodService
from app.security.auth import get_current_user
from app.db.database import get_db

router = APIRouter()
mood_service = MoodService()

@router.post("/", response_model=MoodLogResponse, status_code=status.HTTP_201_CREATED)
async def log_mood(
    mood_in: MoodLogCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return mood_service.create_mood_log(db, current_user.id, mood_in)

@router.get("/today", response_model=List[MoodLogResponse])
async def get_today_moods(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return mood_service.get_moods_by_date(db, current_user.id, date.today())

@router.get("/history", response_model=List[MoodLogResponse])
async def get_mood_history(
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return mood_service.get_mood_history(db, current_user.id, days=days, limit=limit)

@router.get("/trend", response_model=MoodTrendResponse)
async def get_mood_trend(
    days: int = Query(7, ge=1, le=90),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return mood_service.calculate_mood_trend(db, current_user.id, days=days)

@router.get("/activity-correlation")
async def get_correlation(
    days: int = Query(7, ge=1, le=90),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return mood_service.get_activity_mood_correlation(db, current_user.id, days=days)

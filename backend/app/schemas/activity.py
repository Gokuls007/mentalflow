from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime, date

class ActivityBase(BaseModel):
    type: str # exercise, social, creative, etc.
    title: Optional[str] = None
    difficulty: float = Field(..., ge=1.0, le=10.0)
    duration_minutes: int = Field(..., gt=0)
    description: Optional[str] = None
    values: Optional[List[str]] = []

class ActivityCreate(ActivityBase):
    date_scheduled: Optional[date] = None

class ActivityUpdate(BaseModel):
    type: Optional[str] = None
    title: Optional[str] = None
    difficulty: Optional[float] = Field(None, ge=1.0, le=10.0)
    duration_minutes: Optional[int] = Field(None, gt=0)
    description: Optional[str] = None
    values: Optional[List[str]] = None
    date_scheduled: Optional[date] = None

class ActivityResponse(ActivityBase):
    id: int
    user_id: int
    date_scheduled: Optional[date] = None
    date_completed: Optional[date] = None
    completed_at: Optional[datetime] = None
    completion_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MoodLogBase(BaseModel):
    mood_score: int = Field(..., ge=1, le=10)
    context: Optional[str] = None # before_activity, after_activity, general
    tags: Optional[List[str]] = []
    notes: Optional[str] = None
    activity_id: Optional[int] = None

class MoodLogCreate(MoodLogBase):
    pass

class MoodLogResponse(MoodLogBase):
    id: int
    user_id: int
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class MoodTrendResponse(BaseModel):
    average_mood: float
    trend: float # Positive/Negative direction
    std_dev: float
    min_mood: int
    max_mood: int
    improvement_since_baseline: float

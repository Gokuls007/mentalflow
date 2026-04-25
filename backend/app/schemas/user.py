from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=18, le=120)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    anxiety_trigger: Optional[str] = "general"

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=18, le=120)
    anxiety_trigger: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

class UserProfile(UserResponse):
    anxiety_trigger: str
    baseline_phq9: Optional[int] = None
    baseline_gad7: Optional[int] = None
    rl_model_trained: bool
    last_login: Optional[datetime] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)

class UserStatsResponse(BaseModel):
    total_activities: int
    total_games_played: int
    current_streak: int
    average_mood: float
    mood_trend: float
    phq9_current: Optional[int] = None
    gad7_current: Optional[int] = None
    phq9_improvement: int
    gad7_improvement: int
    game_completion_rate: float

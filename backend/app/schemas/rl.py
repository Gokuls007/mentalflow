from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime

class DifficultyPredictionResponse(BaseModel):
    recommended_difficulty: str # easy, medium, hard
    confidence_scores: Dict[str, float] # {"easy": 0.1, ...}
    explanation: Optional[str] = None

class RLMetricsResponse(BaseModel):
    games_processed: int
    model_trained: bool
    last_training: Optional[datetime] = None
    adaptation_effectiveness: float # 0-1
    predicted_next_difficulty: str

class GameResultSubmit(BaseModel):
    activity_id: int
    score: int
    duration: int
    completed: bool
    mood_before: int = Field(..., ge=1, le=10)
    mood_after: int = Field(..., ge=1, le=10)
    engagement_rating: int = Field(..., ge=1, le=10)
    difficulty_level: str = "medium"  # easy, medium, hard

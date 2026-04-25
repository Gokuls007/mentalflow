from pydantic import BaseModel
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

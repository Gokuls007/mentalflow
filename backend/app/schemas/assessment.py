from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import date, datetime

class AssessmentBase(BaseModel):
    type: str # phq9, gad7
    responses: List[int]
    date: date

class PHQ9Create(AssessmentBase):
    pass

class GAD7Create(AssessmentBase):
    pass

class AssessmentResponse(BaseModel):
    id: int
    user_id: int
    type: str
    score: int
    severity: Optional[str] = None
    date: date
    created_at: datetime

    class Config:
        from_attributes = True

class PHQ9Response(AssessmentResponse):
    pass

class GAD7Response(AssessmentResponse):
    pass

class AssessmentHistoryItem(BaseModel):
    date: date
    score: int
    severity: str

class AssessmentHistoryResponse(BaseModel):
    phq9: List[AssessmentHistoryItem]
    gad7: List[AssessmentHistoryItem]
    phq9_trend: int # Delta between last two
    gad7_trend: int

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.security.auth import get_current_user
from app.ai.adaptive_assessment import AdaptiveAssessmentIRT
from app.models.clinical import Assessment
from app.services.assessment_service import AssessmentService
from pydantic import BaseModel, field_validator
from typing import Dict, Optional, List
from datetime import datetime

router = APIRouter()

class AdaptiveSession(BaseModel):
    responses: Dict[int, int] # item_id -> score (0-3)

    @field_validator("responses")
    @classmethod
    def validate_responses(cls, v: Dict[int, int]) -> Dict[int, int]:
        for item_id, score in v.items():
            if item_id not in AdaptiveAssessmentIRT.PHQ9_PARAMS:
                raise ValueError(f"Unknown PHQ-9 item id {item_id} (expected 1-9)")
            if not 0 <= score <= 3:
                raise ValueError(f"Score for item {item_id} must be between 0 and 3")
        return v

@router.post("/adaptive/next-question")
async def get_next_question(
    session: AdaptiveSession,
    current_user = Depends(get_current_user)
):
    """
    Returns the next most informative PHQ-9 question based on IRT.
    """
    theta = AdaptiveAssessmentIRT.estimate_theta(session.responses)
    next_item_id = AdaptiveAssessmentIRT.get_next_item(session.responses, theta)
    
    if next_item_id is None:
        return {"status": "complete", "theta": theta, "final_score": AdaptiveAssessmentIRT.map_theta_to_score(theta)}
        
    question = AdaptiveAssessmentIRT.PHQ9_PARAMS[next_item_id]
    return {
        "status": "in_progress",
        "item_id": next_item_id,
        "text": question["text"],
        "theta_current": theta
    }

@router.post("/adaptive/submit")
async def submit_adaptive_assessment(
    session: AdaptiveSession,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Finalizes the IRT-based assessment and stores the clinical score.
    """
    theta = AdaptiveAssessmentIRT.estimate_theta(session.responses)
    final_score = AdaptiveAssessmentIRT.map_theta_to_score(theta)
    severity = AssessmentService()._calculate_severity("phq9", final_score)
    today = datetime.utcnow().date()
    
    # One adaptive assessment per user per day (unique constraint): update today's if it exists
    assessment = db.query(Assessment).filter_by(
        user_id=current_user.id, type="phq9_adaptive", date=today
    ).first()
    if assessment is None:
        assessment = Assessment(user_id=current_user.id, type="phq9_adaptive", date=today)
        db.add(assessment)
    assessment.score = final_score
    assessment.responses = {str(k): v for k, v in session.responses.items()}
    assessment.severity = severity
    
    # Update User model with latest clinical state
    current_user.latest_phq9_score = final_score
    current_user.clinical_severity = severity
    
    db.commit()
    
    return {
        "status": "success",
        "score": final_score,
        "theta": theta,
        "severity": severity,
        # Item 9 (self-harm thoughts) answered above "Not at all"
        "crisis_level": 1 if session.responses.get(9, 0) >= 1 else 0
    }

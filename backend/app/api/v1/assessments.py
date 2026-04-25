from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.security.auth import get_current_user
from app.ai.adaptive_assessment import AdaptiveAssessmentIRT
from app.models.clinical import Assessment
from pydantic import BaseModel
from typing import Dict, Optional, List
from datetime import datetime

router = APIRouter()

class AdaptiveSession(BaseModel):
    responses: Dict[int, int] # item_id -> score (0-3)

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
    
    assessment = Assessment(
        user_id=current_user.id,
        type="phq9_adaptive",
        score=final_score,
        responses=session.responses,
        date=datetime.utcnow().date()
    )
    
    # Update User model with latest clinical state
    current_user.latest_phq9_score = final_score
    
    db.add(assessment)
    db.commit()
    
    return {
        "status": "success",
        "score": final_score,
        "theta": theta,
        "severity": assessment.severity
    }

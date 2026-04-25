from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.services.clinical_outcomes import ClinicalOutcomeTracker
from app.security.auth import get_current_user

router = APIRouter()

@router.get("/progress/{user_id}")
async def get_recovery_progress(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get user's real recovery progress (PHQ-9/GAD-7 targets)
    """
    # Safety check: only allow professionals or the user themselves
    if current_user.id != user_id and current_user.role != "professional":
        raise HTTPException(status_code=403, detail="Access denied")
        
    tracker = ClinicalOutcomeTracker(db)
    return tracker.get_recovery_progress(user_id)

@router.get("/progress/me")
async def get_my_recovery_progress(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Shortcut for current user to see their own recovery path.
    """
    tracker = ClinicalOutcomeTracker(db)
    return tracker.get_recovery_progress(current_user.id)

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.schemas.assessment import PHQ9Create, GAD7Create, PHQ9Response, GAD7Response, AssessmentHistoryResponse
from app.services.assessment_service import AssessmentService
from app.security.auth import get_current_user
from app.db.database import get_db

router = APIRouter()
assessment_service = AssessmentService()

@router.post("/phq9", response_model=PHQ9Response, status_code=status.HTTP_201_CREATED)
async def submit_phq9(
    phq9_in: PHQ9Create,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return assessment_service.create_assessment(db, current_user.id, "phq9", phq9_in)

@router.post("/gad7", response_model=GAD7Response, status_code=status.HTTP_201_CREATED)
async def submit_gad7(
    gad7_in: GAD7Create,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return assessment_service.create_assessment(db, current_user.id, "gad7", gad7_in)

@router.get("/history", response_model=AssessmentHistoryResponse)
async def get_history(
    type: str = Query("all"),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # AssessmentService historical method returns a dict matching the schema
    return assessment_service.get_assessment_history(db, current_user.id, assessment_type=type, limit=limit)

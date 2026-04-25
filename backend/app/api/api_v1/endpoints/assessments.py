from fastapi import APIRouter, HTTPException
from typing import Any

router = APIRouter()

@router.get("/history")
async def get_assessment_history() -> Any:
    return []

@router.post("/submit")
async def submit_assessment(type: str, scores: dict) -> Any:
    """
    Submit PHQ-9 or GAD-7.
    Triggers clinical threshold check.
    """
    total_score = sum(scores.values())
    alert = False
    if type == "PHQ9" and total_score >= 15:
        alert = True
        
    return {
        "score": total_score,
        "clinical_alert": alert,
        "recommendation": "Maintain consistency" if not alert else "Consult clinician"
    }

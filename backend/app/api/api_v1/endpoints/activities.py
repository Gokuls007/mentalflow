from fastapi import APIRouter, Depends, HTTPException
from typing import List, Any

router = APIRouter()

@router.get("/prescribe")
async def prescribe_activity() -> Any:
    """
    Entry point for the RL Agent to prescribe an activity.
    In a full impl, this would fetch the user's RL state and choose an arm.
    """
    return {
        "activity_id": "893c8340-9a3b-4682-998a-6612df2929e4",
        "title": "15-minute walk",
        "category": "PHYSICAL",
        "prescribed_difficulty": 1.5,
        "xp_reward": 20
    }

@router.post("/log")
async def log_activity(activity_id: str, mood_after: int) -> Any:
    """
    Log completion and trigger reward calculation for RL.
    """
    return {"status": "success", "reward_calculated": 0.8}

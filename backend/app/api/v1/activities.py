from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.schemas.activity import ActivityCreate, ActivityUpdate, ActivityResponse
from app.services.activity_service import ActivityService
from app.security.auth import get_current_user
from app.db.database import get_db

router = APIRouter()
activity_service = ActivityService()

@router.post("/", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    activity_in: ActivityCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return activity_service.create_activity(db, current_user.id, activity_in)

@router.get("/", response_model=List[ActivityResponse])
async def list_activities(
    type: str = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return activity_service.list_activities(db, current_user.id, activity_type=type, limit=limit, offset=offset)

@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    activity_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    activity = activity_service.get_activity(db, activity_id, current_user.id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity

@router.patch("/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: int,
    activity_update: ActivityUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    activity = activity_service.update_activity(db, activity_id, current_user.id, activity_update)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity

@router.post("/{activity_id}/complete", response_model=ActivityResponse)
async def complete_activity(
    activity_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    activity = activity_service.complete_activity(db, activity_id, current_user.id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity

@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not activity_service.delete_activity(db, activity_id, current_user.id):
        raise HTTPException(status_code=404, detail="Activity not found")

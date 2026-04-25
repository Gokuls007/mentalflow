from fastapi import APIRouter
from app.api.api_v1.endpoints import activities, assessments

api_router = APIRouter()
api_router.include_router(activities.router, prefix="/activities", tags=["activities"])
api_router.include_router(assessments.router, prefix="/assessments", tags=["assessments"])

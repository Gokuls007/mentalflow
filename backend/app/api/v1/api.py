from fastapi import APIRouter
from app.api.v1.users import router as users_router
from app.api.v1.activities import router as activities_router
from app.api.v1.moods import router as moods_router
from app.api.v1.assessments import router as assessments_router
from app.api.v1.rl import router as rl_router
from app.api.v1.chat import router as chat_router
from app.api.v1.gan import router as gan_router

api_router = APIRouter()

api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(activities_router, prefix="/activities", tags=["activities"])
api_router.include_router(moods_router, prefix="/moods", tags=["moods"])
api_router.include_router(assessments_router, prefix="/assessments", tags=["assessments"])
api_router.include_router(rl_router, prefix="/rl", tags=["rl"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_router.include_router(gan_router, prefix="/gan", tags=["gan"])

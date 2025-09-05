from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.users import router as users_router
from app.api.auth import router as auth_router

api = APIRouter(prefix="/v1")
api.include_router(health_router, tags=["health"])
api.include_router(users_router, tags=["users"])
api.include_router(auth_router, tags=["auth"])
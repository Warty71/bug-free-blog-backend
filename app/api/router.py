from fastapi import APIRouter
from app.api.health import router as health_router

api = APIRouter(prefix="/v1")
api.include_router(health_router, tags=["health"])
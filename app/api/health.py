from fastapi import APIRouter, status
from app.schemas.health import Health

router = APIRouter()

@router.get("/health", response_model=Health, status_code=status.HTTP_200_OK)
async def health() -> Health:
    return Health(status="ok")
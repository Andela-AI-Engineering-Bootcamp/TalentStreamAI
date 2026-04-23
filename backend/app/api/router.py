from fastapi import APIRouter

from app.api.v1 import health
from app.api.v1 import endpoints

api_router = APIRouter()
api_router.include_router(health.router, prefix="/v1", tags=["health"])
api_router.include_router(endpoints.router, prefix="/v1", tags=["talentstream"])

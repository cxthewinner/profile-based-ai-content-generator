from fastapi import APIRouter

from app.api.routes.generate import router as generate_router
from app.api.routes.health import router as health_router
from app.api.routes.history import router as history_router


api_router = APIRouter(prefix="/api")
api_router.include_router(health_router, tags=["health"])
api_router.include_router(generate_router, tags=["generate"])
api_router.include_router(history_router, tags=["history"])

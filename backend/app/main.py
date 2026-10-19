from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import api_router
from app.core.config import get_settings
from app.core.database import Base, engine, ensure_history_schema
from app.models import GenerationHistory
from app.services.image_service import GENERATED_DIR, ensure_static_assets


settings = get_settings()
ensure_static_assets()

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Create database tables when the application starts."""
    Base.metadata.create_all(bind=engine)
    ensure_history_schema()
    ensure_static_assets()


app.mount("/static", StaticFiles(directory=GENERATED_DIR.parent), name="static")
app.include_router(api_router)


@app.get("/")
def read_root():
    """Simple root route for quick local checking."""
    return {
        "message": "AI Image-Text Generator backend is running.",
        "docs": "/docs",
    }

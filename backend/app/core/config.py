import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_SQLITE_PATH = BASE_DIR / "app.db"


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    app_name: str = "AI Image-Text Generator based on User Profiling"
    app_version: str = "1.0.0"
    app_description: str = (
        "Backend service for a demo app that generates image-text content "
        "based on user profiling."
    )
    sqlite_path: str = os.getenv("SQLITE_PATH", str(DEFAULT_SQLITE_PATH))

    @property
    def database_url(self) -> str:
        """Build a SQLAlchemy SQLite URL."""
        return f"sqlite:///{self.sqlite_path}"


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()

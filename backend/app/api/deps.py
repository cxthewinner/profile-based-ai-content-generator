from sqlalchemy.orm import Session

from app.core.database import get_db


def get_db_session() -> Session:
    """Yield a database session as a dependency alias."""
    yield from get_db()

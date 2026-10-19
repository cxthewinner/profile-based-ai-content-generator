from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import get_settings


settings = get_settings()

# SQLite needs check_same_thread=False for request-scoped sessions.
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def ensure_history_schema() -> None:
    """Add lightweight schema updates for the existing local SQLite file."""
    with engine.begin() as connection:
        table_info = connection.exec_driver_sql(
            "PRAGMA table_info(generation_history)"
        ).fetchall()
        if not table_info:
            return

        column_names = {row[1] for row in table_info}
        if "input_text" not in column_names:
            connection.exec_driver_sql(
                "ALTER TABLE generation_history ADD COLUMN input_text TEXT"
            )


def get_db():
    """Provide a database session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

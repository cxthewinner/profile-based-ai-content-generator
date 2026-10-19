from sqlalchemy import Column, DateTime, Integer, String, Text, func

from app.core.database import Base


class GenerationHistory(Base):
    """SQLAlchemy model for generated history records."""

    __tablename__ = "generation_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    interests = Column(String(255), nullable=False)
    style = Column(String(100), nullable=False)
    scenario = Column(String(100), nullable=False)
    target_user = Column(String(255), nullable=False)
    input_text = Column(Text, nullable=True)
    profile_summary = Column(Text, nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(String(255), nullable=False)
    image_url = Column(String(500), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

from typing import Optional

from sqlalchemy.orm import Session

from app.models.history import GenerationHistory


def create_history(
    db: Session,
    *,
    interests: str,
    style: str,
    scenario: str,
    target_user: str,
    input_text: str | None,
    profile_summary: str,
    title: str,
    content: str,
    tags: str,
    image_url: str,
) -> GenerationHistory:
    """Create a history record in the database."""
    record = GenerationHistory(
        interests=interests,
        style=style,
        scenario=scenario,
        target_user=target_user,
        input_text=input_text,
        profile_summary=profile_summary,
        title=title,
        content=content,
        tags=tags,
        image_url=image_url,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_history_list(db: Session) -> list[GenerationHistory]:
    """Return all records sorted by create time descending."""
    return (
        db.query(GenerationHistory)
        .order_by(GenerationHistory.created_at.desc())
        .all()
    )


def get_history_by_id(db: Session, record_id: int) -> Optional[GenerationHistory]:
    """Return one record by id."""
    return db.query(GenerationHistory).filter(GenerationHistory.id == record_id).first()


def delete_history(db: Session, record: GenerationHistory) -> None:
    """Delete a record from database."""
    db.delete(record)
    db.commit()

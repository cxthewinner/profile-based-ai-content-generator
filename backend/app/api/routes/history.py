from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.history_crud import delete_history, get_history_by_id, get_history_list
from app.schemas.history import DeleteHistoryResponse, HistoryDetailResponse, HistoryItemResponse
from app.utils.helpers import format_datetime, split_csv


router = APIRouter()


@router.get("/history", response_model=list[HistoryItemResponse])
def read_history_list(db: Session = Depends(get_db)):
    """Return all history records."""
    records = get_history_list(db)
    return [
        HistoryItemResponse(
            id=record.id,
            title=record.title,
            profile_summary=record.profile_summary,
            image_url=record.image_url,
            created_at=format_datetime(record.created_at),
        )
        for record in records
    ]


@router.get("/history/{record_id}", response_model=HistoryDetailResponse)
def read_history_detail(record_id: int, db: Session = Depends(get_db)):
    """Return one history record detail."""
    record = get_history_by_id(db, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="record not found")

    return HistoryDetailResponse(
        id=record.id,
        interests=record.interests,
        style=record.style,
        scenario=record.scenario,
        target_user=record.target_user,
        input_text=record.input_text,
        profile_summary=record.profile_summary,
        title=record.title,
        content=record.content,
        tags=split_csv(record.tags),
        image_url=record.image_url,
        created_at=format_datetime(record.created_at),
    )


@router.delete("/history/{record_id}", response_model=DeleteHistoryResponse)
def remove_history(record_id: int, db: Session = Depends(get_db)):
    """Delete one history record."""
    record = get_history_by_id(db, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="record not found")

    delete_history(db, record)
    return DeleteHistoryResponse(message="Record deleted successfully")

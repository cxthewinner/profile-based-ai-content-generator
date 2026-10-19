from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.history_crud import create_history
from app.schemas.generate import GenerateRequest, GenerateResponse
from app.services.image_service import build_negative_prompt, build_visual_prompt, generate_image
from app.services.profile_service import build_profile_summary
from app.services.text_service import generate_text
from app.utils.helpers import format_datetime


router = APIRouter()


def _log(message: str) -> None:
    """Print concise route-level logs for generation flow."""
    print(f"[generate_route] {message}")


@router.post("/generate", response_model=GenerateResponse, status_code=status.HTTP_201_CREATED)
def generate_content(payload: GenerateRequest, db: Session = Depends(get_db)):
    """Generate content, save it, and return the result."""
    if not payload.interests:
        raise HTTPException(status_code=400, detail="interests cannot be empty")

    _log("Generation started")
    profile_summary = build_profile_summary(payload)
    text_result = generate_text(profile_summary, payload=payload)
    title = text_result["title"]
    content = text_result["content"]
    tags = text_result["tags"]
    image_prompt = build_visual_prompt(
        payload=payload,
        profile_summary=profile_summary,
        title=title,
        content=content,
    )
    negative_prompt = build_negative_prompt(
        payload=payload,
        profile_summary=profile_summary,
        title=title,
        content=content,
    )
    image_url = generate_image(image_prompt, negative_prompt=negative_prompt)

    record = create_history(
        db,
        interests=",".join(payload.interests),
        style=payload.style,
        scenario=payload.scenario,
        target_user=payload.target_user,
        input_text=payload.input_text.strip() if payload.input_text else None,
        profile_summary=profile_summary,
        title=title,
        content=content,
        tags=",".join(tags),
        image_url=image_url,
    )
    _log("History record saved successfully")

    return GenerateResponse(
        id=record.id,
        profile_summary=record.profile_summary,
        title=record.title,
        content=record.content,
        tags=tags,
        image_url=record.image_url,
        created_at=format_datetime(record.created_at),
    )

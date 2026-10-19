from typing import List

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    interests: List[str] = Field(..., min_length=1)
    style: str = Field(..., min_length=1, max_length=100)
    scenario: str = Field(..., min_length=1, max_length=100)
    target_user: str = Field(..., min_length=1, max_length=255)
    input_text: str | None = Field(default=None, max_length=2000)


class GenerateResponse(BaseModel):
    id: int
    profile_summary: str
    title: str
    content: str
    tags: List[str]
    image_url: str
    created_at: str

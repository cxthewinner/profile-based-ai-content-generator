from pydantic import BaseModel


class HistoryItemResponse(BaseModel):
    id: int
    title: str
    profile_summary: str
    image_url: str
    created_at: str

    class Config:
        from_attributes = True


class HistoryDetailResponse(BaseModel):
    id: int
    interests: str
    style: str
    scenario: str
    target_user: str
    input_text: str | None
    profile_summary: str
    title: str
    content: str
    tags: list[str]
    image_url: str
    created_at: str


class DeleteHistoryResponse(BaseModel):
    message: str

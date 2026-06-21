from datetime import datetime

from pydantic import BaseModel


class PostCreate(BaseModel):
    account_id: str
    platform: str  # facebook | tiktok
    content_type: str  # text | image | video | mixed
    caption: str | None = None
    hashtags: list[str] | None = None
    media_urls: list[str] | None = None
    scheduled_at: datetime | None = None


class PostResponse(BaseModel):
    id: str
    account_id: str
    platform: str
    content_type: str
    caption: str | None
    hashtags: list[str] | None
    media_urls: list[str] | None
    status: str
    scheduled_at: datetime | None
    published_at: datetime | None
    error_message: str | None
    retry_count: int
    created_at: datetime

    model_config = {"from_attributes": True}

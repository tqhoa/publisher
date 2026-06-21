import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.models.user import Base


class PostModel(Base):
    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id: Mapped[str] = mapped_column(String, ForeignKey("accounts.id"), index=True)
    platform: Mapped[str] = mapped_column(String(20))  # facebook | tiktok
    content_type: Mapped[str] = mapped_column(String(20))  # text | image | video | mixed
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    hashtags: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # type: ignore[type-arg]
    media_urls: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # type: ignore[type-arg]
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    # pending | queued | publishing | published | failed | cancelled
    scheduled_at: Mapped[datetime | None] = mapped_column(nullable=True, index=True)
    published_at: Mapped[datetime | None] = mapped_column(nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    created_by: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.models.user import Base


class AccountModel(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    platform: Mapped[str] = mapped_column(String(20))  # facebook | tiktok
    username: Mapped[str] = mapped_column(String(255), index=True)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active | inactive | banned
    cookie_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    cookie_updated_at: Mapped[datetime | None] = mapped_column(nullable=True)
    last_health_check_at: Mapped[datetime | None] = mapped_column(nullable=True)
    health_status: Mapped[str | None] = mapped_column(String(20), nullable=True)  # healthy | unhealthy
    created_by: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

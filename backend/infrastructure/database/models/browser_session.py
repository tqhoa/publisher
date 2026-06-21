import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.models.user import Base


class BrowserSessionModel(Base):
    __tablename__ = "browser_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id: Mapped[str] = mapped_column(String, ForeignKey("accounts.id"), unique=True, index=True)
    node_id: Mapped[str] = mapped_column(String(100), default="local")
    status: Mapped[str] = mapped_column(String(20), default="starting")
    # idle | busy | crashed | starting
    started_at: Mapped[datetime] = mapped_column(server_default=func.now())
    last_activity_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

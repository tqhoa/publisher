from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.async_api import Browser, BrowserContext, Page


@dataclass
class BrowserSession:
    account_id: str
    browser: "Browser"
    context: "BrowserContext"
    page: "Page"
    status: str = "idle"  # idle | busy | crashed
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def touch(self) -> None:
        self.last_activity_at = datetime.now(timezone.utc)

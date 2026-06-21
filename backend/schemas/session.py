from datetime import datetime

from pydantic import BaseModel


class BrowserSessionResponse(BaseModel):
    id: str
    account_id: str
    node_id: str
    status: str
    started_at: datetime
    last_activity_at: datetime

    model_config = {"from_attributes": True}

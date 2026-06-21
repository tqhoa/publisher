from datetime import datetime

from pydantic import BaseModel


class AccountCreate(BaseModel):
    platform: str  # facebook | tiktok
    username: str


class AccountUpdate(BaseModel):
    username: str | None = None
    status: str | None = None  # active | inactive | banned


class AccountResponse(BaseModel):
    id: str
    platform: str
    username: str
    status: str
    health_status: str | None
    cookie_updated_at: datetime | None
    last_health_check_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CookieImportRequest(BaseModel):
    cookie_json: str  # raw JSON string of cookie array


class HealthCheckResponse(BaseModel):
    account_id: str
    healthy: bool
    checked_at: datetime
    message: str | None = None

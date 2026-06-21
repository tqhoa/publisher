import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from domain.services.account_service import AccountService
from infrastructure.database.models.account import AccountModel
from schemas.account import AccountCreate, AccountUpdate, CookieImportRequest
from shared.exceptions import AppError


def _mock_account(**kwargs) -> MagicMock:
    acc = MagicMock(spec=AccountModel)
    acc.id = kwargs.get("id", "acc-1")
    acc.platform = kwargs.get("platform", "facebook")
    acc.username = kwargs.get("username", "user1")
    acc.status = kwargs.get("status", "active")
    acc.health_status = kwargs.get("health_status", None)
    acc.cookie_encrypted = kwargs.get("cookie_encrypted", None)
    acc.cookie_updated_at = kwargs.get("cookie_updated_at", None)
    acc.last_health_check_at = kwargs.get("last_health_check_at", None)
    acc.created_at = kwargs.get("created_at", datetime.now(timezone.utc))
    return acc


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def service(mock_db):
    svc = AccountService(mock_db)
    svc._repo = AsyncMock()
    return svc


@pytest.mark.asyncio
async def test_get_not_found_raises_404(service):
    service._repo.find_by_id.return_value = None
    with pytest.raises(AppError) as exc:
        await service.get("nonexistent")
    assert exc.value.status_code == 404
    assert exc.value.code == "ACCOUNT_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_deleted_raises_404(service):
    acc = _mock_account(status="deleted")
    service._repo.find_by_id.return_value = acc
    with pytest.raises(AppError) as exc:
        await service.get("acc-1")
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_create_returns_account_response(service):
    acc = _mock_account()
    service._repo.create.return_value = acc
    result = await service.create(AccountCreate(platform="facebook", username="u1"), "user-1")
    assert result.id == "acc-1"


@pytest.mark.asyncio
async def test_delete_soft_sets_inactive(service):
    acc = _mock_account()
    service._repo.find_by_id.return_value = acc
    service._repo.update.return_value = _mock_account(status="inactive")
    await service.delete("acc-1")
    service._repo.update.assert_called_once()
    call_kwargs = service._repo.update.call_args[1]
    assert call_kwargs.get("status") == "inactive"


@pytest.mark.asyncio
async def test_import_cookie_encrypts_value(service):
    acc = _mock_account()
    updated = _mock_account(cookie_encrypted="encrypted_value")
    service._repo.find_by_id.return_value = acc
    service._repo.update.return_value = updated

    result = await service.import_cookie("acc-1", CookieImportRequest(cookie_json='[{"name":"x"}]'))
    # Raw cookie JSON must NOT appear in result
    assert '{"name":"x"}' not in str(result)


@pytest.mark.asyncio
async def test_health_check_no_cookie_returns_unhealthy(service):
    acc = _mock_account(cookie_encrypted=None)
    service._repo.find_by_id.return_value = acc
    result = await service.check_health("acc-1")
    assert result.healthy is False


@pytest.mark.asyncio
async def test_health_check_with_cookie_returns_healthy(service):
    acc = _mock_account(cookie_encrypted="some_encrypted_value")
    service._repo.find_by_id.return_value = acc
    service._repo.update.return_value = acc
    result = await service.check_health("acc-1")
    assert result.healthy is True

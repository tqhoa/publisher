import pytest
from unittest.mock import AsyncMock, MagicMock

from domain.services.auth_service import AuthService
from infrastructure.database.models.user import UserModel
from schemas.auth import LoginRequest
from shared.exceptions import AppError
from shared.helpers.hash import hash_password


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def mock_user() -> MagicMock:
    user = MagicMock(spec=UserModel)
    user.id = "user-123"
    user.email = "test@test.com"
    user.password_hash = hash_password("correct-password")
    user.role = "operator"
    return user


@pytest.mark.asyncio
async def test_login_valid_credentials_returns_tokens(mock_db, mock_user: MagicMock):
    service = AuthService(mock_db)
    service._repo = AsyncMock()
    service._repo.find_by_email.return_value = mock_user

    result = await service.login(LoginRequest(email="test@test.com", password="correct-password"))

    assert result.access_token
    assert result.refresh_token
    assert result.role == "operator"


@pytest.mark.asyncio
async def test_login_wrong_password_raises_401(mock_db, mock_user: MagicMock):
    service = AuthService(mock_db)
    service._repo = AsyncMock()
    service._repo.find_by_email.return_value = mock_user

    with pytest.raises(AppError) as exc:
        await service.login(LoginRequest(email="test@test.com", password="wrong"))

    assert exc.value.status_code == 401
    assert exc.value.code == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_login_unknown_user_raises_401(mock_db):
    service = AuthService(mock_db)
    service._repo = AsyncMock()
    service._repo.find_by_email.return_value = None

    with pytest.raises(AppError) as exc:
        await service.login(LoginRequest(email="nobody@x.com", password="any"))

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_refresh_invalid_token_raises_401(mock_db):
    service = AuthService(mock_db)

    with pytest.raises(AppError) as exc:
        await service.refresh("not-a-valid-token")

    assert exc.value.status_code == 401

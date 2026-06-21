"""Unit tests for AuditMiddleware helpers."""
import pytest
from api.middleware.audit import _parse_resource, _extract_user_id, _MUTATING_METHODS


def test_parse_resource_accounts_with_id():
    resource_type, resource_id = _parse_resource("/api/v1/accounts/abc-123")
    assert resource_type == "accounts"
    assert resource_id == "abc-123"


def test_parse_resource_accounts_list():
    resource_type, resource_id = _parse_resource("/api/v1/accounts")
    assert resource_type == "accounts"
    assert resource_id is None


def test_parse_resource_nested_action():
    resource_type, resource_id = _parse_resource("/api/v1/accounts/xyz/cookie")
    assert resource_type == "accounts"
    assert resource_id == "xyz"


def test_parse_resource_health():
    resource_type, resource_id = _parse_resource("/health")
    assert resource_type is None
    assert resource_id is None


def test_parse_resource_posts():
    resource_type, resource_id = _parse_resource("/api/v1/posts/post-999")
    assert resource_type == "posts"
    assert resource_id == "post-999"


def test_mutating_methods_set():
    assert "POST" in _MUTATING_METHODS
    assert "PATCH" in _MUTATING_METHODS
    assert "DELETE" in _MUTATING_METHODS
    assert "GET" not in _MUTATING_METHODS


def test_extract_user_id_no_header():
    from starlette.testclient import TestClient
    from starlette.requests import Request
    scope = {"type": "http", "headers": []}
    request = Request(scope)
    result = _extract_user_id(request)
    assert result is None


def test_extract_user_id_invalid_token():
    from starlette.requests import Request
    scope = {
        "type": "http",
        "headers": [(b"authorization", b"Bearer totally.invalid.token")],
    }
    request = Request(scope)
    result = _extract_user_id(request)
    assert result is None


def test_extract_user_id_valid_token():
    from starlette.requests import Request
    from shared.helpers.jwt import create_access_token
    token = create_access_token("user-abc", "admin")
    scope = {
        "type": "http",
        "headers": [(b"authorization", f"Bearer {token}".encode())],
    }
    request = Request(scope)
    result = _extract_user_id(request)
    assert result == "user-abc"

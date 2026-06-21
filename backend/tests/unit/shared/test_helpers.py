"""Unit tests for shared helpers — jwt, hash, exceptions."""
import pytest
import time

from shared.helpers.hash import hash_password, verify_password
from shared.helpers.jwt import create_access_token, create_refresh_token, decode_token
from shared.exceptions import AppError
from shared.utils.pagination import PaginationParams, PaginatedResult


# ──────────────────── Hash ────────────────────

def test_hash_password_returns_bcrypt_string():
    h = hash_password("mypassword")
    assert h.startswith("$2b$")


def test_verify_password_correct():
    h = hash_password("secret123")
    assert verify_password("secret123", h) is True


def test_verify_password_wrong():
    h = hash_password("secret123")
    assert verify_password("wrongpass", h) is False


# ──────────────────── JWT ────────────────────

def test_create_access_token_is_decodable():
    token = create_access_token("user-1", "admin")
    payload = decode_token(token, expected_type="access")
    assert payload["sub"] == "user-1"
    assert payload["role"] == "admin"
    assert payload["type"] == "access"


def test_create_refresh_token_is_decodable():
    token = create_refresh_token("user-1")
    payload = decode_token(token, expected_type="refresh")
    assert payload["sub"] == "user-1"
    assert payload["type"] == "refresh"


def test_decode_token_wrong_type_raises():
    access = create_access_token("user-1", "admin")
    with pytest.raises(AppError) as exc:
        decode_token(access, expected_type="refresh")
    assert exc.value.status_code == 401


def test_decode_invalid_token_raises():
    with pytest.raises(AppError) as exc:
        decode_token("not.a.valid.token")
    assert exc.value.status_code == 401


# ──────────────────── AppError ────────────────────

def test_app_error_defaults():
    err = AppError("Something failed")
    assert err.status_code == 500
    assert err.code == "INTERNAL_ERROR"
    assert str(err) == "Something failed"


def test_app_error_custom():
    err = AppError("Not found", 404, "NOT_FOUND")
    assert err.status_code == 404
    assert err.code == "NOT_FOUND"


# ──────────────────── Pagination ────────────────────

def test_pagination_params_offset():
    p = PaginationParams(page=3, limit=20)
    assert p.offset == 40


def test_pagination_params_first_page():
    p = PaginationParams(page=1, limit=10)
    assert p.offset == 0


def test_paginated_result_total_pages():
    result = PaginatedResult(items=[], total=95, page=1, limit=20)
    assert result.total_pages == 5


def test_paginated_result_exact_division():
    result = PaginatedResult(items=[], total=100, page=1, limit=20)
    assert result.total_pages == 5


def test_paginated_result_single_page():
    result = PaginatedResult(items=[], total=5, page=1, limit=20)
    assert result.total_pages == 1

"""Unit tests for SecurityHeadersMiddleware."""
import pytest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from api.middleware.security import SecurityHeadersMiddleware


def homepage(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


app = Starlette(routes=[Route("/", homepage)])
app.add_middleware(SecurityHeadersMiddleware)
client = TestClient(app)


def test_x_content_type_options_header():
    response = client.get("/")
    assert response.headers.get("x-content-type-options") == "nosniff"


def test_x_frame_options_deny():
    response = client.get("/")
    assert response.headers.get("x-frame-options") == "DENY"


def test_xss_protection_header():
    response = client.get("/")
    assert response.headers.get("x-xss-protection") == "1; mode=block"


def test_referrer_policy_header():
    response = client.get("/")
    assert "referrer-policy" in response.headers


def test_csp_header_present():
    response = client.get("/")
    csp = response.headers.get("content-security-policy", "")
    assert "default-src" in csp


def test_permissions_policy_header():
    response = client.get("/")
    assert "permissions-policy" in response.headers

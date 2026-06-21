import asyncio

import structlog
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from infrastructure.database.session import AsyncSessionLocal
from domain.repositories.audit_log_repository import AuditLogRepository
from shared.config import settings

logger = structlog.get_logger()

_MUTATING_METHODS = {"POST", "PATCH", "PUT", "DELETE"}
_SKIP_PATHS = {"/metrics", "/health", "/docs", "/redoc", "/openapi.json"}


def _extract_user_id(request: Request) -> str | None:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[7:]
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if payload.get("type") == "access":
            return str(payload.get("sub"))
    except JWTError:
        pass
    return None


async def _write_audit_log(
    *,
    action: str,
    user_id: str | None,
    resource_type: str | None,
    resource_id: str | None,
    ip_address: str | None,
) -> None:
    try:
        async with AsyncSessionLocal() as session:
            repo = AuditLogRepository(session)
            await repo.create(
                action=action,
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                ip_address=ip_address,
            )
            await session.commit()
    except Exception:
        logger.warning("audit_log_write_failed", action=action)


def _parse_resource(path: str) -> tuple[str | None, str | None]:
    """Extract resource_type and resource_id from path like /api/v1/accounts/uuid."""
    parts = [p for p in path.split("/") if p]
    # Find the versioned API prefix index
    try:
        v_idx = next(i for i, p in enumerate(parts) if p.startswith("v"))
    except StopIteration:
        return None, None
    rest = parts[v_idx + 1 :]
    if not rest:
        return None, None
    resource_type = rest[0]
    resource_id = rest[1] if len(rest) > 1 else None
    return resource_type, resource_id


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        if request.method not in _MUTATING_METHODS or request.url.path in _SKIP_PATHS:
            return await call_next(request)

        response = await call_next(request)

        if response.status_code < 400:
            user_id = _extract_user_id(request)
            resource_type, resource_id = _parse_resource(request.url.path)
            action = f"{request.method.lower()}:{resource_type or request.url.path}"
            ip = request.client.host if request.client else None

            asyncio.ensure_future(
                _write_audit_log(
                    action=action,
                    user_id=user_id,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    ip_address=ip,
                )
            )

        return response

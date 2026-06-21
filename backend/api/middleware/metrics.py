import time

from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "route", "status_code"],
)
REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "route"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        start = time.monotonic()
        response = await call_next(request)
        duration = time.monotonic() - start

        route = request.scope.get("route")
        path = route.path if route else request.url.path

        REQUEST_COUNT.labels(
            method=request.method,
            route=path,
            status_code=str(response.status_code),
        ).inc()
        REQUEST_DURATION.labels(method=request.method, route=path).observe(duration)
        return response

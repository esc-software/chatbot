import json
import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from ..config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._request_log: dict[str, list[float]] = defaultdict(list)
        self._last_cleanup = time.time()

    def _cleanup(self) -> None:
        now = time.time()
        if now - self._last_cleanup < 300:
            return
        self._last_cleanup = now
        cutoff = now - 60
        expired = [ip for ip, times in self._request_log.items() if times and times[-1] < cutoff]
        for ip in expired:
            del self._request_log[ip]

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        self._request_log[ip] = [t for t in self._request_log[ip] if now - t < 60]
        self._cleanup()

        if len(self._request_log[ip]) >= settings.max_requests_per_min:
            body = json.dumps({"detail": "rate limit"}).encode()
            return Response(
                content=body,
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": "60"},
            )

        self._request_log[ip].append(now)
        return await call_next(request)

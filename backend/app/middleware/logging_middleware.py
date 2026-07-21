"""
Request/response logging middleware.
Logs method, path, status code, and duration for every request.
"""

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "%s %s → %s  (%.1f ms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        # Expose timing header in responses
        response.headers["X-Process-Time"] = f"{duration_ms:.1f}ms"
        return response

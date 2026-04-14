"""
Performance monitoring middleware.
Adds response time headers and tracks slow endpoints.
"""

import logging
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# Threshold for logging slow requests (seconds)
SLOW_REQUEST_THRESHOLD = 2.0


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds X-Response-Time header and logs slow requests.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()

        response = await call_next(request)

        duration = time.perf_counter() - start_time
        duration_ms = round(duration * 1000, 2)

        # Add response time header
        response.headers["X-Response-Time"] = f"{duration_ms}ms"

        # Log slow requests
        if duration > SLOW_REQUEST_THRESHOLD:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {duration_ms:.0f}ms"
            )

        return response
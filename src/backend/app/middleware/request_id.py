"""
Request ID middleware for request tracing and observability.
Adds X-Request-ID header to all responses for debugging.
"""

import logging
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that assigns a unique request ID to each request.
    Uses X-Request-ID header if provided by the client, otherwise generates a UUID.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Use existing request ID or generate a new one
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Add to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response
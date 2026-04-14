"""
ETag middleware for HTTP conditional requests.
Enables 304 Not Modified responses for cacheable endpoints,
reducing bandwidth and server processing.
"""

import hashlib
import json
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# Endpoints that support ETag caching
ETAG_ENABLED_PREFIXES = (
    "/analytics/",
    "/health",
    "/trends/",
    "/competitors/",
    "/freshness/",
    "/dashboard",
)


class ETagMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds ETag headers to GET responses for cacheable endpoints.
    If the client sends If-None-Match with a matching ETag, returns 304 Not Modified.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Only process GET requests on ETag-enabled endpoints
        if request.method != "GET":
            return await call_next(request)

        path = request.url.path
        is_etag_enabled = any(path.startswith(prefix) for prefix in ETAG_ENABLED_PREFIXES)

        if not is_etag_enabled:
            return await call_next(request)

        response = await call_next(request)

        # Only add ETag to successful responses
        if response.status_code == 200:
            # Generate ETag from response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            etag = '"' + hashlib.md5(body).hexdigest() + '"'
            response.headers["ETag"] = etag

            # Check If-None-Match header
            if_none_match = request.headers.get("If-None-Match")
            if if_none_match and if_none_match == etag:
                return Response(
                    status_code=304,
                    headers={
                        "ETag": etag,
                        "Cache-Control": response.headers.get(
                            "Cache-Control", "max-age=60"
                        ),
                    },
                )

            # Reconstruct response with collected body
            from starlette.responses import Response as StarletteResponse

            return StarletteResponse(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        return response
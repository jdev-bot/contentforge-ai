"""
Per-request context for caching authenticated user info.

Avoids redundant supabase.auth.get_user() calls across middleware
and route handlers within the same request.

PERFORMANCE: Includes an in-memory auth cache with 5-minute TTL.
This eliminates the ~400ms supabase.auth.get_user() network call
on every request. The cache is keyed by JWT jti (or sub+iat) and
revalidated against Supabase when the TTL expires.

Security note: JWT expiry is checked locally. If a token is revoked
on the Supabase side, the cache will still accept it until TTL expires.
This is acceptable for staging; for production, reduce TTL or add
a revocation check.
"""

import base64
import json
import logging
import threading
import time
from typing import Any, Dict, Optional, Tuple

from starlette.requests import Request

logger = logging.getLogger(__name__)

# ── Per-request state keys ────────────────────────────────────────────────────

_STATE_KEY = "_request_user_id"
_USER_OBJ_KEY = "_request_user_obj"


def set_request_user_id(request: Request, user_id: str) -> None:
    """Store the authenticated user ID on the request state."""
    request.state._request_user_id = user_id


def get_request_user_id(request: Request) -> str | None:
    """Retrieve the cached user ID, or None if not set."""
    return getattr(request.state, "_request_user_id", None)


def set_request_user(request: Request, user) -> None:
    """Store the full Supabase user object on request state."""
    request.state._request_user_obj = user


def get_request_user(request: Request):
    """Retrieve the cached Supabase user object, or None if not set."""
    return getattr(request.state, "_request_user_obj", None)


# ── JWT decode utilities ──────────────────────────────────────────────────────

def _decode_jwt_payload(token: str) -> Optional[Dict[str, Any]]:
    """Decode JWT payload without signature verification."""
    try:
        payload = token.split(".")[1]
        if not payload:
            return None
        padded = payload + "=" * (4 - len(payload) % 4)
        decoded = base64.urlsafe_b64decode(padded)
        return json.loads(decoded)
    except Exception:
        return None


def decode_jwt_subject(token: str) -> str | None:
    """
    Decode a JWT's 'sub' claim without a library.

    Supabase JWTs contain the user ID in the 'sub' field.
    This avoids a network call to Supabase for user validation
    in middleware that only needs the user ID (e.g., error tracking, rate limit headers).
    The full auth validation still happens in the route handler via get_auth_user().

    Returns the user ID string, or None if the JWT can't be decoded.
    """
    data = _decode_jwt_payload(token)
    return data.get("sub") if data else None


def is_jwt_expired(token: str) -> bool:
    """Check if a JWT's exp claim has passed."""
    data = _decode_jwt_payload(token)
    if not data:
        return True
    exp = data.get("exp")
    if exp is None:
        return True
    return time.time() > exp


def get_jwt_cache_key(token: str) -> Optional[str]:
    """Get a cache key from JWT claims (sub + iat uniquely identifies a token)."""
    data = _decode_jwt_payload(token)
    if not data:
        return None
    sub = data.get("sub")
    iat = data.get("iat")
    if sub and iat:
        return f"{sub}:{iat}"
    return None


# ── In-memory auth cache ──────────────────────────────────────────────────────
# Caches the Supabase user object per unique JWT, avoiding ~400ms
# supabase.auth.get_user() network call on every request.
# TTL of 5 minutes means we revalidate periodically.

_AUTH_CACHE: Dict[str, Tuple[float, Any]] = {}
_AUTH_CACHE_LOCK = threading.Lock()
AUTH_CACHE_TTL = 300  # 5 minutes


def get_cached_auth_user(token: str) -> Optional[Any]:
    """Return cached user object if JWT is still valid and cache is fresh."""
    key = get_jwt_cache_key(token)
    if not key:
        return None

    # Check JWT expiry first
    if is_jwt_expired(token):
        return None

    with _AUTH_CACHE_LOCK:
        entry = _AUTH_CACHE.get(key)
        if entry and (time.time() - entry[0]) < AUTH_CACHE_TTL:
            return entry[1]
    return None


def set_cached_auth_user(token: str, user: Any) -> None:
    """Cache a validated user object for this JWT."""
    key = get_jwt_cache_key(token)
    if not key:
        return

    with _AUTH_CACHE_LOCK:
        _AUTH_CACHE[key] = (time.time(), user)

    # Periodic cleanup: prune expired entries when cache grows
    if len(_AUTH_CACHE) > 1000:
        _cleanup_auth_cache()


def _cleanup_auth_cache() -> None:
    """Remove expired entries from the auth cache."""
    now = time.time()
    with _AUTH_CACHE_LOCK:
        expired = [k for k, (ts, _) in _AUTH_CACHE.items()
                   if now - ts >= AUTH_CACHE_TTL]
        for k in expired:
            del _AUTH_CACHE[k]
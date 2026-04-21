"""
Per-request context for caching authenticated user info.

Avoids redundant supabase.auth.get_user() calls across middleware
and route handlers within the same request.

Usage in middleware:
    from app.core.request_context import set_request_user_id, get_request_user_id
    set_request_user_id(request, user_id)

Usage in route handler:
    from app.core.request_context import get_request_user_id
    user_id = get_request_user_id(request)  # Returns None if not set
"""

from starlette.requests import Request

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


def decode_jwt_subject(token: str) -> str | None:
    """
    Decode a JWT's 'sub' claim without a library.

    Supabase JWTs contain the user ID in the 'sub' field.
    This avoids a network call to Supabase for user validation
    in middleware that only needs the user ID (e.g., error tracking, rate limit headers).
    The full auth validation still happens in the route handler via get_auth_user().

    Returns the user ID string, or None if the JWT can't be decoded.
    """
    try:
        payload = token.split(".")[1]
        if not payload:
            return None
        # Base64url decode
        import base64

        padded = payload + "=" * (4 - len(payload) % 4)
        decoded = base64.urlsafe_b64decode(padded)
        import json

        data = json.loads(decoded)
        return data.get("sub")
    except Exception:
        return None
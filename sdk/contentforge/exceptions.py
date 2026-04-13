"""
ContentForge AI Python SDK — Custom Exceptions
"""


class ContentForgeError(Exception):
    """Base exception for all ContentForge SDK errors."""

    def __init__(self, message: str = "", status_code: int = 0):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(ContentForgeError):
    """Raised when authentication fails (401)."""

    def __init__(self, message: str = "Authentication failed. Check your API key."):
        super().__init__(message, status_code=401)


class NotFoundError(ContentForgeError):
    """Raised when a resource is not found (404)."""

    def __init__(self, message: str = "Resource not found."):
        super().__init__(message, status_code=404)


class ValidationError(ContentForgeError):
    """Raised when request validation fails (422)."""

    def __init__(self, message: str = "Validation error. Check your request data."):
        super().__init__(message, status_code=422)


class RateLimitError(ContentForgeError):
    """Raised when rate limit is exceeded (429)."""

    def __init__(self, message: str = "Rate limit exceeded. Please retry later."):
        super().__init__(message, status_code=429)


class ServerError(ContentForgeError):
    """Raised when the server encounters an error (5xx)."""

    def __init__(self, message: str = "Server error. Please try again later."):
        super().__init__(message, status_code=500)


class ConnectionError(ContentForgeError):
    """Raised when unable to connect to the API."""

    def __init__(self, message: str = "Unable to connect to the ContentForge API."):
        super().__init__(message, status_code=0)
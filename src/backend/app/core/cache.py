"""
Redis caching layer for ContentForge AI.
Provides caching for frequently accessed data to reduce database load.
"""

import hashlib
import json
import logging
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional, TypeVar


class _CacheValue:
    """Wrapper to make any value JSON-serializable for cache storage."""

    def __init__(self, value: Any):
        self.value = value

    def to_dict(self) -> dict:
        """Serialize to a dict that JSON can handle."""
        return {"__cache_value__": True, "data": self.value}

    @classmethod
    def from_dict(cls, d: dict) -> Any:
        """Deserialize from dict."""
        if isinstance(d, dict) and d.get("__cache_value__"):
            return d["data"]
        return d


from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Try to import redis, handle gracefully if not available
try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

T = TypeVar("T")


class CacheManager:
    """
    Cache manager with Redis backend.
    Falls back to in-memory dict if Redis is unavailable.
    """

    def __init__(self):
        self._local_cache: dict = {}
        self._redis: Optional[Any] = None
        self._default_ttl = 300  # 5 minutes default

        if REDIS_AVAILABLE and settings.REDIS_URL:
            try:
                self._redis = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=False,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                )
                # Test connection
                self._redis.ping()
                logger.info("Redis cache connected")
            except Exception as e:
                logger.warning(f"Redis connection failed, using in-memory cache: {e}")
                self._redis = None

    def _make_key(self, key: str, prefix: str = "") -> str:
        """Create a prefixed key."""
        if prefix:
            return f"{prefix}:{key}"
        return key

    def _serialize(self, value: Any) -> bytes:
        """Serialize value to bytes using JSON (pickle removed for security)."""
        try:
            return json.dumps(value, default=str).encode("utf-8")
        except (TypeError, ValueError):
            # Fallback: convert non-serializable types to strings
            if isinstance(value, dict):
                safe = {
                    k: (
                        str(v)
                        if not isinstance(
                            v, (str, int, float, bool, list, dict, type(None))
                        )
                        else v
                    )
                    for k, v in value.items()
                }
                return json.dumps(safe, default=str).encode("utf-8")
            return json.dumps(str(value)).encode("utf-8")

    def _deserialize(self, value: bytes) -> Any:
        """Deserialize bytes to value using JSON (pickle removed for security)."""
        try:
            return json.loads(value.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"Cache deserialize error: {e}")
            return None

    def get(self, key: str, prefix: str = "") -> Optional[Any]:
        """Get value from cache."""
        full_key = self._make_key(key, prefix)

        try:
            if self._redis:
                value = self._redis.get(full_key)
                if value:
                    return self._deserialize(value)
            else:
                entry = self._local_cache.get(full_key)
                if entry:
                    if entry["expires"] > datetime.now().timestamp():
                        return entry["value"]
                    else:
                        del self._local_cache[full_key]
        except Exception as e:
            logger.error(f"Cache get error: {e}")

        return None

    def set(
        self, key: str, value: Any, ttl: Optional[int] = None, prefix: str = ""
    ) -> bool:
        """Set value in cache with TTL."""
        full_key = self._make_key(key, prefix)
        ttl = ttl or self._default_ttl

        try:
            if self._redis:
                serialized = self._serialize(value)
                self._redis.setex(full_key, ttl, serialized)
                return True
            else:
                self._local_cache[full_key] = {
                    "value": value,
                    "expires": datetime.now().timestamp() + ttl,
                }
                return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def delete(self, key: str, prefix: str = "") -> bool:
        """Delete value from cache."""
        full_key = self._make_key(key, prefix)

        try:
            if self._redis:
                self._redis.delete(full_key)
            else:
                self._local_cache.pop(full_key, None)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    def delete_pattern(self, pattern: str, prefix: str = "") -> int:
        """Delete all keys matching pattern."""
        full_pattern = self._make_key(pattern, prefix)
        count = 0

        try:
            if self._redis:
                for key in self._redis.scan_iter(match=f"{full_pattern}*"):
                    self._redis.delete(key)
                    count += 1
            else:
                keys_to_delete = [
                    k for k in self._local_cache.keys() if k.startswith(full_pattern)
                ]
                for k in keys_to_delete:
                    del self._local_cache[k]
                    count += 1
        except Exception as e:
            logger.error(f"Cache delete_pattern error: {e}")

        return count

    def invalidate_user(self, user_id: str) -> int:
        """Invalidate all cache entries for a user."""
        return self.delete_pattern("", prefix=f"user:{user_id}")

    def get_or_set(
        self,
        key: str,
        getter: Callable[[], T],
        ttl: Optional[int] = None,
        prefix: str = "",
    ) -> T:
        """Get from cache or compute and store."""
        cached = self.get(key, prefix=prefix)
        if cached is not None:
            return cached

        value = getter()
        self.set(key, value, ttl=ttl, prefix=prefix)
        return value


# Global cache instance
cache = CacheManager()


def cached(
    ttl: Optional[int] = None, prefix: str = "", key_func: Optional[Callable] = None
):
    """
    Decorator to cache function results.

    Args:
        ttl: Time to live in seconds
        prefix: Cache key prefix
        key_func: Optional function to generate cache key from args
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default: use function name + args hash
                key_parts = [func.__name__]
                for arg in args:
                    if hasattr(arg, "id"):  # Likely a user object
                        key_parts.append(str(arg.id))
                    elif isinstance(arg, (str, int, float, bool)):
                        key_parts.append(str(arg))
                for k, v in sorted(kwargs.items()):
                    key_parts.append(f"{k}:{v}")
                cache_key = hashlib.sha256(":".join(key_parts).encode()).hexdigest()

            # Check cache
            result = cache.get(cache_key, prefix=prefix)
            if result is not None:
                return result

            # Compute and cache
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl, prefix=prefix)
            return result

        return wrapper

    return decorator


def invalidate_cache(pattern: str, prefix: str = ""):
    """Invalidate cache entries matching pattern."""
    return cache.delete_pattern(pattern, prefix=prefix)


# Cache TTL constants
CACHE_TTL = {
    "user_profile": 300,  # 5 minutes
    "project_list": 60,  # 1 minute
    "content_list": 60,  # 1 minute
    "content_detail": 120,  # 2 minutes
    "analytics": 300,  # 5 minutes
    "usage_stats": 60,  # 1 minute
    "search_results": 60,  # 1 minute
}


def cache_user_profile(
    user_id: str, profile: dict, ttl: int = CACHE_TTL["user_profile"]
):
    """Cache user profile data."""
    return cache.set(f"profile", profile, ttl=ttl, prefix=f"user:{user_id}")


def get_cached_user_profile(user_id: str) -> Optional[dict]:
    """Get cached user profile."""
    return cache.get("profile", prefix=f"user:{user_id}")


def cache_project_list(
    user_id: str, projects: list, ttl: int = CACHE_TTL["project_list"]
):
    """Cache user's project list."""
    return cache.set("projects", projects, ttl=ttl, prefix=f"user:{user_id}")


def get_cached_project_list(user_id: str) -> Optional[list]:
    """Get cached project list."""
    return cache.get("projects", prefix=f"user:{user_id}")


def invalidate_user_cache(user_id: str) -> int:
    """Invalidate all cached data for a user."""
    return cache.invalidate_user(user_id)

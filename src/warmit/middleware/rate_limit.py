"""Rate limiting middleware for API protection.

SECURITY: Protects against brute-force attacks and API abuse.

Developed with ❤️ by Giovanni Rapa
https://github.com/giovannirapa
"""

import time
import logging
from typing import Optional, Dict, Tuple
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RateLimitExceeded(HTTPException):
    """Raised when rate limit is exceeded."""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Please retry after {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        )


class InMemoryRateLimiter:
    """Simple in-memory rate limiter using sliding window.

    For production with multiple workers, consider using Redis-based rate limiting.
    """

    def __init__(self):
        # Format: {key: [(timestamp, count), ...]}
        self._requests: Dict[str, list] = defaultdict(list)
        self._last_cleanup = time.time()
        self._cleanup_interval = 60  # Cleanup every 60 seconds

    def _cleanup_old_entries(self, window_seconds: int) -> None:
        """Remove entries older than the window."""
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return

        cutoff = now - window_seconds
        for key in list(self._requests.keys()):
            self._requests[key] = [
                (ts, count) for ts, count in self._requests[key] if ts > cutoff
            ]
            if not self._requests[key]:
                del self._requests[key]

        self._last_cleanup = now

    def is_rate_limited(
        self, key: str, max_requests: int, window_seconds: int
    ) -> Tuple[bool, int]:
        """Check if key is rate limited.

        Args:
            key: Unique identifier (e.g., IP address or user ID)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            Tuple of (is_limited, retry_after_seconds)
        """
        now = time.time()
        cutoff = now - window_seconds

        # Cleanup periodically
        self._cleanup_old_entries(window_seconds)

        # Filter to requests within window
        self._requests[key] = [
            (ts, count) for ts, count in self._requests[key] if ts > cutoff
        ]

        # Count total requests in window
        total_requests = sum(count for _, count in self._requests[key])

        if total_requests >= max_requests:
            # Calculate retry after
            if self._requests[key]:
                oldest = min(ts for ts, _ in self._requests[key])
                retry_after = int(oldest + window_seconds - now) + 1
            else:
                retry_after = window_seconds
            return True, max(1, retry_after)

        # Add current request
        self._requests[key].append((now, 1))
        return False, 0

    def get_remaining(self, key: str, max_requests: int, window_seconds: int) -> int:
        """Get remaining requests in window."""
        now = time.time()
        cutoff = now - window_seconds

        requests_in_window = [
            (ts, count) for ts, count in self._requests.get(key, []) if ts > cutoff
        ]
        total = sum(count for _, count in requests_in_window)
        return max(0, max_requests - total)


# Global rate limiter instance
_rate_limiter: Optional[InMemoryRateLimiter] = None


def get_rate_limiter() -> InMemoryRateLimiter:
    """Get or create global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = InMemoryRateLimiter()
    return _rate_limiter


# Rate limit configurations per endpoint type
RATE_LIMITS = {
    # Sensitive endpoints - strict limits
    "auth": {"max_requests": 5, "window_seconds": 300},  # 5 per 5 minutes
    "password": {"max_requests": 3, "window_seconds": 300},  # 3 per 5 minutes
    # API endpoints - moderate limits
    "api": {"max_requests": 100, "window_seconds": 60},  # 100 per minute
    # Tracking endpoints - higher limits (emails may have multiple images)
    "tracking": {"max_requests": 500, "window_seconds": 60},  # 500 per minute
    # Default
    "default": {"max_requests": 60, "window_seconds": 60},  # 60 per minute
}


def get_client_ip(request: Request) -> str:
    """Extract client IP from request, considering proxies."""
    # Check X-Forwarded-For header (set by Nginx)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Take the first IP (original client)
        return forwarded.split(",")[0].strip()

    # Check X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fallback to direct client
    if request.client:
        return request.client.host

    return "unknown"


def get_endpoint_type(path: str) -> str:
    """Determine rate limit type based on endpoint path."""
    path_lower = path.lower()

    if "/auth" in path_lower or "/login" in path_lower:
        return "auth"
    if "/password" in path_lower:
        return "password"
    if "/track" in path_lower:
        return "tracking"
    if "/api" in path_lower:
        return "api"

    return "default"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting API requests."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/health/detailed"]:
            return await call_next(request)

        # Get client identifier
        client_ip = get_client_ip(request)

        # Get rate limit config for this endpoint
        endpoint_type = get_endpoint_type(request.url.path)
        config = RATE_LIMITS.get(endpoint_type, RATE_LIMITS["default"])

        # Create rate limit key
        rate_key = f"{client_ip}:{endpoint_type}"

        # Check rate limit
        limiter = get_rate_limiter()
        is_limited, retry_after = limiter.is_rate_limited(
            rate_key, config["max_requests"], config["window_seconds"]
        )

        if is_limited:
            logger.warning(
                f"Rate limit exceeded for {client_ip} on {endpoint_type} endpoints"
            )
            raise RateLimitExceeded(retry_after=retry_after)

        # Add rate limit headers to response
        response = await call_next(request)

        remaining = limiter.get_remaining(
            rate_key, config["max_requests"], config["window_seconds"]
        )
        response.headers["X-RateLimit-Limit"] = str(config["max_requests"])
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(config["window_seconds"])

        return response

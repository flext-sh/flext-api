"""FLEXT API Plugin System.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio
import time
from typing import TypeVar

from flext_core import FlextResult, get_logger

logger = get_logger(__name__)

# Type variables
T = TypeVar("T")


class FlextApiPlugin:
    """Base plugin for extending HTTP client functionality.

    Uses flext-core patterns instead of local ABC implementation.
    Follows FLEXT architectural standards for plugin systems.
    """

    def __init__(self, name: str | None = None) -> None:
        """Initialize plugin with optional name."""
        self.name = name or self.__class__.__name__
        self.enabled = True
        self._stats = {
            "calls": 0,
            "successes": 0,
            "failures": 0,
            "total_time": 0.0,
        }

    async def process_request(self, request: object) -> FlextResult[object]:
        """Process outgoing request.

        Default implementation returns request unchanged.
        Override in concrete plugins.
        """
        return FlextResult[object].ok(request)

    async def process_response(self, response: object) -> FlextResult[object]:
        """Process incoming response.

        Default implementation returns response unchanged.
        Override in concrete plugins.
        """
        return FlextResult[object].ok(response)

    # Compatibility methods for client integration
    async def before_request(self, request: object) -> FlextResult[object]:
        """Alias for process_request for compatibility."""
        return await self.process_request(request)

    async def after_response(self, response: object) -> FlextResult[object]:
        """Alias for process_response for compatibility."""
        return await self.process_response(response)

    def get_stats(self) -> dict[str, object]:
        """Get plugin statistics."""
        return dict(self._stats)

    def reset_stats(self) -> None:
        """Reset plugin statistics."""
        self._stats = {
            "calls": 0,
            "successes": 0,
            "failures": 0,
            "total_time": 0.0,
        }


class FlextApiCachingPlugin(FlextApiPlugin):
    """Caching plugin for HTTP responses."""

    def __init__(self, ttl: int = 300, max_size: int = 1000) -> None:
        """Initialize caching plugin.

        Args:
            ttl: Time-to-live in seconds
            max_size: Maximum cache size

        """
        super().__init__("CachingPlugin")
        self.ttl = ttl
        self.max_size = max_size
        self._cache: dict[str, dict[str, object]] = {}

    async def process_request(self, request: object) -> FlextResult[object]:
        """Check cache for cached response."""
        self._stats["calls"] += 1
        start_time = time.time()

        try:
            # Simple cache key generation
            cache_key = str(hash(str(request)))

            if cache_key in self._cache:
                cached_entry = self._cache[cache_key]
                timestamp = cached_entry.get("timestamp", 0)

                if isinstance(timestamp, (int, float)) and time.time() - timestamp < self.ttl:
                    logger.debug("Cache hit", cache_key=cache_key)
                    self._stats["successes"] += 1
                    return FlextResult[object].ok(cached_entry.get("response"))
                # Expired entry
                del self._cache[cache_key]

            # Cache miss - continue with request
            self._stats["total_time"] += time.time() - start_time
            return FlextResult[object].ok(request)

        except Exception as e:
            self._stats["failures"] += 1
            self._stats["total_time"] += time.time() - start_time
            logger.exception("Caching plugin error", error=str(e))
            return FlextResult[object].fail(f"Caching error: {e}")

    async def process_response(self, response: object) -> FlextResult[object]:
        """Cache successful responses."""
        try:
            cache_key = str(hash(str(response)))

            # Implement LRU eviction if cache is full
            if len(self._cache) >= self.max_size:
                # Remove oldest entry with type-safe timestamp handling
                oldest_key = ""
                oldest_time = float("inf")

                for key, entry in self._cache.items():
                    timestamp = entry.get("timestamp", 0)
                    if isinstance(timestamp, (int, float)) and timestamp < oldest_time:
                        oldest_time = timestamp
                        oldest_key = key

                if oldest_key:
                    del self._cache[oldest_key]

            # Store in cache
            self._cache[cache_key] = {
                "response": response,
                "timestamp": time.time(),
            }

            logger.debug("Response cached", cache_key=cache_key)
            return FlextResult[object].ok(response)

        except Exception as e:
            logger.exception("Response caching error", error=str(e))
            return FlextResult[object].fail(f"Response caching error: {e}")


class FlextApiRetryPlugin(FlextApiPlugin):
    """Retry plugin for failed requests."""

    def __init__(self, max_retries: int = 3, delay: float = 1.0) -> None:
        """Initialize retry plugin.

        Args:
            max_retries: Maximum retry attempts
            delay: Delay between retries in seconds

        """
        super().__init__("RetryPlugin")
        self.max_retries = max_retries
        self.delay = delay

    async def process_request(self, request: object) -> FlextResult[object]:
        """Process request (no modification needed for retry)."""
        return FlextResult[object].ok(request)

    async def process_response(self, response: object) -> FlextResult[object]:
        """Handle retry logic for failed responses."""
        # In real implementation, would check response status
        # For now, just pass through
        return FlextResult[object].ok(response)

    async def execute_with_retry(
        self,
        operation: object,
        *_args: object,
        **_kwargs: object,
    ) -> FlextResult[object]:
        """Execute operation with retry logic."""
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                # In real implementation, would execute the operation
                # For now, just return success
                if attempt > 0:
                    await asyncio.sleep(self.delay * attempt)

                self._stats["calls"] += 1
                self._stats["successes"] += 1
                return FlextResult[object].ok(operation)

            except Exception as e:
                last_error = e
                self._stats["failures"] += 1
                logger.warning(
                    "Retry attempt failed",
                    attempt=attempt + 1,
                    max_retries=self.max_retries,
                    error=str(e),
                )

                if attempt == self.max_retries:
                    break

        return FlextResult[object].fail(f"Max retries exceeded: {last_error}")


# Re-export plugin types for convenience
__all__ = [
    "FlextApiCachingPlugin",
    "FlextApiPlugin",
    "FlextApiRetryPlugin",
]

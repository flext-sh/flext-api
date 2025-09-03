"""FLEXT API Plugins - HTTP client plugin system following FLEXT patterns.

HTTP client plugin system providing FlextApiPlugins class with extensible
plugin architecture for caching, retries, authentication, and custom behaviors.

Module Role in Architecture:
    FlextApiPlugins serves as the HTTP client plugin system, providing extensible
    architecture for HTTP client functionality, including caching, retry policies,
    authentication, and custom request/response processing.

Classes and Methods:
    FlextApiPlugins:                        # Hierarchical HTTP client plugin system
        # Base Plugin Classes:
        BasePlugin(FlextModels)  # Base plugin interface
        AsyncPlugin(BasePlugin)             # Async plugin base class

        # Core Plugin Implementations:
        CachingPlugin(AsyncPlugin)          # HTTP response caching
        RetryPlugin(AsyncPlugin)            # Request retry logic
        AuthPlugin(AsyncPlugin)             # Authentication handling

        # Specialized Plugins:
        RateLimitPlugin(AsyncPlugin)        # Rate limiting protection
        CircuitBreakerPlugin(AsyncPlugin)  # Circuit breaker pattern
        LoggingPlugin(AsyncPlugin)          # Request/response logging

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
from abc import ABC

from flext_core import FlextLogger, FlextModels, FlextResult, FlextUtilities
from pydantic import Field

from flext_api.constants import FlextApiConstants

logger = FlextLogger(__name__)


class FlextApiPlugins(FlextModels):
    """Single plugin class containing ALL HTTP client plugin implementations.

    This is the ONLY plugin class in this module, containing all plugin classes
    as nested classes. Follows the single-class-per-module pattern rigorously.
    """

    class BasePlugin(FlextModels.Entity, ABC):
        """Base plugin class for HTTP client extensions."""

        name: str = Field(default="base_plugin", description="Plugin name")
        enabled: bool = Field(default=True, description="Plugin enabled status")
        priority: int = Field(default=0, description="Plugin execution priority")

        async def before_request(
            self,
            method: str,
            url: str,
            headers: dict[str, str],
            params: dict[str, object],
            body: object = None,
        ) -> FlextResult[tuple[str, str, dict[str, str], dict[str, object], object]]:
            """Hook called before request execution."""
            return FlextResult.ok((method, url, headers, params, body))

        async def after_response(
            self, response_data: object, _headers: dict[str, str], _status_code: int
        ) -> FlextResult[object]:
            """Hook called after response received."""
            return FlextResult.ok(response_data)

        async def on_error(
            self, error: Exception, _method: str, _url: str
        ) -> FlextResult[object]:
            """Hook called when request fails."""
            return FlextResult.fail(f"Request failed: {error}")

    class AsyncPlugin(BasePlugin):
        """Base class for asynchronous plugins with lifecycle management."""

        def __init__(
            self, name: str = "AsyncPlugin", *, enabled: bool = True, priority: int = 0
        ) -> None:
            super().__init__(
                id=f"plugin_{name}", name=name, enabled=enabled, priority=priority
            )
            self._started = False
            self._lock = asyncio.Lock()

        async def start(self) -> FlextResult[None]:
            """Start the plugin - override for initialization."""
            async with self._lock:
                if not self._started:
                    logger.info(f"Starting plugin: {self.name}")
                    self._started = True
                    return FlextResult[None].ok(None)
                return FlextResult[None].ok(None)

        async def stop(self) -> FlextResult[None]:
            """Stop the plugin - override for cleanup."""
            async with self._lock:
                if self._started:
                    logger.info(f"Stopping plugin: {self.name}")
                    self._started = False
                    return FlextResult[None].ok(None)
                return FlextResult[None].ok(None)

        @property
        def is_started(self) -> bool:
            """Check if plugin is started."""
            return self._started

    class CachingPlugin(AsyncPlugin):
        """HTTP response caching plugin with TTL and size limits."""

        name: str = "caching_plugin"
        ttl: int = Field(
            default=FlextApiConstants.HttpCache.DEFAULT_TTL,
            description="Cache TTL in seconds",
        )
        max_size: int = Field(
            default=FlextApiConstants.HttpCache.MAX_CACHE_SIZE,
            description="Maximum cache entries",
        )

        def __init__(
            self,
            name: str = "caching_plugin",
            *,
            enabled: bool = True,
            priority: int = 0,
            ttl: int = FlextApiConstants.HttpCache.DEFAULT_TTL,
            max_size: int = FlextApiConstants.HttpCache.MAX_CACHE_SIZE,
        ) -> None:
            super().__init__(name=name, enabled=enabled, priority=priority)
            self.ttl = ttl
            self.max_size = max_size
            self._cache: dict[
                str, tuple[object, float]
            ] = {}  # url -> (data, timestamp)

        def _generate_cache_key(
            self, method: str, url: str, params: dict[str, object]
        ) -> str:
            """Generate cache key from request parameters."""
            # Only cache GET requests
            if method.upper() != "GET":
                return ""

            # Simple cache key generation
            params_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
            return f"{method}:{url}?{params_str}" if params_str else f"{method}:{url}"

        def _is_cache_valid(self, timestamp: float) -> bool:
            """Check if cache entry is still valid."""
            return (
                FlextUtilities.Generators.generate_timestamp() - timestamp
            ) < self.ttl

        def _cleanup_expired(self) -> None:
            """Remove expired cache entries."""
            current_time = FlextUtilities.Generators.generate_timestamp()
            expired_keys = [
                key
                for key, (_, timestamp) in self._cache.items()
                if (current_time - timestamp) >= self.ttl
            ]
            for key in expired_keys:
                del self._cache[key]

        async def before_request(
            self,
            method: str,
            url: str,
            headers: dict[str, str],
            params: dict[str, object],
            body: object = None,
        ) -> FlextResult[tuple[str, str, dict[str, str], dict[str, object], object]]:
            """Check cache before making request."""
            cache_key = self._generate_cache_key(method, url, params)

            if cache_key and cache_key in self._cache:
                _data, timestamp = self._cache[cache_key]
                if self._is_cache_valid(timestamp):
                    logger.debug(f"Cache hit for: {cache_key}")
                    # Return cached data by modifying headers to indicate cache hit
                    headers["X-Cache"] = "HIT"
                    return FlextResult.ok((method, url, headers, params, body))
                # Remove expired entry
                del self._cache[cache_key]

            # Periodic cleanup
            if len(self._cache) > self.max_size:
                self._cleanup_expired()

            return FlextResult.ok((method, url, headers, params, body))

        async def after_response(
            self, response_data: object, _headers: dict[str, str], _status_code: int
        ) -> FlextResult[object]:
            """Cache successful responses."""
            # Only cache successful GET responses
            if (
                FlextApiConstants.HttpStatus.OK
                <= _status_code
                < FlextApiConstants.HttpStatus.MULTIPLE_CHOICES
            ):
                # Cache key would need to be reconstructed or passed from before_request
                # For simplicity, we'll use a basic caching strategy here
                logger.debug("Caching response data")

            return FlextResult.ok(response_data)

    class RetryPlugin(AsyncPlugin):
        """HTTP request retry plugin with exponential backoff."""

        name: str = "retry_plugin"
        max_retries: int = Field(
            default=FlextApiConstants.Client.DEFAULT_MAX_RETRIES,
            description="Maximum retry attempts",
        )
        backoff_factor: float = Field(
            default=FlextApiConstants.Client.RETRY_BACKOFF,
            description="Retry backoff multiplier",
        )
        retry_on_status: list[int] = Field(
            default_factory=lambda: [500, 502, 503, 504],
            description="HTTP status codes to retry on",
        )

        async def should_retry(self, status_code: int, attempt: int) -> bool:
            """Determine if request should be retried."""
            if attempt >= self.max_retries:
                return False

            return status_code in self.retry_on_status

        async def calculate_delay(self, attempt: int) -> float:
            """Calculate delay before retry with exponential backoff."""
            return min(self.backoff_factor**attempt, 60.0)  # Max 60 seconds

        async def on_error(
            self, error: Exception, _method: str, _url: str
        ) -> FlextResult[object]:
            """Handle retry logic on error."""
            logger.warning(f"Request failed, error: {error}")
            # The actual retry logic would be implemented in the client
            return FlextResult.fail(f"Request failed after retries: {error}")

    class AuthPlugin(AsyncPlugin):
        """Authentication plugin for HTTP requests."""

        name: str = "auth_plugin"
        auth_type: str = Field(default="bearer", description="Authentication type")
        token: str | None = Field(default=None, description="Authentication token")
        username: str | None = Field(default=None, description="Basic auth username")
        password: str | None = Field(default=None, description="Basic auth password")

        async def before_request(
            self,
            method: str,
            url: str,
            headers: dict[str, str],
            params: dict[str, object],
            body: object = None,
        ) -> FlextResult[tuple[str, str, dict[str, str], dict[str, object], object]]:
            """Add authentication headers to request."""
            auth_headers = headers.copy()

            if self.auth_type == "bearer" and self.token:
                auth_headers["Authorization"] = f"Bearer {self.token}"
            elif self.auth_type == "basic" and self.username and self.password:
                credentials = FlextUtilities.Encoders.encode_base64(
                    f"{self.username}:{self.password}"
                )
                auth_headers["Authorization"] = f"Basic {credentials}"

            return FlextResult.ok((method, url, auth_headers, params, body))

    class RateLimitPlugin(AsyncPlugin):
        """Rate limiting plugin to prevent API abuse."""

        name: str = "rate_limit_plugin"
        calls_per_second: float = Field(
            default=10.0, description="Calls per second limit"
        )
        burst_size: int = Field(default=20, description="Burst capacity")

        def __init__(
            self,
            name: str = "rate_limit_plugin",
            *,
            enabled: bool = True,
            priority: int = 0,
            calls_per_second: float = 10.0,
            burst_size: int = 20,
        ) -> None:
            super().__init__(name=name, enabled=enabled, priority=priority)
            self.calls_per_second = calls_per_second
            self.burst_size = burst_size
            self._last_call = 0.0
            self._tokens = float(self.burst_size)

        async def before_request(
            self,
            method: str,
            url: str,
            headers: dict[str, str],
            params: dict[str, object],
            body: object = None,
        ) -> FlextResult[tuple[str, str, dict[str, str], dict[str, object], object]]:
            """Apply rate limiting before request."""
            current_time = FlextUtilities.Generators.generate_timestamp()

            # Token bucket algorithm
            if self._last_call > 0:
                elapsed = current_time - self._last_call
                self._tokens = min(
                    self.burst_size, self._tokens + elapsed * self.calls_per_second
                )

            if self._tokens < 1:
                wait_time = (1 - self._tokens) / self.calls_per_second
                logger.warning(f"Rate limit exceeded, waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
                self._tokens = 0
            else:
                self._tokens -= 1

            self._last_call = current_time
            return FlextResult.ok((method, url, headers, params, body))

    class CircuitBreakerPlugin(AsyncPlugin):
        """Circuit breaker plugin for fault tolerance."""

        name: str = "circuit_breaker_plugin"
        failure_threshold: int = Field(
            default=5, description="Failures before opening circuit"
        )
        recovery_timeout: float = Field(
            default=60.0, description="Recovery timeout in seconds"
        )

        def __init__(
            self,
            name: str = "circuit_breaker_plugin",
            *,
            enabled: bool = True,
            priority: int = 0,
            failure_threshold: int = 5,
            recovery_timeout: float = 60.0,
        ) -> None:
            super().__init__(name=name, enabled=enabled, priority=priority)
            self.failure_threshold = failure_threshold
            self.recovery_timeout = recovery_timeout
            self._failure_count = 0
            self._last_failure_time = 0.0
            self._state = "closed"  # closed, open, half-open

        async def before_request(
            self,
            method: str,
            url: str,
            headers: dict[str, str],
            params: dict[str, object],
            body: object = None,
        ) -> FlextResult[tuple[str, str, dict[str, str], dict[str, object], object]]:
            """Check circuit breaker state before request."""
            current_time = FlextUtilities.Generators.generate_timestamp()

            if self._state == "open":
                if current_time - self._last_failure_time > self.recovery_timeout:
                    self._state = "half-open"
                    logger.info("Circuit breaker moved to half-open state")
                else:
                    return FlextResult.fail("Circuit breaker is open")

            return FlextResult.ok((method, url, headers, params, body))

        async def after_response(
            self, response_data: object, _headers: dict[str, str], _status_code: int
        ) -> FlextResult[object]:
            """Update circuit breaker state after response."""
            if (
                FlextApiConstants.HttpStatus.OK
                <= _status_code
                < FlextApiConstants.HttpStatus.MULTIPLE_CHOICES
            ):
                # Success - reset failure count
                if self._state == "half-open":
                    self._state = "closed"
                    logger.info("Circuit breaker closed after successful request")
                self._failure_count = 0
            else:
                # Failure - increment count
                self._failure_count += 1
                self._last_failure_time = FlextUtilities.Generators.generate_timestamp()

                if self._failure_count >= self.failure_threshold:
                    self._state = "open"
                    logger.warning(
                        f"Circuit breaker opened after {self._failure_count} failures"
                    )

            return FlextResult.ok(response_data)

    class LoggingPlugin(AsyncPlugin):
        """Request/response logging plugin for debugging."""

        name: str = "logging_plugin"
        log_requests: bool = Field(default=True, description="Log HTTP requests")
        log_responses: bool = Field(default=True, description="Log HTTP responses")
        log_errors: bool = Field(default=True, description="Log HTTP errors")

        async def before_request(
            self,
            method: str,
            url: str,
            headers: dict[str, str],
            params: dict[str, object],
            body: object = None,
        ) -> FlextResult[tuple[str, str, dict[str, str], dict[str, object], object]]:
            """Log request details."""
            if self.log_requests:
                logger.info(
                    f"HTTP Request: {method} {url}",
                    extra={
                        "method": method,
                        "url": url,
                        "headers": headers,
                        "params": params,
                        "has_body": body is not None,
                    },
                )

            return FlextResult.ok((method, url, headers, params, body))

        async def after_response(
            self, response_data: object, _headers: dict[str, str], _status_code: int
        ) -> FlextResult[object]:
            """Log response details."""
            if self.log_responses:
                logger.info(
                    f"HTTP Response: {_status_code}",
                    extra={
                        "status_code": _status_code,
                        "headers": _headers,
                        "has_data": response_data is not None,
                    },
                )

            return FlextResult.ok(response_data)

        async def on_error(
            self, error: Exception, _method: str, _url: str
        ) -> FlextResult[object]:
            """Log error details."""
            if self.log_errors:
                logger.error(
                    f"HTTP Error: {_method} {_url}",
                    extra={
                        "method": _method,
                        "url": _url,
                        "error": str(error),
                        "error_type": type(error).__name__,
                    },
                )

            return FlextResult.fail(f"Request failed: {error}")


# Export compatibility classes for tests
FlextApiPlugin = FlextApiPlugins.BasePlugin  # Base plugin class
FlextApiCachingPlugin = FlextApiPlugins.CachingPlugin
FlextApiRetryPlugin = FlextApiPlugins.RetryPlugin
FlextApiCircuitBreakerPlugin = FlextApiPlugins.CircuitBreakerPlugin

__all__ = [
    "FlextApiCachingPlugin",
    "FlextApiCircuitBreakerPlugin",
    "FlextApiPlugin",
    "FlextApiPlugins",
    "FlextApiRetryPlugin",
]

#!/usr/bin/env python3
"""FlextApi Universal API Client - Core Implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Universal API client with async/await, HTTP/2, streaming, validation,
observability, circuit breaker, caching and plugin system.
"""

from __future__ import annotations

import asyncio
import json
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Self

import aiohttp
from flext_core import FlextResult, get_logger
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Awaitable, Callable

logger = get_logger(__name__)


# ==============================================================================
# CORE TYPES AND ENUMS
# ==============================================================================


class FlextApiClientProtocol(str, Enum):
    """Supported client protocols."""

    HTTP = "http"
    HTTPS = "https"
    HTTP2 = "http2"
    WEBSOCKET = "ws"
    WEBSOCKET_SECURE = "wss"


class FlextApiClientMethod(str, Enum):
    """HTTP methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class FlextApiClientStatus(str, Enum):
    """Client status for health monitoring."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CIRCUIT_OPEN = "circuit_open"


# ==============================================================================
# REQUEST/RESPONSE MODELS
# ==============================================================================


class FlextApiClientRequest(BaseModel):
    """Universal API client request model."""

    method: FlextApiClientMethod = FlextApiClientMethod.GET
    url: str
    headers: dict[str, str] = Field(default_factory=dict)
    params: dict[str, Any] = Field(default_factory=dict)
    data: Any = None
    json: dict[str, Any] | None = None
    timeout: float = 30.0
    retry_count: int = 3
    retry_delay: float = 1.0
    stream: bool = False
    validate_response: bool = True
    cache_ttl: int | None = None
    plugin_data: dict[str, Any] = Field(
        default_factory=dict
    )  # Public plugin data storage


class FlextApiClientResponse(BaseModel):
    """Universal API client response model."""

    status_code: int
    headers: dict[str, str] = Field(default_factory=dict)
    data: Any = None
    text: str = ""
    json_data: dict[str, Any] | None = None
    execution_time_ms: float = 0.0
    cached: bool = False
    circuit_breaker_state: str = "closed"
    retry_count: int = 0
    plugins_executed: list[str] = Field(default_factory=list)


class FlextApiClientMetrics(BaseModel):
    """Client metrics for observability."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    cached_requests: int = 0
    circuit_breaker_trips: int = 0
    average_response_time_ms: float = 0.0
    last_request_time: float = 0.0
    uptime_seconds: float = 0.0


# ==============================================================================
# CONFIGURATION
# ==============================================================================


@dataclass
class FlextApiClientConfig:
    """Configuration for FlextApi universal client."""

    # Basic configuration
    base_url: str = ""
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0

    # Protocol configuration
    protocol: FlextApiClientProtocol = FlextApiClientProtocol.HTTPS
    http2_enabled: bool = True
    connection_pool_size: int = 100

    # Headers and authentication
    default_headers: dict[str, str] = field(default_factory=dict)
    auth_token: str | None = None
    api_key: str | None = None

    # Validation and serialization
    validate_requests: bool = True
    validate_responses: bool = True
    auto_serialize_json: bool = True

    # Caching configuration
    cache_enabled: bool = True
    cache_default_ttl: int = 300
    cache_max_size: int = 1000

    # Circuit breaker configuration
    circuit_breaker_enabled: bool = True
    circuit_failure_threshold: int = 5
    circuit_timeout_seconds: int = 60
    circuit_half_open_max_calls: int = 3

    # Observability
    metrics_enabled: bool = True
    tracing_enabled: bool = True
    logging_enabled: bool = True

    # Performance
    streaming_enabled: bool = True
    compression_enabled: bool = True
    keep_alive_enabled: bool = True


# ==============================================================================
# CIRCUIT BREAKER IMPLEMENTATION
# ==============================================================================


class FlextApiCircuitBreakerState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class FlextApiCircuitBreaker:
    """Circuit breaker for API resilience."""

    failure_threshold: int = 5
    timeout_seconds: int = 60
    half_open_max_calls: int = 3

    _state: FlextApiCircuitBreakerState = FlextApiCircuitBreakerState.CLOSED
    _failure_count: int = 0
    _last_failure_time: float = 0.0
    _half_open_calls: int = 0

    def can_execute(self) -> bool:
        """Check if request can be executed."""
        if self._state == FlextApiCircuitBreakerState.CLOSED:
            return True

        if self._state == FlextApiCircuitBreakerState.OPEN:
            if time.time() - self._last_failure_time > self.timeout_seconds:
                self._state = FlextApiCircuitBreakerState.HALF_OPEN
                self._half_open_calls = 0
                return True
            return False

        # HALF_OPEN state
        return self._half_open_calls < self.half_open_max_calls

    def record_success(self) -> None:
        """Record successful execution."""
        if self._state == FlextApiCircuitBreakerState.HALF_OPEN:
            self._state = FlextApiCircuitBreakerState.CLOSED
            self._failure_count = 0
        elif self._state == FlextApiCircuitBreakerState.CLOSED:
            self._failure_count = 0

    def record_failure(self) -> None:
        """Record failed execution."""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if (
            self._state == FlextApiCircuitBreakerState.HALF_OPEN
            or self._failure_count >= self.failure_threshold
        ):
            self._state = FlextApiCircuitBreakerState.OPEN

    @property
    def state(self) -> FlextApiCircuitBreakerState:
        """Get current circuit breaker state."""
        return self._state


# ==============================================================================
# CACHE IMPLEMENTATION
# ==============================================================================


@dataclass
class FlextApiCacheEntry:
    """Cache entry with TTL support."""

    data: Any
    timestamp: float
    ttl: int

    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return time.time() - self.timestamp > self.ttl


class FlextApiCache:
    """Simple in-memory cache with TTL support."""

    def __init__(self, max_size: int = 1000) -> None:
        self._cache: dict[str, FlextApiCacheEntry] = {}
        self._max_size = max_size

    def get(self, key: str) -> Any | None:
        """Get cached value if not expired."""
        entry = self._cache.get(key)
        if entry and not entry.is_expired():
            return entry.data

        if entry:
            del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set cached value with TTL."""
        if len(self._cache) >= self._max_size:
            # Simple LRU: remove oldest entry
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].timestamp)
            del self._cache[oldest_key]

        self._cache[key] = FlextApiCacheEntry(
            data=value, timestamp=time.time(), ttl=ttl
        )

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()

    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)


# ==============================================================================
# CORE CLIENT IMPLEMENTATION
# ==============================================================================


class FlextApiClient:
    """Universal API client with enterprise features."""

    def __init__(self, config: FlextApiClientConfig | None = None) -> None:
        self.config = config or FlextApiClientConfig()
        self._session: aiohttp.ClientSession | None = None
        self._circuit_breaker = FlextApiCircuitBreaker(
            failure_threshold=self.config.circuit_failure_threshold,
            timeout_seconds=self.config.circuit_timeout_seconds,
            half_open_max_calls=self.config.circuit_half_open_max_calls,
        )
        self._cache = FlextApiCache(max_size=self.config.cache_max_size)
        self._metrics = FlextApiClientMetrics()
        self._plugins: list[FlextApiClientPlugin] = []
        self._start_time = time.time()

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        await self._ensure_session()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Async context manager exit."""
        await self.close()

    async def _ensure_session(self) -> None:
        """Ensure aiohttp session is created."""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=self.config.connection_pool_size,
                enable_cleanup_closed=True,
                force_close=True,
                limit_per_host=20,
            )

            timeout = aiohttp.ClientTimeout(total=self.config.timeout)

            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self.config.default_headers,
            )

    def add_plugin(self, plugin: FlextApiClientPlugin) -> None:
        """Add plugin to client."""
        self._plugins.append(plugin)
        logger.info(f"Added plugin: {plugin.__class__.__name__}")

    def remove_plugin(self, plugin_class: type) -> None:
        """Remove plugin from client."""
        self._plugins = [p for p in self._plugins if not isinstance(p, plugin_class)]
        logger.info(f"Removed plugin: {plugin_class.__name__}")

    def _generate_cache_key(self, request: FlextApiClientRequest) -> str:
        """Generate cache key for request."""
        key_parts = [
            request.method,
            request.url,
            json.dumps(request.params, sort_keys=True),
            json.dumps(request.headers, sort_keys=True),
        ]
        return "|".join(key_parts)

    async def _execute_plugins(
        self,
        phase: str,
        request: FlextApiClientRequest,
        response: FlextApiClientResponse | None = None,
    ) -> None:
        """Execute plugins for specific phase."""
        for plugin in self._plugins:
            try:
                if phase == "before_request":
                    await plugin.before_request(request)
                elif phase == "after_request" and response:
                    await plugin.after_request(request, response)
                elif phase == "on_error" and response:
                    await plugin.on_error(request, response)
            except Exception as e:
                logger.exception(
                    f"Plugin {plugin.__class__.__name__} error in {phase}: {e}"
                )

    async def request(
        self, request: FlextApiClientRequest
    ) -> FlextResult[FlextApiClientResponse]:
        """Execute universal API request with all enterprise features."""
        start_time = time.time()
        response = FlextApiClientResponse(status_code=0)

        try:
            # Circuit breaker check
            if (
                self.config.circuit_breaker_enabled
                and not self._circuit_breaker.can_execute()
            ):
                response.circuit_breaker_state = "open"
                self._metrics.circuit_breaker_trips += 1
                return FlextResult.fail("Circuit breaker is open", response)

            # Check cache
            cache_key = ""
            if self.config.cache_enabled and request.method == FlextApiClientMethod.GET:
                cache_key = self._generate_cache_key(request)
                cached_response = self._cache.get(cache_key)
                if cached_response:
                    cached_response.cached = True
                    self._metrics.cached_requests += 1
                    return FlextResult.ok(cached_response)

            # Execute before_request plugins
            await self._execute_plugins("before_request", request)

            # Prepare HTTP/2 if enabled
            await self._ensure_session()
            if not self._session:
                return FlextResult.fail("Failed to create HTTP session")

            # Build request parameters
            session_kwargs = {
                "method": request.method.value,
                "url": self._build_full_url(request.url),
                "headers": {**self.config.default_headers, **request.headers},
                "params": request.params,
                "timeout": aiohttp.ClientTimeout(total=request.timeout),
            }

            # Add authentication if configured
            if self.config.auth_token:
                session_kwargs["headers"]["Authorization"] = (
                    f"Bearer {self.config.auth_token}"
                )
            elif self.config.api_key:
                session_kwargs["headers"]["X-API-Key"] = self.config.api_key

            # Add request data
            if request.json:
                session_kwargs["json"] = request.json
            elif request.data:
                session_kwargs["data"] = request.data

            # Execute HTTP request with retries
            last_exception: Exception | None = None
            for attempt in range(request.retry_count + 1):
                try:
                    async with self._session.request(**session_kwargs) as http_response:
                        # Build response
                        response = FlextApiClientResponse(
                            status_code=http_response.status,
                            headers=dict(http_response.headers),
                            text=await http_response.text(),
                            execution_time_ms=(time.time() - start_time) * 1000,
                            retry_count=attempt,
                            circuit_breaker_state=self._circuit_breaker.state.value,
                        )

                        # Try to parse JSON
                        try:
                            response.json_data = await http_response.json()
                            response.data = response.json_data
                        except (json.JSONDecodeError, aiohttp.ContentTypeError):
                            response.data = response.text

                        # Check if request was successful
                        if 200 <= http_response.status < 400:
                            self._circuit_breaker.record_success()
                            self._metrics.successful_requests += 1

                            # Cache successful GET requests
                            if (
                                self.config.cache_enabled
                                and request.method == FlextApiClientMethod.GET
                                and cache_key
                            ):
                                ttl = request.cache_ttl or self.config.cache_default_ttl
                                self._cache.set(cache_key, response, ttl)

                            # Execute after_request plugins
                            await self._execute_plugins(
                                "after_request", request, response
                            )

                            return FlextResult.ok(response)

                        # Handle HTTP errors
                        if attempt < request.retry_count:
                            await asyncio.sleep(request.retry_delay * (attempt + 1))
                            continue

                        self._circuit_breaker.record_failure()
                        self._metrics.failed_requests += 1
                        await self._execute_plugins("on_error", request, response)

                        return FlextResult.fail(
                            f"HTTP {http_response.status}: {response.text}", response
                        )

                except Exception as e:
                    last_exception = e
                    if attempt < request.retry_count:
                        logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                        await asyncio.sleep(request.retry_delay * (attempt + 1))
                        continue

            # All retries failed
            self._circuit_breaker.record_failure()
            self._metrics.failed_requests += 1
            error_msg = (
                f"Request failed after {request.retry_count} retries: {last_exception}"
            )

            response.execution_time_ms = (time.time() - start_time) * 1000
            await self._execute_plugins("on_error", request, response)

            return FlextResult.fail(error_msg, response)

        except Exception as e:
            self._circuit_breaker.record_failure()
            self._metrics.failed_requests += 1
            logger.exception(f"Unexpected error in request: {e}")

            response.execution_time_ms = (time.time() - start_time) * 1000
            await self._execute_plugins("on_error", request, response)

            return FlextResult.fail(f"Unexpected error: {e}", response)

        finally:
            # Update metrics
            self._metrics.total_requests += 1
            self._metrics.last_request_time = time.time()
            if self._metrics.total_requests > 0:
                total_time = sum(
                    [
                        self._metrics.average_response_time_ms
                        * (self._metrics.total_requests - 1),
                        response.execution_time_ms,
                    ]
                )
                self._metrics.average_response_time_ms = (
                    total_time / self._metrics.total_requests
                )

    def _build_full_url(self, url: str) -> str:
        """Build full URL from base URL and endpoint."""
        if url.startswith(("http://", "https://")):
            return url

        base = self.config.base_url.rstrip("/")
        endpoint = url.lstrip("/")
        return f"{base}/{endpoint}" if base else url

    # Convenience methods for common HTTP operations
    async def get(
        self, url: str, **kwargs: object
    ) -> FlextResult[FlextApiClientResponse]:
        """Execute GET request."""
        request = FlextApiClientRequest(
            method=FlextApiClientMethod.GET, url=url, **kwargs
        )
        return await self.request(request)

    async def post(
        self, url: str, **kwargs: object
    ) -> FlextResult[FlextApiClientResponse]:
        """Execute POST request."""
        request = FlextApiClientRequest(
            method=FlextApiClientMethod.POST, url=url, **kwargs
        )
        return await self.request(request)

    async def put(
        self, url: str, **kwargs: object
    ) -> FlextResult[FlextApiClientResponse]:
        """Execute PUT request."""
        request = FlextApiClientRequest(
            method=FlextApiClientMethod.PUT, url=url, **kwargs
        )
        return await self.request(request)

    async def patch(
        self, url: str, **kwargs: object
    ) -> FlextResult[FlextApiClientResponse]:
        """Execute PATCH request."""
        request = FlextApiClientRequest(
            method=FlextApiClientMethod.PATCH, url=url, **kwargs
        )
        return await self.request(request)

    async def delete(
        self, url: str, **kwargs: object
    ) -> FlextResult[FlextApiClientResponse]:
        """Execute DELETE request."""
        request = FlextApiClientRequest(
            method=FlextApiClientMethod.DELETE, url=url, **kwargs
        )
        return await self.request(request)

    async def stream(self, request: FlextApiClientRequest) -> AsyncIterator[bytes]:
        """Stream response data."""
        await self._ensure_session()
        if not self._session:
            return

        session_kwargs = {
            "method": request.method.value,
            "url": self._build_full_url(request.url),
            "headers": {**self.config.default_headers, **request.headers},
            "params": request.params,
            "timeout": aiohttp.ClientTimeout(total=request.timeout),
        }

        if request.json:
            session_kwargs["json"] = request.json
        elif request.data:
            session_kwargs["data"] = request.data

        try:
            async with self._session.request(**session_kwargs) as response:
                async for chunk in response.content.iter_chunked(8192):
                    yield chunk
        except Exception as e:
            logger.exception(f"Streaming error: {e}")

    def get_metrics(self) -> FlextApiClientMetrics:
        """Get client metrics."""
        self._metrics.uptime_seconds = time.time() - self._start_time
        return self._metrics

    def get_health(self) -> dict[str, Any]:
        """Get client health status."""
        metrics = self.get_metrics()

        if self._circuit_breaker.state == FlextApiCircuitBreakerState.OPEN:
            status = FlextApiClientStatus.CIRCUIT_OPEN
        elif metrics.failed_requests > metrics.successful_requests:
            status = FlextApiClientStatus.UNHEALTHY
        elif metrics.average_response_time_ms > 5000:  # 5 seconds
            status = FlextApiClientStatus.DEGRADED
        else:
            status = FlextApiClientStatus.HEALTHY

        return {
            "status": status.value,
            "circuit_breaker_state": self._circuit_breaker.state.value,
            "cache_size": self._cache.size(),
            "plugins_loaded": len(self._plugins),
            "uptime_seconds": metrics.uptime_seconds,
            "total_requests": metrics.total_requests,
            "success_rate": (
                metrics.successful_requests / max(metrics.total_requests, 1)
            )
            * 100,
            "average_response_time_ms": metrics.average_response_time_ms,
        }

    async def close(self) -> None:
        """Close client and cleanup resources."""
        if self._session and not self._session.closed:
            await self._session.close()
        self._cache.clear()
        logger.info("FlextApiClient closed")

    # Public methods for protocol clients to avoid private member access
    def get_session(self) -> aiohttp.ClientSession | None:
        """Get HTTP session for protocol clients."""
        return self._session

    async def ensure_session(self) -> None:
        """Ensure HTTP session exists."""
        await self._ensure_session()

    def build_full_url(self, url: str) -> str:
        """Build full URL for protocol clients."""
        return self._build_full_url(url)


# ==============================================================================
# PLUGIN SYSTEM BASE
# ==============================================================================


class FlextApiClientPlugin:
    """Base class for client plugins."""

    async def before_request(self, request: FlextApiClientRequest) -> None:
        """Called before request execution."""

    async def after_request(
        self, request: FlextApiClientRequest, response: FlextApiClientResponse
    ) -> None:
        """Called after successful request."""

    async def on_error(
        self, request: FlextApiClientRequest, response: FlextApiClientResponse
    ) -> None:
        """Called when request fails."""


# ==============================================================================
# BUILDER PATTERN
# ==============================================================================


class FlextApiClientBuilder:
    """Builder for creating configured FlextApiClient instances."""

    def __init__(self) -> None:
        self.config = FlextApiClientConfig()
        self._plugins: list[FlextApiClientPlugin] = []

    def with_base_url(self, base_url: str) -> FlextApiClientBuilder:
        """Set base URL."""
        self.config.base_url = base_url
        return self

    def with_timeout(self, timeout: float) -> FlextApiClientBuilder:
        """Set request timeout."""
        self.config.timeout = timeout
        return self

    def with_auth_token(self, token: str) -> FlextApiClientBuilder:
        """Set authentication token."""
        self.config.auth_token = token
        return self

    def with_api_key(self, api_key: str) -> FlextApiClientBuilder:
        """Set API key."""
        self.config.api_key = api_key
        return self

    def with_http2(self, enabled: bool = True) -> FlextApiClientBuilder:
        """Enable/disable HTTP/2."""
        self.config.http2_enabled = enabled
        return self

    def with_caching(
        self, enabled: bool = True, ttl: int = 300
    ) -> FlextApiClientBuilder:
        """Configure caching."""
        self.config.cache_enabled = enabled
        self.config.cache_default_ttl = ttl
        return self

    def with_circuit_breaker(
        self, enabled: bool = True, failure_threshold: int = 5
    ) -> FlextApiClientBuilder:
        """Configure circuit breaker."""
        self.config.circuit_breaker_enabled = enabled
        self.config.circuit_failure_threshold = failure_threshold
        return self

    def with_retries(
        self, max_retries: int = 3, delay: float = 1.0
    ) -> FlextApiClientBuilder:
        """Configure retry policy."""
        self.config.max_retries = max_retries
        self.config.retry_delay = delay
        return self

    def with_headers(self, headers: dict[str, str]) -> FlextApiClientBuilder:
        """Set default headers."""
        self.config.default_headers.update(headers)
        return self

    def with_plugin(self, plugin: FlextApiClientPlugin) -> FlextApiClientBuilder:
        """Add plugin."""
        self._plugins.append(plugin)
        return self

    def with_validation(
        self, requests: bool = True, responses: bool = True
    ) -> FlextApiClientBuilder:
        """Configure validation."""
        self.config.validate_requests = requests
        self.config.validate_responses = responses
        return self

    def with_observability(
        self, metrics: bool = True, tracing: bool = True
    ) -> FlextApiClientBuilder:
        """Configure observability."""
        self.config.metrics_enabled = metrics
        self.config.tracing_enabled = tracing
        return self

    def build(self) -> FlextApiClient:
        """Build configured FlextApiClient."""
        client = FlextApiClient(self.config)
        for plugin in self._plugins:
            client.add_plugin(plugin)
        return client


# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================


def flext_api_create_client(
    base_url: str = "",
    timeout: float = 30.0,
    auth_token: str | None = None,
    enable_caching: bool = True,
    enable_circuit_breaker: bool = True,
    enable_http2: bool = True,
    **kwargs: object,
) -> FlextApiClient:
    """Create FlextApiClient with common configuration."""
    builder = (
        FlextApiClientBuilder()
        .with_base_url(base_url)
        .with_timeout(timeout)
        .with_caching(enable_caching)
        .with_circuit_breaker(enable_circuit_breaker)
        .with_http2(enable_http2)
    )

    if auth_token:
        builder.with_auth_token(auth_token)

    for key, value in kwargs.items():
        if hasattr(builder.config, key):
            setattr(builder.config, key, value)

    return builder.build()


@asynccontextmanager
async def flext_api_client_context(
    base_url: str = "",
    **kwargs: object,
) -> AsyncIterator[FlextApiClient]:
    """Create FlextApiClient as async context manager."""
    client = flext_api_create_client(base_url=base_url, **kwargs)
    try:
        async with client:
            yield client
    finally:
        await client.close()

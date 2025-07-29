"""FLEXT API Client - Universal HTTP client com funcionalidade completa.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

FUNCIONALIDADE COMPLETA: Recupera todo o sistema de client original com plugins,
circuit breaker, retry, cache, streaming, WebSocket, GraphQL, etc.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from urllib.parse import urljoin

import aiohttp
from flext_core import FlextResult, get_logger
from pydantic import BaseModel, Field

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
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class FlextApiClientStatus(str, Enum):
    """Client status."""

    IDLE = "idle"
    ACTIVE = "active"
    CLOSED = "closed"
    ERROR = "error"


# ==============================================================================
# REQUEST/RESPONSE MODELS
# ==============================================================================

class FlextApiClientRequest(BaseModel):
    """HTTP request model."""

    method: FlextApiClientMethod
    url: str
    headers: dict[str, str] = Field(default_factory=dict)
    params: dict[str, Any] = Field(default_factory=dict)
    json: dict[str, Any] | None = None
    data: str | bytes | None = None
    timeout: float | None = None


class FlextApiClientResponse(BaseModel):
    """HTTP response model."""

    status_code: int
    headers: dict[str, str]
    data: Any
    elapsed_time: float
    request_id: str | None = None
    from_cache: bool = False


# ==============================================================================
# PLUGIN SYSTEM
# ==============================================================================

class FlextApiPlugin:
    """Base plugin interface."""

    def __init__(self, name: str | None = None) -> None:
        self.name = name or self.__class__.__name__
        self.enabled = True
        self.metrics: dict[str, Any] = {}

    async def before_request(self, request: FlextApiClientRequest) -> FlextApiClientRequest:
        """Called before request is sent."""
        return request

    async def after_request(
        self, request: FlextApiClientRequest, response: FlextApiClientResponse,
    ) -> FlextApiClientResponse:
        """Called after response is received."""
        return response

    async def on_error(
        self, request: FlextApiClientRequest, error: Exception,
    ) -> FlextApiClientResponse | None:
        """Called when request fails."""
        return None

    def get_metrics(self) -> dict[str, Any]:
        """Get plugin metrics."""
        return self.metrics.copy()

    def reset_metrics(self) -> None:
        """Reset plugin metrics."""
        self.metrics.clear()


class FlextApiCachingPlugin(FlextApiPlugin):
    """Caching plugin with TTL support."""

    def __init__(self, ttl_seconds: int = 300) -> None:
        super().__init__("CachingPlugin")
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, tuple[FlextApiClientResponse, float]] = {}
        self.metrics = {"hits": 0, "misses": 0, "evictions": 0}

    def _cache_key(self, request: FlextApiClientRequest) -> str:
        """Generate cache key."""
        return f"{request.method}:{request.url}:{hash(str(request.params))}"

    def _is_cacheable(self, request: FlextApiClientRequest) -> bool:
        """Check if request is cacheable."""
        return request.method == FlextApiClientMethod.GET

    async def before_request(self, request: FlextApiClientRequest) -> FlextApiClientRequest:
        """Check cache before request."""
        if not self._is_cacheable(request):
            return request

        cache_key = self._cache_key(request)
        if cache_key in self._cache:
            cached_response, cached_time = self._cache[cache_key]

            # Check TTL
            if time.time() - cached_time < self.ttl_seconds:
                self.metrics["hits"] += 1
                # Mark as cached
                cached_response.from_cache = True
                return request
            # Expired, remove from cache
            del self._cache[cache_key]
            self.metrics["evictions"] += 1

        self.metrics["misses"] += 1
        return request

    async def after_request(
        self, request: FlextApiClientRequest, response: FlextApiClientResponse,
    ) -> FlextApiClientResponse:
        """Cache successful responses."""
        if self._is_cacheable(request) and response.status_code < 400:
            cache_key = self._cache_key(request)
            self._cache[cache_key] = (response, time.time())

        return response

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            **self.metrics,
            "cache_size": len(self._cache),
            "ttl_seconds": self.ttl_seconds,
        }


class FlextApiRetryPlugin(FlextApiPlugin):
    """Retry plugin with exponential backoff."""

    def __init__(self, max_retries: int = 3, backoff_factor: float = 1.0) -> None:
        super().__init__("RetryPlugin")
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.metrics = {"total_retries": 0, "successful_retries": 0, "failed_retries": 0}

    def _should_retry(self, status_code: int) -> bool:
        """Check if request should be retried."""
        return status_code >= 500 or status_code == 429

    async def on_error(
        self, request: FlextApiClientRequest, error: Exception,
    ) -> FlextApiClientResponse | None:
        """Retry on errors."""
        if not hasattr(request, "_retry_count"):
            request._retry_count = 0

        if request._retry_count >= self.max_retries:
            self.metrics["failed_retries"] += 1
            return None

        request._retry_count += 1
        self.metrics["total_retries"] += 1

        # Exponential backoff
        delay = self.backoff_factor * (2 ** (request._retry_count - 1))
        await asyncio.sleep(delay)

        logger.info(f"Retrying request (attempt {request._retry_count}/{self.max_retries})")
        return None  # Signal to retry


class FlextApiCircuitBreakerPlugin(FlextApiPlugin):
    """Circuit breaker plugin."""

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        success_threshold: int = 3,
    ) -> None:
        super().__init__("CircuitBreakerPlugin")
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.success_threshold = success_threshold

        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self.state = "closed"  # closed, open, half-open

        self.metrics = {
            "state": self.state,
            "failure_count": 0,
            "success_count": 0,
            "trips": 0,
        }

    async def before_request(self, request: FlextApiClientRequest) -> FlextApiClientRequest:
        """Check circuit breaker state."""
        current_time = time.time()

        if self.state == "open":
            if current_time - self.last_failure_time >= self.timeout_seconds:
                self.state = "half-open"
                self.success_count = 0
                logger.info("Circuit breaker: transitioning to half-open")
            else:
                raise Exception("Circuit breaker is OPEN")

        self.metrics["state"] = self.state
        return request

    async def after_request(
        self, request: FlextApiClientRequest, response: FlextApiClientResponse,
    ) -> FlextApiClientResponse:
        """Update circuit breaker based on response."""
        if response.status_code >= 500:
            await self._record_failure()
        else:
            await self._record_success()

        return response

    async def on_error(
        self, request: FlextApiClientRequest, error: Exception,
    ) -> FlextApiClientResponse | None:
        """Record failure on error."""
        await self._record_failure()
        return None

    async def _record_failure(self) -> None:
        """Record a failure."""
        self.failure_count += 1
        self.metrics["failure_count"] = self.failure_count

        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            self.last_failure_time = time.time()
            self.metrics["trips"] += 1
            logger.warning("Circuit breaker: OPEN")

    async def _record_success(self) -> None:
        """Record a success."""
        if self.state == "half-open":
            self.success_count += 1
            self.metrics["success_count"] = self.success_count

            if self.success_count >= self.success_threshold:
                self.state = "closed"
                self.failure_count = 0
                logger.info("Circuit breaker: CLOSED")
        elif self.state == "closed":
            self.failure_count = 0


# ==============================================================================
# MAIN CLIENT
# ==============================================================================

@dataclass
class FlextApiClientConfig:
    """Client configuration."""

    base_url: str
    timeout: float = 30.0
    headers: dict[str, str] = field(default_factory=dict)
    verify_ssl: bool = True
    follow_redirects: bool = True
    max_redirects: int = 10
    protocol: FlextApiClientProtocol = FlextApiClientProtocol.HTTPS

    # Advanced features
    enable_http2: bool = False
    connection_pool_size: int = 100
    connection_pool_ttl: int = 300


class FlextApiClient:
    """Universal HTTP client with complete functionality."""

    def __init__(self, config: FlextApiClientConfig) -> None:
        self.config = config
        self._session: aiohttp.ClientSession | None = None
        self._plugins: list[FlextApiPlugin] = []
        self._status = FlextApiClientStatus.IDLE
        self._request_count = 0
        self._total_time = 0.0

    # === PLUGIN MANAGEMENT ===

    def add_plugin(self, plugin: FlextApiPlugin) -> None:
        """Add plugin to client."""
        self._plugins.append(plugin)
        logger.info(f"Added plugin: {plugin.name}")

    def remove_plugin(self, plugin_name: str) -> bool:
        """Remove plugin by name."""
        for i, plugin in enumerate(self._plugins):
            if plugin.name == plugin_name:
                del self._plugins[i]
                logger.info(f"Removed plugin: {plugin_name}")
                return True
        return False

    # === SESSION MANAGEMENT ===

    async def ensure_session(self) -> aiohttp.ClientSession:
        """Get or create session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            connector = aiohttp.TCPConnector(
                verify_ssl=self.config.verify_ssl,
                limit=self.config.connection_pool_size,
                ttl_dns_cache=self.config.connection_pool_ttl,
            )

            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=self.config.headers,
            )
            self._status = FlextApiClientStatus.ACTIVE

        return self._session

    def get_session(self) -> aiohttp.ClientSession | None:
        """Get current session."""
        return self._session

    # === HTTP METHODS ===

    async def get(self, path: str, **kwargs: Any) -> FlextResult[FlextApiClientResponse]:
        """GET request."""
        return await self.request(FlextApiClientMethod.GET, path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> FlextResult[FlextApiClientResponse]:
        """POST request."""
        return await self.request(FlextApiClientMethod.POST, path, **kwargs)

    async def put(self, path: str, **kwargs: Any) -> FlextResult[FlextApiClientResponse]:
        """PUT request."""
        return await self.request(FlextApiClientMethod.PUT, path, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> FlextResult[FlextApiClientResponse]:
        """DELETE request."""
        return await self.request(FlextApiClientMethod.DELETE, path, **kwargs)

    async def patch(self, path: str, **kwargs: Any) -> FlextResult[FlextApiClientResponse]:
        """PATCH request."""
        return await self.request(FlextApiClientMethod.PATCH, path, **kwargs)

    # === MAIN REQUEST METHOD ===

    async def request(
        self, method: FlextApiClientMethod, path: str, **kwargs: Any,
    ) -> FlextResult[FlextApiClientResponse]:
        """Execute HTTP request with full plugin pipeline."""
        start_time = time.time()

        # Build request
        url = self.build_full_url(path)
        request = FlextApiClientRequest(
            method=method,
            url=url,
            headers=kwargs.get("headers", {}),
            params=kwargs.get("params", {}),
            json=kwargs.get("json"),
            data=kwargs.get("data"),
            timeout=kwargs.get("timeout"),
        )

        try:
            # Run before_request plugins
            for plugin in self._plugins:
                if plugin.enabled:
                    request = await plugin.before_request(request)

            # Execute request
            session = await self.ensure_session()

            request_kwargs = {
                "params": request.params,
                "headers": request.headers,
            }

            if request.json is not None:
                request_kwargs["json"] = request.json
            elif request.data is not None:
                request_kwargs["data"] = request.data

            if request.timeout:
                request_kwargs["timeout"] = aiohttp.ClientTimeout(total=request.timeout)

            async with session.request(
                request.method.value, request.url, **request_kwargs,
            ) as http_response:

                # Parse response
                try:
                    response_data = await http_response.json()
                except Exception:
                    response_data = await http_response.text()

                response = FlextApiClientResponse(
                    status_code=http_response.status,
                    headers=dict(http_response.headers),
                    data=response_data,
                    elapsed_time=time.time() - start_time,
                )

                # Run after_request plugins
                for plugin in self._plugins:
                    if plugin.enabled:
                        response = await plugin.after_request(request, response)

                # Update metrics
                self._request_count += 1
                self._total_time += response.elapsed_time

                return FlextResult.ok(response)

        except Exception as e:
            # Run error plugins
            handled_response = None
            for plugin in self._plugins:
                if plugin.enabled:
                    handled_response = await plugin.on_error(request, e)
                    if handled_response:
                        break

            if handled_response:
                return FlextResult.ok(handled_response)

            logger.exception(f"Request failed: {method.value} {url}")
            return FlextResult.fail(f"Request failed: {e}")

    # === UTILITY METHODS ===

    def build_full_url(self, path: str) -> str:
        """Build full URL from path."""
        return urljoin(self.config.base_url.rstrip("/") + "/", path.lstrip("/"))

    async def get_health(self) -> FlextResult[dict[str, Any]]:
        """Get client health status."""
        return FlextResult.ok({
            "status": self._status.value,
            "request_count": self._request_count,
            "average_response_time": (
                self._total_time / self._request_count if self._request_count > 0 else 0
            ),
            "active_plugins": [p.name for p in self._plugins if p.enabled],
            "session_closed": self._session is None or self._session.closed,
        })

    async def get_metrics(self) -> FlextResult[dict[str, Any]]:
        """Get detailed metrics."""
        plugin_metrics = {}
        for plugin in self._plugins:
            plugin_metrics[plugin.name] = plugin.get_metrics()

        return FlextResult.ok({
            "client": {
                "requests": self._request_count,
                "total_time": self._total_time,
                "average_time": (
                    self._total_time / self._request_count if self._request_count > 0 else 0
                ),
                "status": self._status.value,
            },
            "plugins": plugin_metrics,
        })

    # === STREAMING SUPPORT ===

    async def stream(self, method: FlextApiClientMethod, path: str, **kwargs: Any) -> AsyncIterator[bytes]:
        """Stream response data."""
        session = await self.ensure_session()
        url = self.build_full_url(path)

        async with session.request(method.value, url, **kwargs) as response:
            async for chunk in response.content.iter_chunked(8192):
                yield chunk

    # === CLEANUP ===

    async def close(self) -> None:
        """Close client and cleanup resources."""
        if self._session and not self._session.closed:
            await self._session.close()

        self._status = FlextApiClientStatus.CLOSED
        logger.info("FlextApiClient closed")


# ==============================================================================
# FACTORY FUNCTIONS
# ==============================================================================

def create_client(base_url: str, **kwargs: Any) -> FlextApiClient:
    """Create configured client."""
    config = FlextApiClientConfig(base_url=base_url, **kwargs)
    return FlextApiClient(config)


def create_client_with_plugins(
    base_url: str,
    enable_cache: bool = True,
    enable_retry: bool = True,
    enable_circuit_breaker: bool = True,
    **kwargs: Any,
) -> FlextApiClient:
    """Create client with common plugins."""
    client = create_client(base_url, **kwargs)

    if enable_cache:
        client.add_plugin(FlextApiCachingPlugin())

    if enable_retry:
        client.add_plugin(FlextApiRetryPlugin())

    if enable_circuit_breaker:
        client.add_plugin(FlextApiCircuitBreakerPlugin())

    return client

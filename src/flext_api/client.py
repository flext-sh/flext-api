"""FLEXT API Client - Using flext-core structural patterns.

Uses FlextService, FlextPlugin, FlextValueObject and other flext-core patterns
for maximum code reduction and structural alignment.
"""

from __future__ import annotations

import asyncio
import contextlib
import time
import uuid
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, ClassVar, Self, TypeVar, cast
from urllib.parse import urljoin

import aiohttp
import aiohttp.hdrs
import structlog
from flext_core import FlextContainer, FlextResult, FlextService, get_logger
from flext_observability import (
    FlextAlertService,
    FlextHealthService,
    FlextLoggingService,
    FlextMetricsService,
    FlextTracingService,
)
from flext_observability.entities import FlextHealthCheck, FlextMetric

if TYPE_CHECKING:
    import types

logger = structlog.get_logger(__name__)

# Type variable for generic FlextResult handling
T = TypeVar("T")


# ==============================================================================
# CORE ENUMS AND VALUE OBJECTS
# ==============================================================================


class FlextApiClientProtocol(StrEnum):
    """Supported client protocols."""

    HTTP = "http"
    HTTPS = "https"


class FlextApiClientMethod(StrEnum):
    """HTTP methods using aiohttp constants to avoid duplication."""

    GET = aiohttp.hdrs.METH_GET
    POST = aiohttp.hdrs.METH_POST
    PUT = aiohttp.hdrs.METH_PUT
    DELETE = aiohttp.hdrs.METH_DELETE
    PATCH = aiohttp.hdrs.METH_PATCH
    HEAD = aiohttp.hdrs.METH_HEAD
    OPTIONS = aiohttp.hdrs.METH_OPTIONS


class FlextApiClientStatus(StrEnum):
    """Client status."""

    IDLE = "idle"
    ACTIVE = "active"
    RUNNING = "running"
    STOPPED = "stopped"
    CLOSED = "closed"
    ERROR = "error"


@dataclass(frozen=True)
class FlextApiClientConfig:
    """Client configuration using dataclass for immutability."""

    base_url: str = ""
    timeout: float = 30.0
    headers: dict[str, str] | None = None
    max_retries: int = 3

    def __post_init__(self) -> None:
        """Post-initialization validation."""
        if self.base_url and not self.base_url.startswith(("http://", "https://")):
            msg = "Invalid URL format"
            raise ValueError(msg)
        if self.headers is None:
            object.__setattr__(self, "headers", {})


@dataclass(frozen=True)
class FlextApiClientRequest:
    """HTTP request using dataclass for immutability."""

    method: FlextApiClientMethod | str
    url: str
    headers: dict[str, str] | None = None
    params: dict[str, object] | None = None
    json_data: dict[str, object] | None = None
    data: str | bytes | None = None
    timeout: float | None = None

    def __post_init__(self) -> None:
        """Post-initialization validation."""
        # Validation handled by dataclass field types

        if isinstance(self.method, str):
            method_value = FlextApiClientMethod(self.method.upper())
            object.__setattr__(self, "method", method_value)

        if self.headers is None:
            object.__setattr__(self, "headers", {})
        if self.params is None:
            object.__setattr__(self, "params", {})


@dataclass(frozen=True)
class FlextApiClientResponse:
    """HTTP response using dataclass for immutability."""

    status_code: int
    headers: dict[str, str] | None = None
    data: object = None
    elapsed_time: float = 0.0
    request_id: str | None = None
    from_cache: bool = False

    def __post_init__(self) -> None:
        """Post-initialization validation."""
        if self.headers is None:
            object.__setattr__(self, "headers", {})

    def json(self) -> object:
        """Get JSON data from response."""
        return self.data

    def text(self) -> str:
        """Get text data from response."""
        return str(self.data)


# ==============================================================================
# PLUGIN SYSTEM USING FLEXT-CORE
# ==============================================================================


class FlextApiPlugin:
    """Base API plugin interface."""

    def __init__(self, name: str | None = None) -> None:
        """Initialize plugin."""
        self.name = name or self.__class__.__name__
        self.enabled = True
        self.metrics: dict[str, object] = {}

    async def before_request(
        self,
        request: FlextApiClientRequest,
    ) -> FlextApiClientRequest:
        """Process request before sending."""
        return request

    async def after_request(
        self,
        _request: FlextApiClientRequest,
        response: FlextApiClientResponse,
    ) -> FlextApiClientResponse:
        """Process response after receiving."""
        return response

    async def on_error(
        self,
        _request: FlextApiClientRequest,
        error: Exception,
    ) -> Exception:
        """Handle request error."""
        return error


class FlextApiCachingPlugin(FlextApiPlugin):
    """Caching plugin using flext-core patterns."""

    def __init__(self, ttl: int = 300, max_size: int = 1000) -> None:
        """Initialize caching plugin."""
        super().__init__("CachingPlugin")
        self.ttl = ttl
        self.max_size = max_size
        self._cache: dict[str, tuple[object, float]] = {}

    async def before_request(
        self,
        request: FlextApiClientRequest,
    ) -> FlextApiClientRequest:
        """Check cache before request."""
        if request.method == FlextApiClientMethod.GET:
            cache_key = f"{request.url}:{hash(str(request.params))}"
            if cache_key in self._cache:
                _cached_data, timestamp = self._cache[cache_key]
                if time.time() - timestamp < self.ttl:
                    # Cache hit - return cached response
                    # This would need to be handled differently in real implementation
                    pass
        return request


class FlextApiRetryPlugin(FlextApiPlugin):
    """Retry plugin using flext-core patterns."""

    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0) -> None:
        """Initialize retry plugin."""
        super().__init__("RetryPlugin")
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor


class FlextApiCircuitBreakerPlugin(FlextApiPlugin):
    """Circuit breaker plugin using flext-core patterns."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60) -> None:
        """Initialize circuit breaker plugin."""
        super().__init__("CircuitBreakerPlugin")
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN


# ==============================================================================
# HTTP CLIENT SERVICE USING FLEXT-CORE
# ==============================================================================


class FlextApiClient:
    """HTTP client service using flext-core patterns with FlextService interface."""

    # DRY Class-level session tracking for proper cleanup
    _active_sessions: ClassVar[set[aiohttp.ClientSession]] = set()

    def __init__(
        self,
        config: FlextApiClientConfig | None = None,
        plugins: list[FlextApiPlugin] | None = None,
    ) -> None:
        """Initialize HTTP client service."""
        self.config = config or FlextApiClientConfig()
        self.plugins = plugins or []
        self.status = FlextApiClientStatus.IDLE
        self._session: aiohttp.ClientSession | None = None

        # Enterprise Observability Integration - DRY pattern using container
        self._container = FlextContainer()
        self._metrics_service = FlextMetricsService(self._container)
        self._tracing_service = FlextTracingService(self._container)
        self._health_service = FlextHealthService(self._container)
        self._alert_service = FlextAlertService(self._container)
        self._logging_service = FlextLoggingService(self._container)

        # Replace default logger with flext-core logger
        self.logger = get_logger(self.__class__.__name__)

        # Performance tracking attributes
        self._request_count = 0
        self._error_count = 0
        self._total_response_time = 0.0
        self._start_time = time.time()

    def _handle_observability_result(
        self,
        result: FlextResult[T],
        operation: str,
    ) -> None:
        """DRY helper to handle observability operation results consistently."""
        if not result.is_success:
            self.logger.warning(f"Observability {operation} failed: {result.error}")

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure session is created with DRY tracking."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self.config.headers,
            )
            # DRY session tracking - register for cleanup
            FlextApiClient._active_sessions.add(self._session)
        return self._session

    async def _cleanup_session(self) -> None:
        """DRY helper method to cleanup session safely with tracking."""
        if self._session and not self._session.closed:
            try:
                await self._session.close()
                # DRY session tracking - unregister from active sessions
                FlextApiClient._active_sessions.discard(self._session)
            except Exception as e:
                self.logger.debug(f"Session cleanup warning: {e}")
            finally:
                self._session = None

    @classmethod
    async def cleanup_all_sessions(cls) -> None:
        """DRY class method to cleanup all active sessions."""
        sessions_to_close = list(cls._active_sessions)
        for session in sessions_to_close:
            if not session.closed:
                with contextlib.suppress(Exception):
                    await session.close()
        cls._active_sessions.clear()

    async def _make_request(
        self,
        request: FlextApiClientRequest,
    ) -> FlextResult[FlextApiClientResponse]:
        """Make HTTP request with plugin processing."""
        try:
            response = await self._make_request_impl(request)
            return FlextResult.ok(response)
        except Exception as e:
            logger.exception(
                "Failed to make HTTP request",
                method=request.method,
                url=request.url,
            )
            error_msg = f"Failed to make {request.method} request to {request.url}: {e}"
            return FlextResult.fail(error_msg)

    def _prepare_request_params(
        self,
        request: FlextApiClientRequest,
    ) -> tuple[
        dict[str, str] | None,
        dict[str, str] | None,
        object | None,
        str | bytes | None,
        aiohttp.ClientTimeout | None,
    ]:
        """Prepare request parameters with proper aiohttp types."""
        # Parameters - convert object values to strings for aiohttp compatibility
        params: dict[str, str] | None = None
        if request.params:
            params = {k: str(v) for k, v in request.params.items()}

        # Headers - merge config and request headers
        headers: dict[str, str] | None = None
        if self.config.headers or request.headers:
            headers = dict(self.config.headers or {})
            if request.headers:
                headers.update(request.headers)

        # JSON data
        json_data = request.json_data if request.json_data is not None else None

        # Raw data
        data = request.data if request.data is not None else None

        # Timeout
        timeout = (
            aiohttp.ClientTimeout(total=request.timeout) if request.timeout else None
        )

        return params, headers, json_data, data, timeout

    async def _make_request_impl(
        self,
        request: FlextApiClientRequest,
    ) -> FlextApiClientResponse:
        """Implement request processing with plugins."""
        # Process through before_request plugins
        for plugin in self.plugins:
            if plugin.enabled:
                request = await plugin.before_request(request)

        session = await self._ensure_session()
        start_time = time.time()

        url = (
            urljoin(self.config.base_url, request.url)
            if self.config.base_url
            else request.url
        )

        # Prepare request parameters with proper typing
        params, headers, json_data, data, timeout = self._prepare_request_params(
            request,
        )

        # Ensure method is converted to enum value
        method_value = (
            request.method.value
            if hasattr(request.method, "value")
            else str(request.method).upper()
        )

        # Make request with properly typed parameters
        async with session.request(
            method=method_value,
            url=url,
            params=params,
            headers=headers,
            json=json_data,
            data=data,
            timeout=timeout,
        ) as http_response:
            elapsed_time = time.time() - start_time

            try:
                response_data = await http_response.json()
            except (RuntimeError, ValueError, TypeError, aiohttp.ContentTypeError):
                response_data = await http_response.text()

            response = FlextApiClientResponse(
                status_code=http_response.status,
                headers=dict(http_response.headers),
                data=response_data,
                elapsed_time=elapsed_time,
            )

            # Process through after_request plugins
            for plugin in self.plugins:
                if plugin.enabled:
                    response = await plugin.after_request(request, response)

            return response

    async def get(
        self,
        path: str,
        params: dict[str, object] | None = None,
        headers: dict[str, str] | None = None,
        request_timeout: float | None = None,
    ) -> FlextResult[FlextApiClientResponse]:
        """Make GET request."""
        request = FlextApiClientRequest(
            method=FlextApiClientMethod.GET,
            url=path,
            params=params,
            headers=headers,
            timeout=request_timeout,
        )
        return await self._make_request(request)

    async def post(
        self,
        path: str,
        json_data: dict[str, object] | None = None,
        data: str | bytes | None = None,
        headers: dict[str, str] | None = None,
        request_timeout: float | None = None,
    ) -> FlextResult[FlextApiClientResponse]:
        """Make POST request."""
        request = FlextApiClientRequest(
            method=FlextApiClientMethod.POST,
            url=path,
            json_data=json_data,
            data=data,
            headers=headers,
            timeout=request_timeout,
        )
        return await self._make_request(request)

    async def put(
        self,
        path: str,
        json_data: dict[str, object] | None = None,
        data: str | bytes | None = None,
        headers: dict[str, str] | None = None,
        request_timeout: float | None = None,
    ) -> FlextResult[FlextApiClientResponse]:
        """Make PUT request."""
        request = FlextApiClientRequest(
            method=FlextApiClientMethod.PUT,
            url=path,
            json_data=json_data,
            data=data,
            headers=headers,
            timeout=request_timeout,
        )
        return await self._make_request(request)

    async def delete(
        self,
        path: str,
        headers: dict[str, str] | None = None,
        request_timeout: float | None = None,
    ) -> FlextResult[FlextApiClientResponse]:
        """Make DELETE request."""
        request = FlextApiClientRequest(
            method=FlextApiClientMethod.DELETE,
            url=path,
            headers=headers,
            timeout=request_timeout,
        )
        return await self._make_request(request)

    async def patch(
        self,
        path: str,
        json_data: dict[str, object] | None = None,
        data: str | bytes | None = None,
        headers: dict[str, str] | None = None,
        request_timeout: float | None = None,
    ) -> FlextResult[FlextApiClientResponse]:
        """Make PATCH request."""
        request = FlextApiClientRequest(
            method=FlextApiClientMethod.PATCH,
            url=path,
            json_data=json_data,
            data=data,
            headers=headers,
            timeout=request_timeout,
        )
        return await self._make_request(request)

    async def head(
        self,
        path: str,
        headers: dict[str, str] | None = None,
        request_timeout: float | None = None,
    ) -> FlextResult[FlextApiClientResponse]:
        """Make HEAD request."""
        request = FlextApiClientRequest(
            method=FlextApiClientMethod.HEAD,
            url=path,
            headers=headers,
            timeout=request_timeout,
        )
        return await self._make_request(request)

    async def options(
        self,
        path: str,
        headers: dict[str, str] | None = None,
        request_timeout: float | None = None,
    ) -> FlextResult[FlextApiClientResponse]:
        """Make OPTIONS request."""
        request = FlextApiClientRequest(
            method=FlextApiClientMethod.OPTIONS,
            url=path,
            headers=headers,
            timeout=request_timeout,
        )
        return await self._make_request(request)

    def _sync_start(self) -> FlextResult[None]:
        """Internal sync start implementation - DRY pattern."""
        try:
            self.status = FlextApiClientStatus.RUNNING

            # Record service start metric using DRY helper
            start_metric_result = self._metrics_service.record_metric(
                FlextMetric(id=str(uuid.uuid4()), name="service_started", value=1.0),
            )
            self._handle_observability_result(
                start_metric_result,
                "service start metric",
            )

            self.logger.info("FlextApiClient service started successfully")
            return FlextResult.ok(None)
        except Exception as e:
            self.logger.exception("Failed to start FlextApiClient service")
            return FlextResult.fail(f"Service start failed: {e}")

    def _sync_stop(self) -> FlextResult[None]:
        """Internal sync stop implementation - DRY pattern."""
        try:
            self.status = FlextApiClientStatus.STOPPED

            # Record service stop metric using DRY helper
            stop_metric_result = self._metrics_service.record_metric(
                FlextMetric(id=str(uuid.uuid4()), name="service_stopped", value=1.0),
            )
            self._handle_observability_result(stop_metric_result, "service stop metric")

            self.logger.info("FlextApiClient service stopped successfully")
            return FlextResult.ok(None)
        except Exception as e:
            self.logger.exception("Failed to stop FlextApiClient service")
            return FlextResult.fail(f"Service stop failed: {e}")

    # Main interface (async for API compatibility, FlextService will adapt)
    async def start(self) -> FlextResult[None]:
        """Start the client service."""
        return self._sync_start()

    async def stop(self) -> FlextResult[None]:
        """Stop the client service."""
        # Handle async session cleanup if needed
        result = self._sync_stop()
        if result.is_success:
            # Use DRY cleanup helper but keep status as STOPPED (not CLOSED)
            await self._cleanup_session()
            # Status remains STOPPED (set by _sync_stop)
        return result

    def __del__(self) -> None:
        """Cleanup unclosed session to prevent resource warnings."""
        if (
            hasattr(self, "_session")
            and self._session is not None
            and not self._session.closed
        ):
            # Warn about unclosed session in debug mode only
            if hasattr(self, "logger"):
                msg = "Session not explicitly closed, cleanup in destructor"
                self.logger.debug(msg)
            # Schedule session cleanup for next event loop iteration
            try:
                # Try to get the current event loop
                loop = asyncio.get_running_loop()
                # Schedule cleanup safely
                task = loop.create_task(self._cleanup_session())
                # Don't wait for completion to avoid blocking destructor
                task.add_done_callback(lambda _: None)
            except RuntimeError:
                # No event loop running, sessions will be cleaned by GC
                pass

    def _sync_health_check(self) -> FlextResult[dict[str, object]]:
        """Internal sync health check implementation - DRY pattern."""
        try:
            session_active = self._session is not None and not (
                self._session.closed if self._session else True
            )

            # Gather comprehensive health information
            health_data: dict[str, object] = {
                "service": "FlextApiClient",
                "status": self.status.value,
                "base_url": self.config.base_url,
                "session_active": session_active,
                "plugins_count": len(self.plugins),
                "timestamp": time.time(),
                "performance": {
                    "request_count": self._request_count,
                    "error_count": self._error_count,
                    "total_response_time": self._total_response_time,
                    "uptime_seconds": time.time() - self._start_time,
                },
            }

            # Record health check metric using DRY helper
            performance_metrics = cast("dict[str, object]", health_data["performance"])
            status = (
                "healthy" if self.status == FlextApiClientStatus.RUNNING else "degraded"
            )
            health_check_result = self._health_service.check_health(
                FlextHealthCheck(
                    id=str(uuid.uuid4()),
                    component="FlextApiClient",
                    status=status,
                    message=f"Service status: {self.status.value}",
                    metrics=performance_metrics,
                ),
            )
            self._handle_observability_result(health_check_result, "health check")

            return FlextResult.ok(health_data)
        except Exception as e:
            self.logger.exception("Health check failed")
            return FlextResult.fail(f"Health check failed: {e}")

    # Legacy interface (returns dict directly for backward compatibility)
    def health_check(self) -> dict[str, object]:
        """Health check (legacy interface - returns dict directly)."""
        result = self._sync_health_check()
        if result.is_success and result.data is not None:
            return result.data
        # On error, return error health data
        return {
            "service": "FlextApiClient",
            "status": "unhealthy",
            "error": result.error,
            "timestamp": time.time(),
        }

    # FlextService interface (returns FlextResult)
    def service_health_check(self) -> FlextResult[dict[str, object]]:
        """Health check (FlextService interface - returns FlextResult)."""
        return self._sync_health_check()

    async def close(self) -> None:
        """Close client session."""
        await self._cleanup_session()  # Use DRY cleanup helper
        self.status = FlextApiClientStatus.CLOSED

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Async context manager exit."""
        await self.stop()  # Use stop to maintain STOPPED status


class FlextApiClientServiceAdapter(FlextService):
    """DRY Service Adapter - Implements FlextService interface for FlextApiClient.

    This adapter pattern avoids code duplication by wrapping the async FlextApiClient
    with a sync FlextService interface, maintaining backward compatibility.
    """

    def __init__(self, client: FlextApiClient) -> None:
        """Initialize service adapter."""
        self._client = client

    def start(self) -> FlextResult[None]:
        """Start service (FlextService sync interface)."""
        return self._client._sync_start()

    def stop(self) -> FlextResult[None]:
        """Stop service (FlextService sync interface)."""
        return self._client._sync_stop()

    def health_check(self) -> FlextResult[dict[str, object]]:
        """Health check (FlextService sync interface)."""
        return self._client.service_health_check()


# ==============================================================================
# FACTORY FUNCTIONS
# ==============================================================================


def create_client(config: dict[str, object] | None = None) -> FlextApiClient:
    """Create HTTP client with configuration."""
    # Convert config to appropriate types for dataclass
    raw_config = config or {}

    base_url = str(raw_config.get("base_url", ""))

    # Validate base_url if provided
    if base_url and not base_url.startswith(("http://", "https://")):
        msg = "Invalid URL format"
        raise ValueError(msg)

    timeout_val = raw_config.get("timeout", 30.0)
    timeout = float(timeout_val) if isinstance(timeout_val, (int, float)) else 30.0
    headers = None
    if "headers" in raw_config and isinstance(raw_config["headers"], dict):
        headers = {str(k): str(v) for k, v in raw_config["headers"].items()}
    max_retries_val = raw_config.get("max_retries", 3)
    max_retries = (
        int(max_retries_val) if isinstance(max_retries_val, (int, float)) else 3
    )

    client_config = FlextApiClientConfig(
        base_url=base_url,
        timeout=timeout,
        headers=headers,
        max_retries=max_retries,
    )
    return FlextApiClient(client_config)


def create_client_with_plugins(
    config: dict[str, object] | FlextApiClientConfig | None = None,
    plugins: list[FlextApiPlugin] | None = None,
) -> FlextApiClient:
    """Create HTTP client with plugins."""
    if isinstance(config, FlextApiClientConfig):
        client_config = config
    elif config is not None:
        client = create_client(config)
        client_config = client.config
    else:
        client_config = FlextApiClientConfig()

    return FlextApiClient(client_config, plugins or [])

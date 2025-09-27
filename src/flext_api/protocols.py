"""Protocol definitions for flext-api domain.

All protocol interfaces are centralized here for better type safety and dependency inversion.
Following FLEXT standards: protocols only, no implementations.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_core import FlextProtocols, FlextResult

from .typings import FlextApiTypes


class FlextApiProtocols(FlextProtocols):
    """Single unified API protocols class following FLEXT standards.

    Contains all protocol definitions for API domain operations.
    Follows FLEXT pattern: one class per module with nested subclasses.
    """

    @runtime_checkable
    class HttpClientProtocol(Protocol):
        """Protocol for HTTP client implementations."""

        def request(
            self,
            method: FlextApiTypes.HttpMethod,
            url: str,
            headers: FlextApiTypes.HttpHeaders | None = None,
            params: FlextApiTypes.HttpParams | None = None,
            data: FlextApiTypes.HttpData | None = None,
            timeout: FlextApiTypes.TimeoutSeconds | None = None,
        ) -> FlextResult[FlextApiTypes.ResponseData]:
            """Execute an HTTP request."""
            ...

        def get(
            self,
            url: str,
            headers: FlextApiTypes.HttpHeaders | None = None,
            params: FlextApiTypes.HttpParams | None = None,
            timeout: FlextApiTypes.TimeoutSeconds | None = None,
        ) -> FlextResult[FlextApiTypes.ResponseData]:
            """Execute HTTP GET request."""
            ...

        def post(
            self,
            url: str,
            data: FlextApiTypes.HttpData | None = None,
            headers: FlextApiTypes.HttpHeaders | None = None,
            timeout: FlextApiTypes.TimeoutSeconds | None = None,
        ) -> FlextResult[FlextApiTypes.ResponseData]:
            """Execute HTTP POST request."""
            ...

        def put(
            self,
            url: str,
            data: FlextApiTypes.HttpData | None = None,
            headers: FlextApiTypes.HttpHeaders | None = None,
            timeout: FlextApiTypes.TimeoutSeconds | None = None,
        ) -> FlextResult[FlextApiTypes.ResponseData]:
            """Execute HTTP PUT request."""
            ...

        def delete(
            self,
            url: str,
            headers: FlextApiTypes.HttpHeaders | None = None,
            timeout: FlextApiTypes.TimeoutSeconds | None = None,
        ) -> FlextResult[FlextApiTypes.ResponseData]:
            """Execute HTTP DELETE request."""
            ...

    @runtime_checkable
    class StorageBackendProtocol(Protocol):
        """Protocol for storage backend implementations."""

        def get(
            self, key: FlextApiTypes.StorageKey
        ) -> FlextResult[FlextApiTypes.StorageValue | None]:
            """Retrieve value by key."""
            ...

        def set(
            self,
            key: FlextApiTypes.StorageKey,
            value: FlextApiTypes.StorageValue,
            timeout: int | None = None,
        ) -> FlextResult[bool]:
            """Store value with optional timeout."""
            ...

        def delete(self, key: FlextApiTypes.StorageKey) -> FlextResult[bool]:
            """Delete value by key."""
            ...

        def exists(self, key: FlextApiTypes.StorageKey) -> FlextResult[bool]:
            """Check if key exists."""
            ...

        def clear(self: object) -> FlextResult[bool]:
            """Clear all stored values."""
            ...

        def keys(self: object) -> FlextResult[list[FlextApiTypes.StorageKey]]:
            """Get all keys."""
            ...

    @runtime_checkable
    class RetryStrategyProtocol(Protocol):
        """Protocol for retry strategy implementations."""

        def should_retry(
            self,
            attempt: int,
            exception: Exception,
            status_code: FlextApiTypes.HttpStatusCode | None = None,
        ) -> bool:
            """Determine if operation should be retried."""
            ...

        def get_delay(self, attempt: int) -> float:
            """Get delay before next retry attempt."""
            ...

        def get_max_attempts(self: object) -> int:
            """Get maximum number of retry attempts."""
            ...

    @runtime_checkable
    class ConnectionManagerProtocol(Protocol):
        """Protocol for connection manager implementations."""

        def get_connection(self: object) -> FlextResult[object]:
            """Get active connection."""
            ...

        def release_connection(self, connection: object) -> FlextResult[bool]:
            """Release connection back to pool."""
            ...

        def close_all(self: object) -> FlextResult[bool]:
            """Close all connections."""
            ...

        def is_healthy(self: object) -> FlextResult[bool]:
            """Check if connection manager is healthy."""
            ...

    @runtime_checkable
    class CacheProtocol(Protocol):
        """Protocol for cache implementations."""

        def get(self, key: str) -> FlextResult[object | None]:
            """Get cached value."""
            ...

        def set(
            self, key: str, value: object, ttl: int | None = None
        ) -> FlextResult[bool]:
            """Set cached value with optional TTL."""
            ...

        def invalidate(self, key: str) -> FlextResult[bool]:
            """Invalidate cache entry."""
            ...

        def clear(self: object) -> FlextResult[bool]:
            """Clear all cache entries."""
            ...

    @runtime_checkable
    class RequestValidatorProtocol(Protocol):
        """Protocol for request validation implementations."""

        def validate_request(
            self, request_data: FlextApiTypes.RequestData
        ) -> FlextResult[FlextApiTypes.RequestData]:
            """Validate and sanitize request data."""
            ...

        def validate_headers(
            self, headers: FlextApiTypes.HttpHeaders
        ) -> FlextResult[FlextApiTypes.HttpHeaders]:
            """Validate HTTP headers."""
            ...

        def validate_params(
            self, params: FlextApiTypes.HttpParams
        ) -> FlextResult[FlextApiTypes.HttpParams]:
            """Validate query parameters."""
            ...

    @runtime_checkable
    class ResponseProcessorProtocol(Protocol):
        """Protocol for response processing implementations."""

        def process_response(
            self,
            response_data: FlextApiTypes.ResponseData,
            status_code: FlextApiTypes.HttpStatusCode,
        ) -> FlextResult[FlextApiTypes.ResponseData]:
            """Process and transform response data."""
            ...

        def handle_error_response(
            self,
            response_data: FlextApiTypes.ResponseData,
            status_code: FlextApiTypes.HttpStatusCode,
        ) -> FlextResult[Exception]:
            """Handle error responses and create appropriate exceptions."""
            ...

    @runtime_checkable
    class AuthenticationProviderProtocol(Protocol):
        """Protocol for authentication provider implementations."""

        def get_auth_headers(self: object) -> FlextResult[FlextApiTypes.HttpHeaders]:
            """Get authentication headers for requests."""
            ...

        def is_authenticated(self: object) -> FlextResult[bool]:
            """Check if currently authenticated."""
            ...

        def refresh_auth(self: object) -> FlextResult[bool]:
            """Refresh authentication credentials."""
            ...

    @runtime_checkable
    class MetricsCollectorProtocol(Protocol):
        """Protocol for metrics collection implementations."""

        def record_request(
            self,
            method: FlextApiTypes.HttpMethod,
            url: str,
            status_code: FlextApiTypes.HttpStatusCode,
            duration_ms: float,
        ) -> FlextResult[bool]:
            """Record request metrics."""
            ...

        def record_error(
            self, error: Exception, context: FlextApiTypes.JsonObject
        ) -> FlextResult[bool]:
            """Record error metrics."""
            ...

        def get_metrics(self: object) -> FlextResult[FlextApiTypes.JsonObject]:
            """Get collected metrics."""
            ...

    @runtime_checkable
    class MiddlewareProtocol(Protocol):
        """Protocol for middleware implementations."""

        async def process_request(
            self, request: FlextApiTypes.RequestData
        ) -> FlextResult[FlextApiTypes.RequestData]:
            """Process incoming request."""
            ...

        async def process_response(
            self, response: FlextApiTypes.ResponseData
        ) -> FlextResult[FlextApiTypes.ResponseData]:
            """Process outgoing response."""
            ...

    @runtime_checkable
    class PluginProtocol(Protocol):
        """Protocol for plugin implementations."""

        def initialize(self, config: FlextApiTypes.JsonObject) -> FlextResult[bool]:
            """Initialize plugin with configuration."""
            ...

        def is_enabled(self: object) -> bool:
            """Check if plugin is enabled."""
            ...

        def get_name(self: object) -> str:
            """Get plugin name."""
            ...

        def get_version(self: object) -> str:
            """Get plugin version."""
            ...

    @runtime_checkable
    class ConfigurationProviderProtocol(Protocol):
        """Protocol for configuration provider implementations."""

        def get_config(self, key: str) -> FlextResult[object]:
            """Get configuration value by key."""
            ...

        def set_config(self, key: str, value: object) -> FlextResult[bool]:
            """Set configuration value."""
            ...

        def reload_config(self: object) -> FlextResult[bool]:
            """Reload configuration from source."""
            ...

    @runtime_checkable
    class LoggerProtocol(Protocol):
        """Protocol for logger implementations."""

        def info(self, message: str, **kwargs: object) -> None:
            """Log info message."""
            ...

        def error(self, message: str, **kwargs: object) -> None:
            """Log error message."""
            ...

        def debug(self, message: str, **kwargs: object) -> None:
            """Log debug message."""
            ...

        def warning(self, message: str, **kwargs: object) -> None:
            """Log warning message."""
            ...


__all__ = [
    "FlextApiProtocols",
]

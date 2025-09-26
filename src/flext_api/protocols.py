"""Protocol definitions for flext-api domain.

All protocol interfaces are centralized here for better type safety and dependency inversion.
Following FLEXT standards: protocols only, no implementations.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_core import FlextProtocols, FlextResult

from .typings import FlextApiTypings

HttpData = FlextApiTypings.HttpData
HttpHeaders = FlextApiTypings.HttpHeaders
HttpMethod = FlextApiTypings.HttpMethod
HttpParams = FlextApiTypings.HttpParams
HttpStatusCode = FlextApiTypings.HttpStatusCode
JsonObject = FlextApiTypings.JsonObject
RequestData = FlextApiTypings.RequestData
ResponseData = FlextApiTypings.ResponseData
StorageKey = FlextApiTypings.StorageKey
StorageValue = FlextApiTypings.StorageValue
TimeoutSeconds = FlextApiTypings.TimeoutSeconds


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
            method: HttpMethod,
            url: str,
            headers: HttpHeaders | None = None,
            params: HttpParams | None = None,
            data: HttpData | None = None,
            timeout: TimeoutSeconds | None = None,
        ) -> FlextResult[ResponseData]:
            """Execute an HTTP request."""
            ...

        def get(
            self,
            url: str,
            headers: HttpHeaders | None = None,
            params: HttpParams | None = None,
            timeout: TimeoutSeconds | None = None,
        ) -> FlextResult[ResponseData]:
            """Execute HTTP GET request."""
            ...

        def post(
            self,
            url: str,
            data: HttpData | None = None,
            headers: HttpHeaders | None = None,
            timeout: TimeoutSeconds | None = None,
        ) -> FlextResult[ResponseData]:
            """Execute HTTP POST request."""
            ...

        def put(
            self,
            url: str,
            data: HttpData | None = None,
            headers: HttpHeaders | None = None,
            timeout: TimeoutSeconds | None = None,
        ) -> FlextResult[ResponseData]:
            """Execute HTTP PUT request."""
            ...

        def delete(
            self,
            url: str,
            headers: HttpHeaders | None = None,
            timeout: TimeoutSeconds | None = None,
        ) -> FlextResult[ResponseData]:
            """Execute HTTP DELETE request."""
            ...

    @runtime_checkable
    class StorageBackendProtocol(Protocol):
        """Protocol for storage backend implementations."""

        def get(self, key: StorageKey) -> FlextResult[StorageValue | None]:
            """Retrieve value by key."""
            ...

        def set(
            self, key: StorageKey, value: StorageValue, timeout: int | None = None
        ) -> FlextResult[bool]:
            """Store value with optional timeout."""
            ...

        def delete(self, key: StorageKey) -> FlextResult[bool]:
            """Delete value by key."""
            ...

        def exists(self, key: StorageKey) -> FlextResult[bool]:
            """Check if key exists."""
            ...

        def clear(self: object) -> FlextResult[bool]:
            """Clear all stored values."""
            ...

        def keys(self: object) -> FlextResult[list[StorageKey]]:
            """Get all keys."""
            ...

    @runtime_checkable
    class RetryStrategyProtocol(Protocol):
        """Protocol for retry strategy implementations."""

        def should_retry(
            self,
            attempt: int,
            exception: Exception,
            status_code: HttpStatusCode | None = None,
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
            self, request_data: RequestData
        ) -> FlextResult[RequestData]:
            """Validate and sanitize request data."""
            ...

        def validate_headers(self, headers: HttpHeaders) -> FlextResult[HttpHeaders]:
            """Validate HTTP headers."""
            ...

        def validate_params(self, params: HttpParams) -> FlextResult[HttpParams]:
            """Validate query parameters."""
            ...

    @runtime_checkable
    class ResponseProcessorProtocol(Protocol):
        """Protocol for response processing implementations."""

        def process_response(
            self, response_data: ResponseData, status_code: HttpStatusCode
        ) -> FlextResult[ResponseData]:
            """Process and transform response data."""
            ...

        def handle_error_response(
            self, response_data: ResponseData, status_code: HttpStatusCode
        ) -> FlextResult[Exception]:
            """Handle error responses and create appropriate exceptions."""
            ...

    @runtime_checkable
    class AuthenticationProviderProtocol(Protocol):
        """Protocol for authentication provider implementations."""

        def get_auth_headers(self: object) -> FlextResult[HttpHeaders]:
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
            method: HttpMethod,
            url: str,
            status_code: HttpStatusCode,
            duration_ms: float,
        ) -> FlextResult[bool]:
            """Record request metrics."""
            ...

        def record_error(
            self, error: Exception, context: JsonObject
        ) -> FlextResult[bool]:
            """Record error metrics."""
            ...

        def get_metrics(self: object) -> FlextResult[JsonObject]:
            """Get collected metrics."""
            ...

    @runtime_checkable
    class MiddlewareProtocol(Protocol):
        """Protocol for middleware implementations."""

        async def process_request(
            self, request: RequestData
        ) -> FlextResult[RequestData]:
            """Process incoming request."""
            ...

        async def process_response(
            self, response: ResponseData
        ) -> FlextResult[ResponseData]:
            """Process outgoing response."""
            ...

    @runtime_checkable
    class PluginProtocol(Protocol):
        """Protocol for plugin implementations."""

        def initialize(self, config: JsonObject) -> FlextResult[bool]:
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


# Backward compatibility aliases
HttpClientProtocol = FlextApiProtocols.HttpClientProtocol
StorageBackendProtocol = FlextApiProtocols.StorageBackendProtocol
RetryStrategyProtocol = FlextApiProtocols.RetryStrategyProtocol
ConnectionManagerProtocol = FlextApiProtocols.ConnectionManagerProtocol
CacheProtocol = FlextApiProtocols.CacheProtocol
RequestValidatorProtocol = FlextApiProtocols.RequestValidatorProtocol
ResponseProcessorProtocol = FlextApiProtocols.ResponseProcessorProtocol
AuthenticationProviderProtocol = FlextApiProtocols.AuthenticationProviderProtocol
MetricsCollectorProtocol = FlextApiProtocols.MetricsCollectorProtocol
MiddlewareProtocol = FlextApiProtocols.MiddlewareProtocol
PluginProtocol = FlextApiProtocols.PluginProtocol
ConfigurationProviderProtocol = FlextApiProtocols.ConfigurationProviderProtocol
LoggerProtocol = FlextApiProtocols.LoggerProtocol

__all__ = [
    "AuthenticationProviderProtocol",
    "CacheProtocol",
    "ConfigurationProviderProtocol",
    "ConnectionManagerProtocol",
    "FlextApiProtocols",
    "HttpClientProtocol",
    "LoggerProtocol",
    "MetricsCollectorProtocol",
    "MiddlewareProtocol",
    "PluginProtocol",
    "RequestValidatorProtocol",
    "ResponseProcessorProtocol",
    "RetryStrategyProtocol",
    "StorageBackendProtocol",
]

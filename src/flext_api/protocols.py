"""Protocol definitions for flext-api domain.

All protocol interfaces are centralized here for better type safety and dependency inversion.
Following FLEXT standards: protocols only, no implementations.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_core import FlextProtocols, FlextResult

from .models import FlextApiModels
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
            method: str,
            url: str,
            **kwargs: object,
        ) -> FlextResult[FlextApiModels.HttpResponse]:
            """Execute an HTTP request."""

        def get(
            self,
            url: str,
            **kwargs: object,
        ) -> FlextResult[FlextApiModels.HttpResponse]:
            """Execute HTTP GET request."""

        def post(
            self,
            url: str,
            **kwargs: object,
        ) -> FlextResult[FlextApiModels.HttpResponse]:
            """Execute HTTP POST request."""

        def put(
            self,
            url: str,
            **kwargs: object,
        ) -> FlextResult[FlextApiModels.HttpResponse]:
            """Execute HTTP PUT request."""

        def delete(
            self,
            url: str,
            **kwargs: object,
        ) -> FlextResult[FlextApiModels.HttpResponse]:
            """Execute HTTP DELETE request."""

    @runtime_checkable
    class StorageBackendProtocol(Protocol):
        """Protocol for storage backend implementations."""

        def get(
            self, key: str, default: FlextApiTypes.Core.JsonValue = None
        ) -> FlextResult[FlextApiTypes.Core.JsonValue]:
            """Retrieve value by key."""

        def set(
            self,
            key: FlextApiTypes.StorageKey,
            value: object,
            timeout: int | None = None,
        ) -> FlextResult[None]:
            """Store value with optional timeout."""

        def delete(self, key: str) -> FlextResult[None]:
            """Delete value by key."""

        def exists(self, key: FlextApiTypes.StorageKey) -> FlextResult[bool]:
            """Check if key exists."""

        def clear(self) -> FlextResult[None]:
            """Clear all stored values."""

        def keys(self: object) -> FlextResult[list[FlextApiTypes.StorageKey]]:
            """Get all keys."""

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

        def get_delay(self, attempt: int) -> float:
            """Get delay before next retry attempt."""

        def get_max_attempts(self: object) -> int:
            """Get maximum number of retry attempts."""

    @runtime_checkable
    class ConnectionManagerProtocol(Protocol):
        """Protocol for connection manager implementations."""

        def get_connection(self) -> FlextResult[FlextApiTypes.Core.JsonValue]:
            """Get active connection."""

        def release_connection(self, connection: object) -> FlextResult[bool]:
            """Release connection back to pool."""

        def close_all(self: object) -> FlextResult[bool]:
            """Close all connections."""

        def is_healthy(self: object) -> FlextResult[bool]:
            """Check if connection manager is healthy."""

    @runtime_checkable
    class CacheProtocol(Protocol):
        """Protocol for cache implementations."""

        def get(self, key: str) -> FlextResult[object | None]:
            """Get cached value."""

        def set(
            self, key: str, value: object, ttl: int | None = None
        ) -> FlextResult[bool]:
            """Set cached value with optional TTL."""

        def invalidate(self, key: str) -> FlextResult[bool]:
            """Invalidate cache entry."""

        def clear(self: object) -> FlextResult[bool]:
            """Clear all cache entries."""

    @runtime_checkable
    class RequestValidatorProtocol(Protocol):
        """Protocol for request validation implementations."""

        def validate_request(
            self, request_data: FlextApiTypes.RequestData
        ) -> FlextResult[FlextApiTypes.RequestData]:
            """Validate and sanitize request data."""

        def validate_headers(
            self, headers: FlextApiTypes.HttpHeaders
        ) -> FlextResult[FlextApiTypes.HttpHeaders]:
            """Validate HTTP headers."""

        def validate_params(
            self, params: FlextApiTypes.HttpParams
        ) -> FlextResult[FlextApiTypes.HttpParams]:
            """Validate query parameters."""

    @runtime_checkable
    class ResponseProcessorProtocol(Protocol):
        """Protocol for response processing implementations."""

        def process_response(
            self,
            response_data: FlextApiTypes.ResponseData,
            status_code: FlextApiTypes.HttpStatusCode,
        ) -> FlextResult[FlextApiTypes.ResponseData]:
            """Process and transform response data."""

        def handle_error_response(
            self,
            response_data: FlextApiTypes.ResponseData,
            status_code: FlextApiTypes.HttpStatusCode,
        ) -> FlextResult[Exception]:
            """Handle error responses and create appropriate exceptions."""

    @runtime_checkable
    class AuthenticationProviderProtocol(Protocol):
        """Protocol for authentication provider implementations."""

        def get_auth_headers(self: object) -> FlextResult[FlextApiTypes.HttpHeaders]:
            """Get authentication headers for requests."""

        def is_authenticated(self: object) -> FlextResult[bool]:
            """Check if currently authenticated."""

        def refresh_auth(self: object) -> FlextResult[bool]:
            """Refresh authentication credentials."""

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

        def record_error(
            self, error: Exception, context: FlextApiTypes.JsonObject
        ) -> FlextResult[bool]:
            """Record error metrics."""

        def get_metrics(self: object) -> FlextResult[FlextApiTypes.JsonObject]:
            """Get collected metrics."""

    @runtime_checkable
    class MiddlewareProtocol(Protocol):
        """Protocol for middleware implementations."""

        def process_request(
            self, request: FlextApiTypes.RequestData
        ) -> FlextResult[FlextApiTypes.RequestData]:
            """Process incoming request."""

        def process_response(
            self, response: FlextApiTypes.ResponseData
        ) -> FlextResult[FlextApiTypes.ResponseData]:
            """Process outgoing response."""

    @runtime_checkable
    class PluginProtocol(Protocol):
        """Protocol for plugin implementations."""

        def initialize(self, config: FlextApiTypes.JsonObject) -> FlextResult[bool]:
            """Initialize plugin with configuration."""

        def is_enabled(self: object) -> bool:
            """Check if plugin is enabled."""

        def get_name(self: object) -> str:
            """Get plugin name."""

        def get_version(self: object) -> str:
            """Get plugin version."""

    @runtime_checkable
    class ConfigurationProviderProtocol(Protocol):
        """Protocol for configuration provider implementations."""

        def get_config(self, key: str) -> FlextResult[FlextApiTypes.Core.ConfigValue]:
            """Get configuration value by key."""

        def set_config(self, key: str, value: object) -> FlextResult[bool]:
            """Set configuration value."""

        def reload_config(self: object) -> FlextResult[bool]:
            """Reload configuration from source."""

    @runtime_checkable
    class LoggerProtocol(Protocol):
        """Protocol for logger implementations."""

        def info(self, message: str, **kwargs: object) -> None:
            """Log info message."""

        def error(self, message: str, **kwargs: object) -> None:
            """Log error message."""

        def debug(self, message: str, **kwargs: object) -> None:
            """Log debug message."""

        def warning(self, message: str, **kwargs: object) -> None:
            """Log warning message."""

    # NEW PROTOCOLS FOR TRANSFORMATION (Phase 1)

    @runtime_checkable
    class ProtocolHandlerProtocol(Protocol):
        """Protocol for protocol handler implementations.

        Protocol handlers implement support for different API protocols
        (HTTP, WebSocket, GraphQL, gRPC, SSE).
        """

        def handle_request(
            self,
            request: FlextApiModels.HttpRequest,
            **kwargs: object,
        ) -> FlextResult[FlextApiModels.HttpResponse]:
            """Handle request for this protocol."""

        def supports_protocol(self, protocol: str) -> bool:
            """Check if this handler supports the given protocol."""

        def get_protocol_name(self) -> str:
            """Get protocol name (e.g., 'http', 'websocket', 'graphql')."""

    @runtime_checkable
    class SchemaValidatorProtocol(Protocol):
        """Protocol for schema validator implementations.

        Schema validators implement support for different schema systems
        (OpenAPI, API, JSON Schema, GraphQL Schema, Protobuf).
        """

        def validate_request(
            self,
            request: FlextApiModels.HttpRequest,
            schema: object,
        ) -> FlextResult[dict[str, object]]:
            """Validate request against schema."""

        def validate_response(
            self,
            response: FlextApiModels.HttpResponse,
            schema: object,
        ) -> FlextResult[dict[str, object]]:
            """Validate response against schema."""

        def load_schema(
            self,
            schema_source: str | dict[str, object],
        ) -> FlextResult[object]:
            """Load schema from source."""

        def get_schema_type(self) -> str:
            """Get schema type (e.g., 'openapi', 'jsonschema', 'graphql')."""

    @runtime_checkable
    class TransportLayerProtocol(Protocol):
        """Protocol for transport layer implementations.

        Transport layers implement the actual network communication
        (httpx, websockets, gql, grpcio).
        """

        def connect(
            self,
            url: str,
            **options: object,
        ) -> FlextResult[object]:
            """Establish connection to endpoint."""

        def disconnect(
            self,
            connection: object,
        ) -> FlextResult[None]:
            """Close connection."""

        def send(
            self,
            connection: object,
            data: bytes | str,
            **options: object,
        ) -> FlextResult[None]:
            """Send data through connection."""

        def receive(
            self,
            connection: object,
            **options: object,
        ) -> FlextResult[bytes | str]:
            """Receive data from connection."""

        def supports_streaming(self) -> bool:
            """Check if transport supports streaming."""

    @runtime_checkable
    class RegistryProtocol(Protocol):
        """Protocol for registry implementations.

        Registries manage plugin registration and lookup.
        """

        def register(
            self,
            name: str,
            plugin: object,
        ) -> FlextResult[None]:
            """Register a plugin."""

        def get(
            self,
            name: str,
        ) -> FlextResult[object]:
            """Get registered plugin by name."""

        def list_registered(self) -> FlextResult[list[str]]:
            """List all registered plugin names."""

        def unregister(
            self,
            name: str,
        ) -> FlextResult[None]:
            """Unregister a plugin."""


__all__ = [
    "FlextApiProtocols",
]

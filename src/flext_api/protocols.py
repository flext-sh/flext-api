"""FLEXT API Protocol Definitions - Centralized from flext-core.

This module implements the FLEXT ecosystem protocol architecture by extending
the hierarchical FlextProtocols from flext-core. All protocols follow Clean
Architecture principles with clear separation of concerns.

Architecture:
    Foundation → Domain → Application → Infrastructure → Extensions

Usage:
    from flext_api import FlextApiProtocols

    # Use hierarchical access
    client: FlextApiProtocols.Infrastructure.HttpClient = HttpClientImpl()
    plugin: FlextApiProtocols.Extensions.Plugin = CachePlugin()

    # Or use direct aliases for common patterns
    from flext_api import FlextApiClientProtocol, FlextApiPluginProtocol
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from typing import Protocol, runtime_checkable

from flext_core import FlextResult
from flext_core.protocols import FlextProtocols
from flext_core.typings import FlextTypes

# ==============================================================================
# FLEXT API PROTOCOL EXTENSIONS - Extending flext-core hierarchy
# ==============================================================================


class FlextApiProtocols:
    """FLEXT API protocol extensions following flext-core hierarchical architecture.

    Extends FlextProtocols from flext-core with API-specific interfaces while
    maintaining the hierarchical structure and composition patterns.

    Architecture Layers:
        - Foundation: Core building blocks (from flext-core)
        - Domain: Business logic protocols (from flext-core)
        - Application: Use case handlers (from flext-core)
        - Infrastructure: External systems with HTTP extensions
        - Extensions: Plugins and middleware with API extensions
    """

    # =========================================================================
    # FOUNDATION LAYER - Inherit from flext-core
    # =========================================================================

    Foundation = FlextProtocols.Foundation

    # =========================================================================
    # DOMAIN LAYER - Inherit from flext-core
    # =========================================================================

    Domain = FlextProtocols.Domain

    # =========================================================================
    # APPLICATION LAYER - Inherit from flext-core
    # =========================================================================

    Application = FlextProtocols.Application

    # =========================================================================
    # INFRASTRUCTURE LAYER - Extend with HTTP-specific protocols
    # =========================================================================

    class Infrastructure:
        """Infrastructure layer with HTTP client extensions."""

        # Inherit base infrastructure protocols
        Connection = FlextProtocols.Infrastructure.Connection
        Auth = FlextProtocols.Infrastructure.Auth
        Configurable = FlextProtocols.Infrastructure.Configurable
        LoggerProtocol = FlextProtocols.Infrastructure.LoggerProtocol

        @runtime_checkable
        class HttpClient(Protocol):
            """HTTP client protocol extending Infrastructure.Connection."""

            async def request(
                self,
                method: str,
                url: str,
                *,
                headers: Mapping[str, str] | None = None,
                data: FlextTypes.Core.JsonDict | str | bytes | None = None,
                json: FlextTypes.Core.JsonDict | None = None,
                params: Mapping[str, str] | None = None,
            ) -> FlextResult[FlextTypes.Core.JsonDict]:
                """Make HTTP request with type-safe result."""
                ...

            async def get(
                self,
                url: str,
                *,
                params: Mapping[str, str] | None = None,
                headers: Mapping[str, str] | None = None,
            ) -> FlextResult[FlextTypes.Core.JsonDict]:
                """HTTP GET request."""
                ...

            async def post(
                self,
                url: str,
                *,
                json: FlextTypes.Core.JsonDict | None = None,
                data: str | bytes | None = None,
                headers: Mapping[str, str] | None = None,
            ) -> FlextResult[FlextTypes.Core.JsonDict]:
                """HTTP POST request."""
                ...

            async def put(
                self,
                url: str,
                *,
                json: FlextTypes.Core.JsonDict | None = None,
                data: str | bytes | None = None,
                headers: Mapping[str, str] | None = None,
            ) -> FlextResult[FlextTypes.Core.JsonDict]:
                """HTTP PUT request."""
                ...

            async def delete(
                self,
                url: str,
                *,
                headers: Mapping[str, str] | None = None,
            ) -> FlextResult[FlextTypes.Core.JsonDict]:
                """HTTP DELETE request."""
                ...

            async def close(self) -> None:
                """Close client and cleanup resources."""
                ...

        class ConnectionPool(Protocol):
            """Connection pool management protocol."""

            def get_connection(self) -> FlextResult[FlextApiProtocols.Infrastructure.HttpClient]:
                """Get connection from pool."""
                ...

            def return_connection(
                self, connection: FlextApiProtocols.Infrastructure.HttpClient
            ) -> FlextResult[None]:
                """Return connection to pool."""
                ...

            def close_all(self) -> FlextResult[None]:
                """Close all connections."""
                ...

        class QueryBuilder(Protocol):
            """Query building protocol for API requests."""

            def equals(self, field: str, value: object) -> FlextApiProtocols.Infrastructure.QueryBuilder:
                """Add equality filter."""
                ...

            def sort_asc(self, field: str) -> FlextApiProtocols.Infrastructure.QueryBuilder:
                """Add ascending sort."""
                ...

            def sort_desc(self, field: str) -> FlextApiProtocols.Infrastructure.QueryBuilder:
                """Add descending sort."""
                ...

            def page(self, page_num: int) -> FlextApiProtocols.Infrastructure.QueryBuilder:
                """Set page number."""
                ...

            def page_size(self, size: int) -> FlextApiProtocols.Infrastructure.QueryBuilder:
                """Set page size."""
                ...

            def build(self) -> FlextResult[FlextTypes.Core.JsonDict]:
                """Build final query."""
                ...

        class ResponseBuilder(Protocol):
            """Response building protocol for API responses."""

            def success(
                self,
                data: FlextTypes.Core.JsonDict,
                message: str | None = None,
            ) -> FlextApiProtocols.Infrastructure.ResponseBuilder:
                """Build success response."""
                ...

            def error(
                self,
                message: str,
                code: int,
                details: FlextTypes.Core.JsonDict | None = None,
            ) -> FlextApiProtocols.Infrastructure.ResponseBuilder:
                """Build error response."""
                ...

            def paginated(
                self,
                data: list[FlextTypes.Core.JsonDict],
                total: int,
                page: int,
                page_size: int,
            ) -> FlextApiProtocols.Infrastructure.ResponseBuilder:
                """Build paginated response."""
                ...

            def build(self) -> FlextResult[FlextTypes.Core.JsonDict]:
                """Build final response."""
                ...

    # =========================================================================
    # EXTENSIONS LAYER - Extend with API-specific plugins and middleware
    # =========================================================================

    class Extensions:
        """Extensions layer with API-specific plugins and middleware."""

        # Inherit base extension protocols
        Plugin = FlextProtocols.Extensions.Plugin
        PluginContext = FlextProtocols.Extensions.PluginContext
        Middleware = FlextProtocols.Extensions.Middleware
        AsyncMiddleware = FlextProtocols.Extensions.AsyncMiddleware
        Observability = FlextProtocols.Extensions.Observability

        @runtime_checkable
        class HttpPlugin(Plugin, Protocol):
            """HTTP client plugin extending base Plugin."""

            async def before_request(
                self,
                method: str,
                url: str,
                headers: dict[str, str],
                data: FlextTypes.Core.JsonDict | None = None,
            ) -> FlextResult[tuple[str, str, dict[str, str], FlextTypes.Core.JsonDict | None]]:
                """Process request before sending."""
                ...

            async def after_response(
                self,
                response: FlextTypes.Core.JsonDict,
            ) -> FlextResult[FlextTypes.Core.JsonDict]:
                """Process response after receiving."""
                ...

            async def on_error(
                self, error: Exception
            ) -> FlextResult[FlextTypes.Core.JsonDict | None]:
                """Handle request errors."""
                ...

        class CachePlugin(HttpPlugin, Protocol):
            """HTTP cache plugin."""

            async def get_cached(
                self, cache_key: str
            ) -> FlextResult[FlextTypes.Core.JsonDict | None]:
                """Get cached response."""
                ...

            async def set_cache(
                self,
                cache_key: str,
                response: FlextTypes.Core.JsonDict,
                ttl: int | None = None,
            ) -> FlextResult[None]:
                """Cache response."""
                ...

        class RetryPlugin(HttpPlugin, Protocol):
            """HTTP retry plugin."""

            def should_retry(
                self, error: Exception, attempt: int
            ) -> bool:
                """Determine if request should be retried."""
                ...

            def get_delay(self, attempt: int) -> float:
                """Calculate retry delay."""
                ...

        class RateLimitPlugin(HttpPlugin, Protocol):
            """Rate limiting plugin."""

            async def check_rate_limit(
                self, endpoint: str
            ) -> FlextResult[bool]:
                """Check if rate limit allows request."""
                ...

            async def record_request(
                self, endpoint: str
            ) -> FlextResult[None]:
                """Record request for rate limiting."""
                ...

        class StreamingProtocol(Protocol):
            """Streaming data protocol."""

            async def stream_data(
                self
            ) -> AsyncIterator[FlextTypes.Core.JsonDict]:
                """Stream data asynchronously."""
                ...

            async def close_stream(self) -> FlextResult[None]:
                """Close streaming connection."""
                ...


# ==============================================================================
# BACKWARD COMPATIBILITY ALIASES
# ==============================================================================

# Direct access aliases for common usage patterns
FlextApiClientProtocol = FlextApiProtocols.Infrastructure.HttpClient
FlextApiPluginProtocol = FlextApiProtocols.Extensions.HttpPlugin
FlextApiConnectionPoolProtocol = FlextApiProtocols.Infrastructure.ConnectionPool
FlextApiQueryBuilderProtocol = FlextApiProtocols.Infrastructure.QueryBuilder
FlextApiResponseBuilderProtocol = FlextApiProtocols.Infrastructure.ResponseBuilder

# Legacy protocol aliases mapping to flext-core hierarchy
FlextApiServiceProtocol = FlextProtocols.Domain.Service
FlextApiAuthProtocol = FlextProtocols.Infrastructure.Auth
FlextApiAuthorizationProtocol = FlextProtocols.Infrastructure.Auth
FlextApiRepositoryProtocol = FlextProtocols.Domain.Repository
FlextApiCacheProtocol = FlextApiProtocols.Extensions.CachePlugin
FlextApiMiddlewareProtocol = FlextProtocols.Extensions.Middleware
FlextApiRateLimitProtocol = FlextApiProtocols.Extensions.RateLimitPlugin
FlextApiHandlerProtocol = FlextProtocols.Application.Handler
FlextApiValidatorProtocol = FlextProtocols.Foundation.Validator
FlextApiStreamProtocol = FlextApiProtocols.Extensions.StreamingProtocol
FlextApiWebSocketProtocol = FlextApiProtocols.Extensions.StreamingProtocol  # WebSocket is streaming
FlextApiMetricsProtocol = FlextProtocols.Extensions.Observability
FlextApiHealthCheckProtocol = FlextProtocols.Extensions.Observability  # Health check is observability


# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    # Main hierarchical protocol class
    "FlextApiProtocols",

    # Direct access aliases - commonly used
    "FlextApiClientProtocol",
    "FlextApiPluginProtocol",
    "FlextApiConnectionPoolProtocol",
    "FlextApiQueryBuilderProtocol",
    "FlextApiResponseBuilderProtocol",

    # Legacy compatibility aliases
    "FlextApiServiceProtocol",
    "FlextApiAuthProtocol",
    "FlextApiAuthorizationProtocol",
    "FlextApiRepositoryProtocol",
    "FlextApiCacheProtocol",
    "FlextApiMiddlewareProtocol",
    "FlextApiRateLimitProtocol",
    "FlextApiHandlerProtocol",
    "FlextApiValidatorProtocol",
    "FlextApiStreamProtocol",
    "FlextApiWebSocketProtocol",
    "FlextApiMetricsProtocol",
    "FlextApiHealthCheckProtocol",
]

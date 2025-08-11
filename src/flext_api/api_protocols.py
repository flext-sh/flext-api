"""FLEXT API Protocols - Enhanced interface definitions following PEP8 standards.

Enhanced protocol module providing comprehensive interface definitions for the
FLEXT API library. Follows Interface Segregation Principle and Dependency
Inversion Principle with type-safe protocol definitions.

Architecture:
    Protocol Layer → Interface Contracts → Implementation Guidelines

Core Features:
    - Type-safe protocol definitions with runtime checking
    - Interface segregation for focused responsibilities
    - Async/sync method support for different use cases
    - Generic protocols for flexible implementations

Design Patterns:
    - Interface Segregation Principle: Minimal focused interfaces
    - Dependency Inversion Principle: Depend on abstractions
    - Protocol Pattern: Structural typing for flexible implementations
    - Strategy Pattern: Pluggable algorithm interfaces

Usage:
    from flext_api.api_protocols import FlextApiClientProtocol

    class MyApiClient:
        def __init__(self, client: FlextApiClientProtocol):
            self._client = client

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Mapping

    from flext_core import FlextResult, FlextTypes

# ==============================================================================
# HTTP CLIENT PROTOCOLS
# ==============================================================================


@runtime_checkable
class FlextApiClientProtocol(Protocol):
    """Protocol for HTTP client implementations.

    Follows Interface Segregation Principle - minimal required interface.
    Provides type-safe contract for HTTP operations with async support.
    """

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        data: FlextTypes.Core.JsonDict | str | bytes | None = None,
        json: FlextTypes.Core.JsonDict | None = None,
        params: Mapping[str, str] | None = None,
        timeout: float | None = None,
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Target URL
            headers: Optional request headers
            data: Optional form data
            json: Optional JSON data
            params: Optional query parameters
            timeout: Optional timeout in seconds

        Returns:
            FlextResult containing response data or error

        """
        ...

    async def get(
        self,
        url: str,
        *,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        timeout: float | None = None,
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Perform GET request."""
        ...

    async def post(
        self,
        url: str,
        *,
        json: FlextTypes.Core.JsonDict | None = None,
        data: str | bytes | None = None,
        headers: Mapping[str, str] | None = None,
        timeout: float | None = None,
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Perform POST request."""
        ...

    async def put(
        self,
        url: str,
        *,
        json: FlextTypes.Core.JsonDict | None = None,
        data: str | bytes | None = None,
        headers: Mapping[str, str] | None = None,
        timeout: float | None = None,
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Perform PUT request."""
        ...

    async def delete(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        timeout: float | None = None,
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Perform DELETE request."""
        ...

    async def close(self) -> None:
        """Close the client and cleanup resources."""
        ...


@runtime_checkable
class FlextApiPluginProtocol(Protocol):
    """Protocol for HTTP client plugins.

    Follows Open/Closed Principle - extend behavior without modification.
    Supports async plugin operations for request/response processing.
    """

    name: str
    enabled: bool

    async def before_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        **kwargs: FlextTypes.Core.JsonDict,
    ) -> FlextResult[None]:
        """Hook called before request execution.

        Args:
            method: HTTP method
            url: Target URL
            headers: Request headers (mutable)
            **kwargs: Additional request parameters

        Returns:
            FlextResult indicating success or failure

        """
        ...

    async def after_response(
        self,
        response: FlextTypes.Core.JsonDict,
        method: str,
        url: str,
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Hook called after response received.

        Args:
            response: Response data
            method: HTTP method used
            url: Target URL

        Returns:
            FlextResult containing modified response or error

        """
        ...


@runtime_checkable
class FlextApiConnectionPoolProtocol(Protocol):
    """Protocol for HTTP connection pool management."""

    async def get_connection(self, host: str, port: int, ssl: bool = False) -> FlextResult[object]:
        """Get connection from pool."""
        ...

    async def return_connection(self, connection: object) -> FlextResult[None]:
        """Return connection to pool."""
        ...

    async def close_pool(self) -> FlextResult[None]:
        """Close all connections in pool."""
        ...


# ==============================================================================
# BUILDER PROTOCOLS
# ==============================================================================


@runtime_checkable
class FlextApiQueryBuilderProtocol(Protocol):
    """Protocol for query builders.

    Follows Builder Pattern and Single Responsibility Principle.
    Provides fluent interface for constructing API queries.
    """

    def add_filter(
        self,
        field: str,
        value: FlextTypes.Core.JsonDict | str | float | bool | None,
        operator: str = "eq",
    ) -> FlextApiQueryBuilderProtocol:
        """Add a filter to the query.

        Args:
            field: Field name to filter
            value: Filter value
            operator: Filter operator (eq, ne, gt, lt, etc.)

        Returns:
            Self for method chaining

        """
        ...

    def add_sort(
        self, field: str, ascending: bool = True
    ) -> FlextApiQueryBuilderProtocol:
        """Add sorting to the query.

        Args:
            field: Field to sort by
            ascending: Sort direction

        Returns:
            Self for method chaining

        """
        ...

    def set_pagination(self, page: int, size: int) -> FlextApiQueryBuilderProtocol:
        """Set pagination parameters.

        Args:
            page: Page number (1-based)
            size: Page size

        Returns:
            Self for method chaining

        """
        ...

    def add_search(self, term: str, fields: list[str] | None = None) -> FlextApiQueryBuilderProtocol:
        """Add search functionality.

        Args:
            term: Search term
            fields: Fields to search in (optional)

        Returns:
            Self for method chaining

        """
        ...

    def select_fields(self, fields: list[str]) -> FlextApiQueryBuilderProtocol:
        """Select specific fields to return.

        Args:
            fields: List of field names

        Returns:
            Self for method chaining

        """
        ...

    def build(self) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Build the final query dictionary.

        Returns:
            FlextResult containing query dict or error

        """
        ...


@runtime_checkable
class FlextApiResponseBuilderProtocol(Protocol):
    """Protocol for response builders.

    Follows Builder Pattern for constructing API responses.
    Provides standardized response format across the API.
    """

    def set_success(self, success: bool = True) -> FlextApiResponseBuilderProtocol:
        """Set response success status.

        Args:
            success: Whether the operation was successful

        Returns:
            Self for method chaining

        """
        ...

    def set_data(
        self,
        data: FlextTypes.Core.JsonDict | list | str | float | bool | None,
    ) -> FlextApiResponseBuilderProtocol:
        """Set response data.

        Args:
            data: Response payload

        Returns:
            Self for method chaining

        """
        ...

    def set_message(self, message: str) -> FlextApiResponseBuilderProtocol:
        """Set response message.

        Args:
            message: Human-readable message

        Returns:
            Self for method chaining

        """
        ...

    def set_error(self, error: str | None) -> FlextApiResponseBuilderProtocol:
        """Set error message.

        Args:
            error: Error message if any

        Returns:
            Self for method chaining

        """
        ...

    def add_metadata(
        self,
        key: str,
        value: FlextTypes.Core.JsonDict | str | float | bool | None,
    ) -> FlextApiResponseBuilderProtocol:
        """Add metadata to response.

        Args:
            key: Metadata key
            value: Metadata value

        Returns:
            Self for method chaining

        """
        ...

    def set_pagination(
        self,
        page: int,
        page_size: int,
        total: int,
    ) -> FlextApiResponseBuilderProtocol:
        """Set pagination metadata.

        Args:
            page: Current page
            page_size: Items per page
            total: Total items

        Returns:
            Self for method chaining

        """
        ...

    def build(self) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Build the final response dictionary.

        Returns:
            FlextResult containing response dict or error

        """
        ...


# ==============================================================================
# SERVICE PROTOCOLS
# ==============================================================================


@runtime_checkable
class FlextApiServiceProtocol(Protocol):
    """Protocol for API services.

    Extends flext-core service patterns for consistency.
    Provides lifecycle management and health checking.
    """

    async def start(self) -> FlextResult[None]:
        """Start the service.

        Returns:
            FlextResult indicating success or failure

        """
        ...

    async def stop(self) -> FlextResult[None]:
        """Stop the service.

        Returns:
            FlextResult indicating success or failure

        """
        ...

    async def restart(self) -> FlextResult[None]:
        """Restart the service.

        Returns:
            FlextResult indicating success or failure

        """
        ...

    async def health_check(self) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Check service health.

        Returns:
            FlextResult containing health status or error

        """
        ...

    def get_status(self) -> str:
        """Get current service status."""
        ...


@runtime_checkable
class FlextApiAuthProtocol(Protocol):
    """Protocol for authentication providers.

    Follows Dependency Inversion - depend on abstraction not concretion.
    Supports multiple authentication methods and token management.
    """

    async def authenticate(
        self, credentials: FlextTypes.Core.JsonDict
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Authenticate with credentials.

        Args:
            credentials: Authentication credentials

        Returns:
            FlextResult containing auth token/data or error

        """
        ...

    async def validate_token(self, token: str) -> FlextResult[bool]:
        """Validate an authentication token.

        Args:
            token: Token to validate

        Returns:
            FlextResult containing validation result

        """
        ...

    async def refresh_token(self, token: str) -> FlextResult[str]:
        """Refresh an authentication token.

        Args:
            token: Current token

        Returns:
            FlextResult containing new token or error

        """
        ...

    async def revoke_token(self, token: str) -> FlextResult[None]:
        """Revoke an authentication token.

        Args:
            token: Token to revoke

        Returns:
            FlextResult indicating success or failure

        """
        ...

    async def get_user_info(self, token: str) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Get user information from token.

        Args:
            token: Authentication token

        Returns:
            FlextResult containing user information

        """
        ...


@runtime_checkable
class FlextApiAuthorizationProtocol(Protocol):
    """Protocol for authorization and permission checking."""

    async def check_permission(
        self,
        user_id: str,
        resource: str,
        action: str,
    ) -> FlextResult[bool]:
        """Check if user has permission for action on resource.

        Args:
            user_id: User identifier
            resource: Resource identifier
            action: Action being performed

        Returns:
            FlextResult containing permission check result

        """
        ...

    async def get_user_roles(self, user_id: str) -> FlextResult[list[str]]:
        """Get roles for user.

        Args:
            user_id: User identifier

        Returns:
            FlextResult containing list of role names

        """
        ...

    async def grant_permission(
        self,
        user_id: str,
        resource: str,
        action: str,
    ) -> FlextResult[None]:
        """Grant permission to user.

        Args:
            user_id: User identifier
            resource: Resource identifier
            action: Action being granted

        Returns:
            FlextResult indicating success or failure

        """
        ...


# ==============================================================================
# REPOSITORY PROTOCOLS
# ==============================================================================


@runtime_checkable
class FlextApiRepositoryProtocol(Protocol):
    """Protocol for data repositories.

    Follows Repository Pattern for data access abstraction.
    Provides CRUD operations with filtering and pagination.
    """

    async def find_by_id(self, entity_id: str) -> FlextResult[FlextTypes.Core.JsonDict | None]:
        """Find entity by ID.

        Args:
            entity_id: Entity identifier

        Returns:
            FlextResult containing entity or None if not found

        """
        ...

    async def find_all(
        self,
        filters: FlextTypes.Core.JsonDict | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        sort_desc: bool = False,
    ) -> FlextResult[list[FlextTypes.Core.JsonDict]]:
        """Find all entities matching criteria.

        Args:
            filters: Optional filter criteria
            limit: Optional result limit
            offset: Optional result offset
            sort_by: Field to sort by
            sort_desc: Sort in descending order

        Returns:
            FlextResult containing entity list or error

        """
        ...

    async def count(
        self,
        filters: FlextTypes.Core.JsonDict | None = None,
    ) -> FlextResult[int]:
        """Count entities matching criteria.

        Args:
            filters: Optional filter criteria

        Returns:
            FlextResult containing count or error

        """
        ...

    async def save(
        self, entity: FlextTypes.Core.JsonDict
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Save an entity.

        Args:
            entity: Entity to save

        Returns:
            FlextResult containing saved entity or error

        """
        ...

    async def update(
        self,
        entity_id: str,
        updates: FlextTypes.Core.JsonDict,
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Update an entity.

        Args:
            entity_id: Entity identifier
            updates: Fields to update

        Returns:
            FlextResult containing updated entity or error

        """
        ...

    async def delete(self, entity_id: str) -> FlextResult[None]:
        """Delete an entity by ID.

        Args:
            entity_id: Entity identifier

        Returns:
            FlextResult indicating success or failure

        """
        ...

    async def exists(self, entity_id: str) -> FlextResult[bool]:
        """Check if entity exists.

        Args:
            entity_id: Entity identifier

        Returns:
            FlextResult containing existence check result

        """
        ...


@runtime_checkable
class FlextApiCacheProtocol(Protocol):
    """Protocol for caching implementations."""

    async def get(self, key: str) -> FlextResult[FlextTypes.Core.JsonDict | None]:
        """Get cached value by key."""
        ...

    async def set(
        self,
        key: str,
        value: FlextTypes.Core.JsonDict,
        ttl_seconds: int | None = None,
    ) -> FlextResult[None]:
        """Set cached value with optional TTL."""
        ...

    async def delete(self, key: str) -> FlextResult[bool]:
        """Delete cached value."""
        ...

    async def clear(self) -> FlextResult[None]:
        """Clear all cached values."""
        ...


# ==============================================================================
# MIDDLEWARE PROTOCOLS
# ==============================================================================


@runtime_checkable
class FlextApiMiddlewareProtocol(Protocol):
    """Protocol for API middleware.

    Follows Chain of Responsibility Pattern.
    Provides request/response processing pipeline.
    """

    async def process_request(
        self, request: FlextTypes.Core.JsonDict
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Process incoming request.

        Args:
            request: Request data

        Returns:
            FlextResult containing processed request or error

        """
        ...

    async def process_response(
        self, response: FlextTypes.Core.JsonDict
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Process outgoing response.

        Args:
            response: Response data

        Returns:
            FlextResult containing processed response or error

        """
        ...


@runtime_checkable
class FlextApiRateLimitProtocol(Protocol):
    """Protocol for rate limiting implementations."""

    async def check_rate_limit(
        self,
        identifier: str,
        resource: str,
        window_seconds: int,
        max_requests: int,
    ) -> FlextResult[bool]:
        """Check if rate limit is exceeded.

        Args:
            identifier: Client/user identifier
            resource: Resource being accessed
            window_seconds: Rate limit window
            max_requests: Maximum requests in window

        Returns:
            FlextResult indicating if request is allowed

        """
        ...

    async def get_rate_limit_info(
        self,
        identifier: str,
        resource: str,
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Get rate limit information.

        Args:
            identifier: Client/user identifier
            resource: Resource being accessed

        Returns:
            FlextResult containing rate limit info

        """
        ...


# ==============================================================================
# HANDLER PROTOCOLS
# ==============================================================================


@runtime_checkable
class FlextApiHandlerProtocol(Protocol):
    """Protocol for request handlers.

    Follows Command Pattern and Single Responsibility Principle.
    Provides type-safe request processing interface.
    """

    async def handle(
        self, request: FlextTypes.Core.JsonDict
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Handle a request.

        Args:
            request: Request data

        Returns:
            FlextResult containing response or error

        """
        ...

    def can_handle(self, request: FlextTypes.Core.JsonDict) -> bool:
        """Check if handler can process the request.

        Args:
            request: Request data

        Returns:
            True if handler can process the request

        """
        ...


@runtime_checkable
class FlextApiValidatorProtocol(Protocol):
    """Protocol for request/response validation."""

    async def validate_request(
        self, request: FlextTypes.Core.JsonDict
    ) -> FlextResult[None]:
        """Validate request data.

        Args:
            request: Request data to validate

        Returns:
            FlextResult indicating validation success or failure

        """
        ...

    async def validate_response(
        self, response: FlextTypes.Core.JsonDict
    ) -> FlextResult[None]:
        """Validate response data.

        Args:
            response: Response data to validate

        Returns:
            FlextResult indicating validation success or failure

        """
        ...


# ==============================================================================
# STREAMING PROTOCOLS
# ==============================================================================


@runtime_checkable
class FlextApiStreamProtocol(Protocol):
    """Protocol for streaming responses.

    Supports async iteration for streaming data.
    Provides efficient large data transfer capabilities.
    """

    def __aiter__(self) -> AsyncIterator[bytes]:
        """Return async iterator for streaming."""
        ...

    async def __anext__(self) -> bytes:
        """Get next chunk of data."""
        ...

    async def close(self) -> None:
        """Close the stream."""
        ...


@runtime_checkable
class FlextApiWebSocketProtocol(Protocol):
    """Protocol for WebSocket connections."""

    async def accept(self) -> FlextResult[None]:
        """Accept WebSocket connection."""
        ...

    async def send_text(self, data: str) -> FlextResult[None]:
        """Send text message."""
        ...

    async def send_bytes(self, data: bytes) -> FlextResult[None]:
        """Send binary message."""
        ...

    async def receive(self) -> FlextResult[str | bytes]:
        """Receive message from WebSocket."""
        ...

    async def close(self, code: int = 1000, reason: str = "") -> FlextResult[None]:
        """Close WebSocket connection."""
        ...


# ==============================================================================
# MONITORING PROTOCOLS
# ==============================================================================


@runtime_checkable
class FlextApiMetricsProtocol(Protocol):
    """Protocol for metrics collection."""

    def increment_counter(self, name: str, tags: dict[str, str] | None = None) -> None:
        """Increment a counter metric."""
        ...

    def record_gauge(self, name: str, value: float, tags: dict[str, str] | None = None) -> None:
        """Record a gauge metric."""
        ...

    def record_histogram(self, name: str, value: float, tags: dict[str, str] | None = None) -> None:
        """Record a histogram metric."""
        ...

    async def get_metrics(self) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Get collected metrics."""
        ...


@runtime_checkable
class FlextApiHealthCheckProtocol(Protocol):
    """Protocol for health check implementations."""

    async def check_health(self) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Perform health check."""
        ...

    def get_name(self) -> str:
        """Get health check name."""
        ...

    def is_critical(self) -> bool:
        """Check if this health check is critical."""
        ...


# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    # HTTP Client Protocols
    "FlextApiClientProtocol",
    "FlextApiPluginProtocol",
    "FlextApiConnectionPoolProtocol",
    # Builder Protocols
    "FlextApiQueryBuilderProtocol",
    "FlextApiResponseBuilderProtocol",
    # Service Protocols
    "FlextApiServiceProtocol",
    "FlextApiAuthProtocol",
    "FlextApiAuthorizationProtocol",
    # Repository Protocols
    "FlextApiRepositoryProtocol",
    "FlextApiCacheProtocol",
    # Middleware Protocols
    "FlextApiMiddlewareProtocol",
    "FlextApiRateLimitProtocol",
    # Handler Protocols
    "FlextApiHandlerProtocol",
    "FlextApiValidatorProtocol",
    # Streaming Protocols
    "FlextApiStreamProtocol",
    "FlextApiWebSocketProtocol",
    # Monitoring Protocols
    "FlextApiMetricsProtocol",
    "FlextApiHealthCheckProtocol",
]

"""FLEXT API - Unified API interface using flext-core composition.

Reduces module complexity by leveraging flext-core patterns.
Elimina redundância usando ServiceResult, DI, e builder patterns.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from flext_core import FlextResult, get_logger

from flext_api.builder import (
    FlextApiBuilder,
    build_error_response,
    build_paginated_response,
    build_query,
    build_success_response,
)
from flext_api.client import FlextApiClient, FlextApiClientConfig


class FlextApi:
    """Unified API class combining all flext-api functionality.

    Uses composition to provide access to all API features through a single interface.
    Leverages flext-core patterns for consistency and reduced code duplication.
    """

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self._builder = FlextApiBuilder()
        self._client = None
        self.logger.info("FlextApi initialized with unified builder")

    # HTTP Client functionality using flext-core service pattern
    def flext_api_create_client(
        self,
        config: dict | None = None,
    ) -> FlextResult[FlextApiClient]:
        """Create HTTP client with configuration."""
        try:
            client_config = FlextApiClientConfig(**(config or {}))
            self._client = FlextApiClient(client_config)
            return FlextResult.ok(self._client)
        except Exception as e:
            self.logger.exception("Failed to create client")
            return FlextResult.fail(f"Client creation failed: {e}")

    def flext_api_request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> FlextResult[dict]:
        """Make HTTP request using configured client."""
        if not self._client:
            return FlextResult.fail(
                "Client not initialized. Call flext_api_create_client first.",
            )

        # Client returns FlextResult already
        return self._client.request(method, url, **kwargs)

    # Query building using unified builder
    def flext_api_create_query(self) -> FlextApiBuilder:
        """Create query builder instance."""
        return self._builder.for_query()

    def flext_api_build_query(self, **filters: Any) -> dict:
        """Build query from filters using unified builder."""
        return build_query(**filters)

    # Response building using unified builder
    def flext_api_success_response(self, data: Any, message: str = "Success") -> dict:
        """Create success response using unified builder."""
        return build_success_response(data, message)

    def flext_api_error_response(self, message: str, error_code: int = 500) -> dict:
        """Create error response using unified builder."""
        return build_error_response(message, error_code)

    def flext_api_paginated_response(
        self,
        data: Any,
        total: int,
        page: int,
        page_size: int,
        message: str = "Success",
    ) -> dict:
        """Create paginated response using unified builder."""
        return build_paginated_response(data, total, page, page_size, message)

    def flext_api_response_with_metadata(
        self,
        data: Any,
        message: str = "Success",
        **metadata: Any,
    ) -> dict:
        """Create response with metadata using unified builder."""
        builder = self._builder.for_response().success(data, message)
        for key, value in metadata.items():
            builder.with_metadata(key, value)
        return builder.build()

    # App creation functionality
    def flext_api_create_app(self, **config: Any) -> Any:
        """Create FastAPI app using unified builder."""
        app_builder = self._builder.for_app()

        # Apply config to builder
        if "middlewares" in config:
            for middleware in config["middlewares"]:
                app_builder.with_middleware(middleware)

        if "routes" in config:
            for route in config["routes"]:
                app_builder.with_route(route)

        return app_builder.build()

    # Advanced query operations
    def flext_api_query_with_pagination(
        self,
        page: int,
        page_size: int,
        **filters: Any,
    ) -> dict:
        """Build query with pagination and filters."""
        builder = self._builder.for_query()

        # Add filters
        for field, value in filters.items():
            builder.equals(field, value)

        # Add pagination
        builder.page(page, page_size)

        return builder.build()

    def flext_api_query_with_sorting(
        self,
        sort_field: str,
        sort_direction: str = "asc",
        **filters: Any,
    ) -> dict:
        """Build query with sorting and filters."""
        builder = self._builder.for_query()

        # Add filters
        for field, value in filters.items():
            builder.equals(field, value)

        # Add sorting
        builder.sort(sort_field, sort_direction)

        return builder.build()

    # Advanced response operations
    def flext_api_response_with_pagination_data(
        self,
        data: Any,
        total: int,
        page: int,
        page_size: int,
        message: str = "Success",
        **metadata: Any,
    ) -> dict:
        """Create response with data, pagination, and metadata."""
        builder = (
            self._builder.for_response()
            .success(data, message)
            .with_pagination_response(total, page, page_size)
        )

        # Add metadata
        for key, value in metadata.items():
            builder.with_metadata(key, value)

        return builder.build()

    def flext_api_health(self) -> dict:
        """Get API health status."""
        return {
            "status": "healthy",
            "client_initialized": self._client is not None,
            "timestamp": self._get_timestamp(),
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now(UTC).isoformat()

    # Full feature methods restored
    def flext_api_query_complex(
        self,
        filters: dict[str, Any] | None = None,
        sorts: list[dict[str, str]] | None = None,
        page: int | None = None,
        page_size: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict:
        """Build complex query with all parameters."""
        builder = self._builder.for_query()

        # Add filters
        if filters:
            for field, value in filters.items():
                if isinstance(value, dict) and "operator" in value:
                    builder.filter(field, value["operator"], value.get("value"))
                else:
                    builder.equals(field, value)

        # Add sorts
        if sorts:
            for sort_config in sorts:
                builder.sort(sort_config["field"], sort_config.get("direction", "asc"))

        # Add pagination
        if page and page_size:
            builder.page(page, page_size)

        return builder.build()

    def flext_api_response_complete(
        self,
        success: bool,
        data: Any = None,
        message: str = "",
        error_code: int | None = None,
        metadata: dict[str, Any] | None = None,
        pagination: dict[str, Any] | None = None,
    ) -> dict:
        """Build complete response with all features."""
        builder = self._builder.for_response()

        if success:
            builder.success(data, message or "Operation successful")
        else:
            builder.error(message or "Operation failed", error_code or 500)

        # Add metadata
        if metadata:
            for key, value in metadata.items():
                builder.with_metadata(key, value)

        # Add pagination
        if pagination:
            builder.with_pagination_response(
                pagination["total"],
                pagination["page"],
                pagination["page_size"],
            )

        return builder.build()


# Factory function for backwards compatibility
def create_flext_api() -> FlextApi:
    """Create FlextApi instance."""
    return FlextApi()

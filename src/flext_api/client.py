"""FLEXT API HTTP Client - CONSOLIDATED ARCHITECTURE.

Este módulo implementa o padrão CONSOLIDATED seguindo FLEXT_REFACTORING_PROMPT.md.
Todos os componentes de client estão centralizados na classe FlextApiClient,
eliminando a violação de "múltiplas classes por módulo" e garantindo
consistência arquitetural seguindo single-consolidated-class-per-module.

Padrões FLEXT aplicados:
- Classe CONSOLIDADA FlextApiClient contendo TODOS os componentes
- FlextResult para operações que podem falhar
- Nested classes para organização (Operation, Builder, QueryBuilder, ResponseBuilder)
- FlextLogger do flext-core
- Eliminação completa de duplicação com builders.py

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import math
import time

# Time operations now use time module directly - no FlextUtilities.TimeUtils needed
# Datetime operations now use FlextUtilities.Generators.generate_iso_timestamp() - available
from typing import Self, TypeVar, cast
from urllib.parse import urljoin

import aiohttp
from flext_core import FlextLogger, FlextResult, FlextTypes, FlextUtilities

from flext_api.models import (
    ApiRequest,
    ApiResponse,
    ClientConfig,
    ClientStatus,
    HttpMethod,
)
from flext_api.plugins import FlextApiPlugin

logger = FlextLogger(__name__)

# Type variables
T = TypeVar("T")

# Type aliases from models for backward compatibility
FlextApiClientConfig = ClientConfig
FlextApiClientRequest = ApiRequest
FlextApiClientResponse = ApiResponse
FlextApiClientStatus = ClientStatus
FlextApiClientMethod = HttpMethod


# ==============================================================================
# CONSOLIDATED FLEXT API CLIENT CLASS
# ==============================================================================


class FlextApiClient:
    """Single consolidated class containing ALL HTTP client functionality following FLEXT patterns.

    This class follows the CONSOLIDATED class pattern from FLEXT_REFACTORING_PROMPT.md,
    centralizing ALL client functionality into a single class structure to eliminate
    the "multiple classes per module" violation while maintaining clean
    architecture principles following single-consolidated-class-per-module.

    All client components are implemented as nested classes within this consolidated structure:
    - Operation: API operation definition
    - Builder: Main builder factory
    - QueryBuilder: Query construction with fluent interface
    - ResponseBuilder: Response construction
    - PaginatedResponseBuilder: Specialized paginated response builder

    This eliminates duplication with builders.py and provides a single entry point
    for all HTTP client operations while maintaining logical separation of concerns.
    """

    def __init__(
        self,
        config: ClientConfig | dict[str, object] | None = None,
        plugins: list[FlextApiPlugin] | None = None,
    ) -> None:
        """Initialize HTTP client with configuration and optional plugins."""
        # Normalize configuration
        if isinstance(config, dict):
            self.config = ClientConfig.model_validate(config)
        else:
            self.config = config or ClientConfig(base_url="http://localhost:8000")

        # Initialize plugins
        self.plugins = plugins or []

        # Initialize session
        self._session: aiohttp.ClientSession | None = None
        self._closed = False

        # Statistics
        self._stats = {
            "requests_made": 0,
            "requests_successful": 0,
            "requests_failed": 0,
            "total_time": 0.0,
        }

        logger.info(
            "FlextApiClient initialized",
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            plugins_count=len(self.plugins),
        )

    # ==========================================================================
    # NESTED OPERATION CLASS - API operation definition
    # ==========================================================================

    class Operation:
        """Operation class for API operations."""

        def __init__(self, name: str, method: HttpMethod, endpoint: str) -> None:
            """Initialize operation."""
            self.name = name
            self.method = method
            self.endpoint = endpoint

    # ==========================================================================
    # NESTED BUILDER CLASSES - Query and response construction
    # ==========================================================================

    class Builder:
        """Main builder factory for API operations."""

        def for_query(self) -> FlextApiClient.QueryBuilder:
            """Create query builder."""
            return FlextApiClient.QueryBuilder()

        def for_response(self) -> FlextApiClient.ResponseBuilder:
            """Create response builder."""
            return FlextApiClient.ResponseBuilder()

    class QueryBuilder:
        """Query builder with fluent interface."""

        def __init__(self) -> None:
            """Initialize query builder."""
            self._filters: list[FlextTypes.Core.JsonDict] = []
            self._sorts: list[dict[str, str]] = []
            self._page = 1
            self._page_size = 20
            self._search: str | None = None
            self._fields: list[str] | None = None
            self._includes: list[str] | None = None
            self._excludes: list[str] | None = None

        def with_filters(self, filters: FlextTypes.Core.JsonDict) -> Self:
            """Add filters to query."""
            for key, value in filters.items():
                self._filters.append({"field": key, "value": value, "operator": "eq"})
            return self

        def equals(self, field: str, value: object) -> Self:
            """Add equality filter."""
            self._filters.append({"field": field, "value": value, "operator": "eq"})
            return self

        def not_equals(self, field: str, value: object) -> Self:
            """Add not equals filter."""
            self._filters.append({"field": field, "value": value, "operator": "ne"})
            return self

        def contains(self, field: str, value: str) -> Self:
            """Add contains filter."""
            self._filters.append({
                "field": field,
                "value": value,
                "operator": "contains",
            })
            return self

        def sort_asc(self, field: str) -> Self:
            """Add ascending sort."""
            self._sorts.append({"field": field, "direction": "asc"})
            return self

        def sort_desc(self, field: str) -> Self:
            """Add descending sort."""
            self._sorts.append({"field": field, "direction": "desc"})
            return self

        def page(self, page_number: int) -> Self:
            """Set page number."""
            self._page = max(1, page_number)
            return self

        def page_size(self, size: int) -> Self:
            """Set page size."""
            self._page_size = max(1, min(1000, size))
            return self

        def search(self, term: str) -> Self:
            """Set search term."""
            self._search = term
            return self

        def fields(self, fields: list[str]) -> Self:
            """Set fields to include."""
            self._fields = fields
            return self

        def includes(self, includes: list[str]) -> Self:
            """Set related data to include."""
            self._includes = includes
            return self

        def excludes(self, excludes: list[str]) -> Self:
            """Set fields to exclude."""
            self._excludes = excludes
            return self

        def build(self) -> FlextTypes.Core.JsonDict:
            """Build the final query object."""
            query = cast(
                "FlextTypes.Core.JsonDict",
                {
                    "filters": self._filters,
                    "sorts": self._sorts,
                    "pagination": {
                        "page": self._page,
                        "page_size": self._page_size,
                    },
                },
            )

            if self._search:
                query["search"] = self._search
            if self._fields:
                query["fields"] = self._fields
            if self._includes:
                query["includes"] = self._includes
            if self._excludes:
                query["excludes"] = self._excludes

            return query

    class ResponseBuilder:
        """Response builder for constructing API responses."""

        def __init__(self) -> None:
            """Initialize response builder."""
            self._data: object = None
            self._message = "Request completed successfully"
            self._status_code = 200
            self._metadata: FlextTypes.Core.JsonDict = {}

        def success(self, data: object = None, message: str = "Success") -> Self:
            """Set successful response data."""
            self._data = data
            self._message = message
            self._status_code = 200
            return self

        def error(self, message: str, status_code: int = 400) -> Self:
            """Set error response."""
            self._data = None
            self._message = message
            self._status_code = status_code
            return self

        def with_metadata(self, metadata: FlextTypes.Core.JsonDict) -> Self:
            """Add metadata to response."""
            self._metadata.update(metadata)
            return self

        def build(self) -> FlextTypes.Core.JsonDict:
            """Build the final response object."""
            return cast(
                "FlextTypes.Core.JsonDict",
                {
                    "data": self._data,
                    "message": self._message,
                    "status_code": self._status_code,
                    "metadata": dict(self._metadata),
                    "timestamp": FlextUtilities.generate_iso_timestamp(),
                },
            )

    class PaginatedResponseBuilder(ResponseBuilder):
        """Specialized builder for paginated responses."""

        def __init__(self) -> None:
            """Initialize paginated response builder."""
            super().__init__()
            self._current_page = 1
            self._page_size = 20
            self._total_items = 0

        def with_pagination(
            self, current_page: int, page_size: int, total_items: int
        ) -> Self:
            """Set pagination information."""
            self._current_page = current_page
            self._page_size = page_size
            self._total_items = total_items
            return self

        def build(self) -> FlextTypes.Core.JsonDict:
            """Build paginated response with pagination metadata."""
            response = super().build()

            total_pages = (
                math.ceil(self._total_items / self._page_size)
                if self._page_size > 0
                else 1
            )

            pagination = {
                "current_page": self._current_page,
                "page_size": self._page_size,
                "total_items": self._total_items,
                "total_pages": total_pages,
                "has_next": self._current_page < total_pages,
                "has_previous": self._current_page > 1,
            }

            response["pagination"] = pagination
            return response

    # ==========================================================================
    # HTTP CLIENT CORE METHODS
    # ==========================================================================

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure HTTP session is available."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            headers = dict(self.config.headers) if self.config.headers else {}

            # Add default headers
            headers.setdefault("User-Agent", "FlextApiClient/1.0")
            headers.setdefault("Content-Type", "application/json")

            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=headers,
            )

        return self._session

    async def _make_request(
        self,
        method: HttpMethod,
        url: str,
        data: object = None,
        headers: dict[str, str] | None = None,
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Make HTTP request with plugin processing."""
        start_time = time.time()
        self._stats["requests_made"] += 1

        try:
            # Create request object
            request_data = {
                "method": method.value,
                "url": url,
                "data": data,
                "headers": headers or {},
                "timestamp": FlextUtilities.generate_iso_timestamp(),
            }

            # Process through plugins (before request)
            for plugin in self.plugins:
                if hasattr(plugin, "before_request"):
                    result = await plugin.before_request(request_data)
                    if not result.is_success:
                        return FlextResult[FlextTypes.Core.JsonDict].fail(
                            f"Plugin {plugin.name} failed: {result.error}"
                        )
                    if isinstance(result.value, dict):
                        request_data.update(result.value)
                    else:
                        request_data = cast("FlextTypes.Core.JsonDict", result.value)

            # Make actual HTTP request
            session = await self._ensure_session()

            request_url = (
                urljoin(self.config.base_url, url) if self.config.base_url else url
            )
            request_headers = dict(self.config.headers) if self.config.headers else {}
            request_headers.update(headers or {})

            async with session.request(
                method.value,
                request_url,
                json=data
                if method in {HttpMethod.POST, HttpMethod.PUT, HttpMethod.PATCH}
                else None,
                headers=request_headers,
            ) as response:
                try:
                    response_data = await response.json()
                except Exception:
                    response_data = {"text": await response.text()}

                result_data = cast(
                    "FlextTypes.Core.JsonDict",
                    {
                        "status_code": response.status,
                        "data": response_data,
                        "headers": dict(response.headers),
                        "url": str(response.url),
                        "method": method.value,
                        "success": 200 <= response.status < 300,
                    },
                )

                # Process through plugins (after response)
                for plugin in self.plugins:
                    if hasattr(plugin, "after_response"):
                        plugin_result = await plugin.after_response(result_data)
                        if not plugin_result.is_success:
                            logger.warning(
                                "Plugin processing warning",
                                plugin=plugin.name,
                                error=plugin_result.error,
                            )

                # Update stats
                if result_data["success"]:
                    self._stats["requests_successful"] += 1
                else:
                    self._stats["requests_failed"] += 1

                self._stats["total_time"] += time.time() - start_time

                return FlextResult[FlextTypes.Core.JsonDict].ok(result_data)

        except Exception as e:
            self._stats["requests_failed"] += 1
            logger.exception(
                "HTTP request failed", method=method.value, url=url, error=str(e)
            )
            return FlextResult[FlextTypes.Core.JsonDict].fail(
                f"HTTP request failed: {e}"
            )

    # ==========================================================================
    # HTTP METHOD SHORTCUTS
    # ==========================================================================

    async def get(
        self, endpoint: str, headers: dict[str, str] | None = None
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Make GET request."""
        return await self._make_request(HttpMethod.GET, endpoint, headers=headers)

    async def post(
        self, endpoint: str, data: object = None, headers: dict[str, str] | None = None
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Make POST request."""
        return await self._make_request(
            HttpMethod.POST, endpoint, data=data, headers=headers
        )

    async def put(
        self, endpoint: str, data: object = None, headers: dict[str, str] | None = None
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Make PUT request."""
        return await self._make_request(
            HttpMethod.PUT, endpoint, data=data, headers=headers
        )

    async def patch(
        self, endpoint: str, data: object = None, headers: dict[str, str] | None = None
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Make PATCH request."""
        return await self._make_request(
            HttpMethod.PATCH, endpoint, data=data, headers=headers
        )

    async def delete(
        self, endpoint: str, headers: dict[str, str] | None = None
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Make DELETE request."""
        return await self._make_request(HttpMethod.DELETE, endpoint, headers=headers)

    # ==========================================================================
    # BUILDER FACTORY METHODS
    # ==========================================================================

    def get_builder(self) -> Builder:
        """Get builder factory for constructing queries and responses."""
        return self.Builder()

    def create_query_builder(self) -> QueryBuilder:
        """Create query builder directly."""
        return self.QueryBuilder()

    def create_response_builder(self) -> ResponseBuilder:
        """Create response builder directly."""
        return self.ResponseBuilder()

    def create_paginated_response_builder(self) -> PaginatedResponseBuilder:
        """Create paginated response builder directly."""
        return self.PaginatedResponseBuilder()

    # ==========================================================================
    # CLIENT LIFECYCLE MANAGEMENT
    # ==========================================================================

    async def close(self) -> None:
        """Close HTTP client and cleanup resources."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

        self._closed = True
        logger.info("FlextApiClient closed")

    def get_stats(self) -> dict[str, object]:
        """Get client statistics."""
        return dict(self._stats)

    def is_closed(self) -> bool:
        """Check if client is closed."""
        return self._closed

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        return self

    async def __aexit__(
        self, exc_type: object, exc_val: object, exc_tb: object
    ) -> None:
        """Async context manager exit."""
        await self.close()


# =============================================================================
# LEGACY ALIASES FOR BACKWARD COMPATIBILITY
# =============================================================================

# Operation class alias
FlextApiOperation = FlextApiClient.Operation

# Builder classes aliases
FlextApiBuilder = FlextApiClient.Builder
FlextApiQueryBuilder = FlextApiClient.QueryBuilder
FlextApiResponseBuilder = FlextApiClient.ResponseBuilder
PaginatedResponseBuilder = FlextApiClient.PaginatedResponseBuilder


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def create_client(
    config: dict[str, object] | ClientConfig | None = None,
) -> FlextApiClient:
    """Create HTTP client with configuration."""
    return FlextApiClient(config)


def build_query(**kwargs: object) -> FlextTypes.Core.JsonDict:
    """Build query using kwargs."""
    builder = FlextApiClient.QueryBuilder()

    if "filters" in kwargs:
        filters = cast("dict[str, object]", kwargs["filters"])
        builder = builder.with_filters(filters)

    if "page" in kwargs:
        page_value = kwargs["page"]
        if isinstance(page_value, int | str) and str(page_value).isdigit():
            builder = builder.page(int(page_value))

    if "page_size" in kwargs:
        page_size_value = kwargs["page_size"]
        if isinstance(page_size_value, int | str) and str(page_size_value).isdigit():
            builder = builder.page_size(int(page_size_value))

    if "search" in kwargs:
        builder = builder.search(str(kwargs["search"]))

    return builder.build()


def build_success_response(
    data: object = None, message: str = "Success"
) -> FlextTypes.Core.JsonDict:
    """Build success response."""
    return FlextApiClient.ResponseBuilder().success(data, message).build()


def build_error_response(
    message: str, status_code: int = 400
) -> FlextTypes.Core.JsonDict:
    """Build error response."""
    return FlextApiClient.ResponseBuilder().error(message, status_code).build()


def build_paginated_response(
    data: object,
    current_page: int,
    page_size: int,
    total_items: int,
    message: str = "Success",
) -> FlextTypes.Core.JsonDict:
    """Build paginated response."""
    return (
        FlextApiClient.PaginatedResponseBuilder()
        .success(data, message)
        .with_pagination(current_page, page_size, total_items)
        .build()
    )


# =============================================================================
# EXPORTS - Consolidated class first, then backward compatibility
# =============================================================================

__all__ = [
    "FlextApiBuilder",
    "FlextApiClient",
    "FlextApiClientConfig",
    "FlextApiClientMethod",
    "FlextApiClientRequest",
    "FlextApiClientResponse",
    "FlextApiClientStatus",
    "FlextApiOperation",
    "FlextApiQueryBuilder",
    "FlextApiResponseBuilder",
    "PaginatedResponseBuilder",
    "build_error_response",
    "build_paginated_response",
    "build_query",
    "build_success_response",
    "create_client",
]

"""FLEXT API Builder - Using flext-core structural patterns.

Uses FlextValueObject, make_builder, and other flext-core patterns
for maximum code reduction and structural alignment.
"""

from __future__ import annotations

import http
import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

import structlog

logger = structlog.get_logger(__name__)


# =====================================================================================
# CONFIGURATION CLASSES - Reducing Function Parameter Complexity
# =====================================================================================


@dataclass(frozen=True)
class ResponseConfig:
    """Configuration for response creation - reduces parameter complexity."""

    success: bool | None = None
    data: object = None
    message: str | None = None
    metadata: dict[str, object] | None = None
    pagination: dict[str, object] | None = None


@dataclass(frozen=True)
class PaginationConfig:
    """Configuration for pagination - simplifies paginated response creation."""

    data: object
    total: int
    page: int
    page_size: int
    message: str = "Success"
    metadata: dict[str, object] | None = None

    def __post_init__(self) -> None:
        """Validate pagination parameters."""
        if self.total < 0:
            msg = "Total must be non-negative"
            raise ValueError(msg)
        if self.page < 1:
            msg = "Page must be positive"
            raise ValueError(msg)
        if self.page_size < 1:
            msg = "Page size must be positive"
            raise ValueError(msg)


class FlextApiOperation(Enum):
    """Operations supported by the unified builder."""

    QUERY = "query"
    RESPONSE = "response"
    APP = "app"


@dataclass(frozen=True)
class FlextApiQuery:
    """Query value object using dataclass for immutability."""

    filters: list[dict[str, object]] = field(default_factory=list)
    sorts: list[dict[str, str]] = field(default_factory=list)
    page: int = 1
    page_size: int = 20

    def __post_init__(self) -> None:
        """Post-initialization validation."""
        if self.page <= 0:
            msg = "Page must be greater than 0"
            raise ValueError(msg)
        if self.page_size <= 0:
            msg = "Page size must be greater than 0"
            raise ValueError(msg)

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary format."""
        return {
            "filters": self.filters,
            "sorts": self.sorts,
            "page": self.page,
            "page_size": self.page_size,
            "limit": self.page_size,
            "offset": (self.page - 1) * self.page_size,
        }


@dataclass(frozen=True)
class FlextApiResponse:
    """Response value object using dataclass for immutability."""

    success: bool
    data: object = None
    message: str = ""
    metadata: dict[str, object] = field(default_factory=dict)
    timestamp: str = ""
    pagination: dict[str, object] | None = None

    def __post_init__(self) -> None:
        """Post-initialization with timestamp."""
        if not self.timestamp:
            object.__setattr__(self, "timestamp", datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary format."""
        result = {
            "success": self.success,
            "data": self.data,
            "message": self.message,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }

        if self.pagination:
            result["pagination"] = self.pagination

        return result


class FlextApiBuilder:
    """Unified builder using flext-core patterns."""

    def __init__(self) -> None:
        """Initialize builder."""
        self.logger = structlog.get_logger(__name__)

    def for_query(self) -> FlextApiQueryBuilder:
        """Create query builder."""
        return FlextApiQueryBuilder()

    def for_response(self) -> FlextApiResponseBuilder:
        """Create response builder."""
        return FlextApiResponseBuilder()


# Professional query builder with fluent interface
class FlextApiQueryBuilder:
    """Professional query builder using flext-core patterns."""

    def __init__(self) -> None:
        """Initialize query builder."""
        self._query = FlextApiQuery(
            filters=[],
            sorts=[],
            page=1,
            page_size=20,
        )

    def _validate_field(self, field: str) -> None:
        """DRY helper: Validate field name."""
        if not field or not field.strip():
            msg = "Field cannot be empty"
            raise ValueError(msg)

    def _add_filter(
        self, field: str, operator: str, value: object
    ) -> FlextApiQueryBuilder:
        """DRY helper: Add filter to query - reduces code duplication."""
        self._validate_field(field)
        self._query.filters.append(
            {
                "field": field,
                "operator": operator,
                "value": value,
            }
        )
        return self

    def _add_sort(self, field: str, direction: str) -> FlextApiQueryBuilder:
        """DRY helper: Add sort to query - reduces code duplication."""
        self._validate_field(field)
        self._query.sorts.append({"field": field, "direction": direction})
        return self

    def equals(self, field: str, value: object) -> FlextApiQueryBuilder:
        """Add equals filter."""
        return self._add_filter(field, "equals", value)

    def greater_than(self, field: str, value: object) -> FlextApiQueryBuilder:
        """Add greater than filter."""
        return self._add_filter(field, "gt", value)

    def sort_desc(self, field: str) -> FlextApiQueryBuilder:
        """Add descending sort."""
        return self._add_sort(field, "desc")

    def sort_asc(self, field: str) -> FlextApiQueryBuilder:
        """Add ascending sort."""
        return self._add_sort(field, "asc")

    def _validate_page(self, page: int) -> None:
        """DRY helper: Validate page number."""
        if page <= 0:
            msg = "Page must be greater than 0"
            raise ValueError(msg)

    def _validate_page_size(self, size: int) -> None:
        """DRY helper: Validate page size."""
        if size <= 0:
            msg = "Page size must be greater than 0"
            raise ValueError(msg)

    def _rebuild_query_with_pagination(
        self, page: int | None = None, page_size: int | None = None
    ) -> None:
        """DRY helper: Rebuild query with new pagination values."""
        self._query = FlextApiQuery(
            filters=self._query.filters,
            sorts=self._query.sorts,
            page=page if page is not None else self._query.page,
            page_size=page_size if page_size is not None else self._query.page_size,
        )

    def page(self, page: int) -> FlextApiQueryBuilder:
        """Set page number."""
        self._validate_page(page)
        self._rebuild_query_with_pagination(page=page)
        return self

    def page_size(self, size: int) -> FlextApiQueryBuilder:
        """Set page size."""
        self._validate_page_size(size)
        self._rebuild_query_with_pagination(page_size=size)
        return self

    def pagination(self, page: int, size: int) -> FlextApiQueryBuilder:
        """Set pagination (both page and size)."""
        self._validate_page(page)
        self._validate_page_size(size)
        self._rebuild_query_with_pagination(page=page, page_size=size)
        return self

    def build(self) -> FlextApiQuery:
        """Build query object."""
        return self._query


# Professional response builder with fluent interface
class FlextApiResponseBuilder:
    """Professional response builder using flext-core patterns."""

    def __init__(self) -> None:
        """Initialize response builder."""
        self._response = FlextApiResponse(
            success=True,
            message="Success",
            metadata={},
        )

    def _create_response(self, config: ResponseConfig) -> None:
        """DRY helper to create response using configuration object."""
        # Use helper methods to reduce conditional complexity
        self._response = FlextApiResponse(
            success=self._resolve_success(config),
            data=self._resolve_data(config),
            message=self._resolve_message(config),
            metadata=self._resolve_metadata(config),
            pagination=self._resolve_pagination(config),
        )

    def _resolve_success(self, config: ResponseConfig) -> bool:
        """DRY helper: Resolve success value."""
        return config.success if config.success is not None else self._response.success

    def _resolve_data(self, config: ResponseConfig) -> object:
        """DRY helper: Resolve data value."""
        return config.data if config.data is not None else self._response.data

    def _resolve_message(self, config: ResponseConfig) -> str:
        """DRY helper: Resolve message value."""
        return config.message if config.message is not None else self._response.message

    def _resolve_metadata(self, config: ResponseConfig) -> dict[str, object]:
        """DRY helper: Resolve metadata value."""
        return (
            config.metadata if config.metadata is not None else self._response.metadata
        )

    def _resolve_pagination(self, config: ResponseConfig) -> dict[str, object] | None:
        """DRY helper: Resolve pagination value."""
        return (
            config.pagination
            if config.pagination is not None
            else self._response.pagination
        )

    def _create_response_legacy(
        self,
        config: ResponseConfig,
    ) -> None:
        """Legacy method - uses ResponseConfig directly.

        Refactored to eliminate parameter explosion using Parameter Object pattern.
        Reduces function parameters from 6 to 2 (self + config).
        """
        self._create_response(config)

    def success(
        self,
        data: object = None,
        message: str = "Success",
    ) -> FlextApiResponseBuilder:
        """Set success response."""
        config = ResponseConfig(success=True, data=data, message=message)
        self._create_response(config)
        return self

    def error(
        self,
        message: str,
        code: int = http.HTTPStatus.INTERNAL_SERVER_ERROR.value,
    ) -> FlextApiResponseBuilder:
        """Set error response."""
        metadata = dict(self._response.metadata)
        metadata["error_code"] = code
        config = ResponseConfig(success=False, message=message, metadata=metadata)
        self._create_response(config)
        return self

    def with_metadata(self, key: str, value: object) -> FlextApiResponseBuilder:
        """Add metadata."""
        metadata = dict(self._response.metadata)
        metadata[key] = value
        config = ResponseConfig(metadata=metadata)
        self._create_response(config)
        return self

    def _validate_pagination_params(
        self, total: int, page: int, page_size: int
    ) -> None:
        """DRY helper: Validate pagination parameters."""
        if total < 0:
            msg = "Total must be positive"
            raise ValueError(msg)
        if page <= 0:
            msg = "Page must be greater than 0"
            raise ValueError(msg)
        if page_size <= 0:
            msg = "Page size must be greater than 0"
            raise ValueError(msg)

    def _create_pagination_data(
        self, total: int, page: int, page_size: int
    ) -> dict[str, object]:
        """DRY helper: Create pagination data dictionary."""
        total_pages = math.ceil(total / page_size) if page_size > 0 else 0
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
        }

    def with_pagination(
        self,
        total: int,
        page: int,
        page_size: int,
    ) -> FlextApiResponseBuilder:
        """Add pagination metadata."""
        self._validate_pagination_params(total, page, page_size)
        pagination = self._create_pagination_data(total, page, page_size)

        # Add pagination data to metadata for test compatibility
        metadata = dict(self._response.metadata)
        metadata.update(pagination)

        config = ResponseConfig(metadata=metadata, pagination=pagination)
        self._create_response(config)
        return self

    def metadata(self, metadata: dict[str, object]) -> FlextApiResponseBuilder:
        """Set metadata (replaces existing metadata)."""
        config = ResponseConfig(metadata=metadata)
        self._create_response(config)
        return self

    def pagination(
        self,
        *,
        page: int,
        page_size: int,
        total: int,
    ) -> FlextApiResponseBuilder:
        """Set pagination (simplified for tests)."""
        return self.with_pagination(total=total, page=page, page_size=page_size)

    def build(self) -> FlextApiResponse:
        """Build response object."""
        return self._response


# Factory functions using flext-core patterns
def build_query(
    filters: list[dict[str, object]] | dict[str, object] | None = None,
) -> FlextApiQuery:
    """Build query from filters list or dict."""
    builder = FlextApiQueryBuilder()

    if filters:
        if isinstance(filters, dict):
            # Convert simple dict to filter format
            for field, value in filters.items():
                builder.equals(field, value)
        else:
            # Handle list of filter dictionaries
            for filter_item in filters:
                field = str(filter_item["field"])
                operator = str(filter_item["operator"])
                value = filter_item["value"]

                if operator == "equals":
                    builder.equals(field, value)
                elif operator == "gt":
                    builder.greater_than(field, value)
                # Add more operators as needed

    return builder.build()


def build_query_dict(
    filters: list[dict[str, object]] | dict[str, object] | None = None,
) -> dict[str, object]:
    """Build query from filters list or dict and return as dict."""
    return build_query(filters).to_dict()


def build_success_response(
    data: object = None,
    message: str = "Success",
    metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    """Build success response."""
    builder = FlextApiResponseBuilder().success(data=data, message=message)

    if metadata:
        for key, value in metadata.items():
            builder.with_metadata(key, value)

    return builder.build().to_dict()


def build_error_response(
    message: str,
    code: int = http.HTTPStatus.INTERNAL_SERVER_ERROR.value,
    details: object = None,
) -> dict[str, object]:
    """Build error response."""
    builder = FlextApiResponseBuilder().error(message, code)

    if details:
        builder.with_metadata("details", details)

    return builder.build().to_dict()


def build_paginated_response(
    config: PaginationConfig,
) -> dict[str, object]:
    """Build paginated response using PaginationConfig to reduce complexity."""
    builder = (
        FlextApiResponseBuilder()
        .success(data=config.data, message=config.message)
        .with_pagination(config.total, config.page, config.page_size)
    )

    if config.metadata:
        for key, value in config.metadata.items():
            builder.with_metadata(key, value)

    return builder.build().to_dict()


class PaginatedResponseBuilder:
    """Builder Pattern for paginated responses - eliminates 7-parameter complexity.

    SOLID Builder Pattern: Provides fluent interface for building paginated responses
    reducing parameter explosion and improving maintainability.
    """

    def __init__(self) -> None:
        """Initialize builder with default values."""
        self._data: object = None
        self._total: int = 0
        self._page: int = 1
        self._page_size: int = 20
        self._message: str = "Success"
        self._metadata: dict[str, object] | None = None

    def with_data(self, data: object) -> PaginatedResponseBuilder:
        """Set the response data."""
        self._data = data
        return self

    def with_total(self, total: int) -> PaginatedResponseBuilder:
        """Set the total count."""
        self._total = total
        return self

    def with_page(self, page: int) -> PaginatedResponseBuilder:
        """Set the current page number."""
        self._page = page
        return self

    def with_page_size(self, page_size: int) -> PaginatedResponseBuilder:
        """Set the page size."""
        self._page_size = page_size
        return self

    def with_message(self, message: str) -> PaginatedResponseBuilder:
        """Set the response message."""
        self._message = message
        return self

    def with_metadata(
        self, metadata: dict[str, object] | None
    ) -> PaginatedResponseBuilder:
        """Set the response metadata."""
        self._metadata = metadata
        return self

    def build(self) -> dict[str, object]:
        """Build the paginated response using PaginationConfig."""
        config = PaginationConfig(
            data=self._data,
            total=self._total,
            page=self._page,
            page_size=self._page_size,
            message=self._message,
            metadata=self._metadata,
        )
        return build_paginated_response(config)


def build_paginated_response_legacy(  # noqa: PLR0913
    data: object,
    total: int,
    page: int,
    page_size: int,
    message: str = "Success",
    metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    """Legacy build paginated response using Builder Pattern - eliminates explosion.

    DEPRECATED: Use PaginatedResponseBuilder or build_paginated_response with
    PaginationConfig for better maintainability and fluent interface.
    """
    return (
        PaginatedResponseBuilder()
        .with_data(data)
        .with_total(total)
        .with_page(page)
        .with_page_size(page_size)
        .with_message(message)
        .with_metadata(metadata)
        .build()
    )


def build_success_response_object(
    data: object = None,
    message: str = "Success",
    metadata: dict[str, object] | None = None,
) -> FlextApiResponse:
    """Build success response as object."""
    builder = FlextApiResponseBuilder().success(data=data, message=message)

    if metadata:
        for key, value in metadata.items():
            builder.with_metadata(key, value)

    return builder.build()


def build_error_response_object(
    message: str,
    code: int = http.HTTPStatus.INTERNAL_SERVER_ERROR.value,
    details: object = None,
) -> FlextApiResponse:
    """Build error response as object."""
    builder = FlextApiResponseBuilder().error(message, code)

    if details:
        builder.with_metadata("details", details)

    return builder.build()


def build_paginated_response_object(
    config: PaginationConfig,
) -> FlextApiResponse:
    """Build paginated response as object using PaginationConfig."""
    builder = (
        FlextApiResponseBuilder()
        .success(data=config.data, message=config.message)
        .with_pagination(config.total, config.page, config.page_size)
    )

    if config.metadata:
        for key, value in config.metadata.items():
            builder.with_metadata(key, value)

    return builder.build()


def build_paginated_response_object_legacy(  # noqa: PLR0913
    data: object,
    total: int,
    page: int,
    page_size: int,
    message: str = "Success",
    metadata: dict[str, object] | None = None,
) -> FlextApiResponse:
    """Legacy build paginated response as object using PaginationConfig.

    DEPRECATED: Use PaginatedResponseBuilder for fluent interface or
    build_paginated_response_object with PaginationConfig for better maintainability.
    """
    config = PaginationConfig(
        data=data,
        total=total,
        page=page,
        page_size=page_size,
        message=message,
        metadata=metadata,
    )
    return build_paginated_response_object(config)

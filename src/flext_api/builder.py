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

    def equals(self, field: str, value: object) -> FlextApiQueryBuilder:
        """Add equals filter."""
        if not field or not field.strip():
            msg = "Field cannot be empty"
            raise ValueError(msg)
        self._query.filters.append(
            {
                "field": field,
                "operator": "equals",
                "value": value,
            },
        )
        return self

    def greater_than(self, field: str, value: object) -> FlextApiQueryBuilder:
        """Add greater than filter."""
        if not field or not field.strip():
            msg = "Field cannot be empty"
            raise ValueError(msg)
        self._query.filters.append(
            {
                "field": field,
                "operator": "gt",
                "value": value,
            },
        )
        return self

    def sort_desc(self, field: str) -> FlextApiQueryBuilder:
        """Add descending sort."""
        if not field or not field.strip():
            msg = "Field cannot be empty"
            raise ValueError(msg)
        self._query.sorts.append({"field": field, "direction": "desc"})
        return self

    def sort_asc(self, field: str) -> FlextApiQueryBuilder:
        """Add ascending sort."""
        if not field or not field.strip():
            msg = "Field cannot be empty"
            raise ValueError(msg)
        self._query.sorts.append({"field": field, "direction": "asc"})
        return self

    def page(self, page: int) -> FlextApiQueryBuilder:
        """Set page number."""
        if page <= 0:
            msg = "Page must be greater than 0"
            raise ValueError(msg)
        # Create new query with updated page
        self._query = FlextApiQuery(
            filters=self._query.filters,
            sorts=self._query.sorts,
            page=page,
            page_size=self._query.page_size,
        )
        return self

    def page_size(self, size: int) -> FlextApiQueryBuilder:
        """Set page size."""
        if size <= 0:
            msg = "Page size must be greater than 0"
            raise ValueError(msg)
        # Create new query with updated page size
        self._query = FlextApiQuery(
            filters=self._query.filters,
            sorts=self._query.sorts,
            page=self._query.page,
            page_size=size,
        )
        return self

    def pagination(self, page: int, size: int) -> FlextApiQueryBuilder:
        """Set pagination (both page and size)."""
        if page <= 0:
            msg = "Page must be greater than 0"
            raise ValueError(msg)
        if size <= 0:
            msg = "Page size must be greater than 0"
            raise ValueError(msg)
        # Create new query with updated pagination
        self._query = FlextApiQuery(
            filters=self._query.filters,
            sorts=self._query.sorts,
            page=page,
            page_size=size,
        )
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

    def _create_response(
        self,
        *,
        success: bool | None = None,
        data: object = None,
        message: str | None = None,
        metadata: dict[str, object] | None = None,
        pagination: dict[str, object] | None = None,
    ) -> None:
        """DRY helper to create response with current values as defaults."""
        current_pagination = self._response.pagination
        self._response = FlextApiResponse(
            success=success if success is not None else self._response.success,
            data=data if data is not None else self._response.data,
            message=message if message is not None else self._response.message,
            metadata=metadata if metadata is not None else self._response.metadata,
            pagination=pagination if pagination is not None else current_pagination,
        )

    def success(
        self,
        data: object = None,
        message: str = "Success",
    ) -> FlextApiResponseBuilder:
        """Set success response."""
        self._create_response(success=True, data=data, message=message)
        return self

    def error(
        self,
        message: str,
        code: int = http.HTTPStatus.INTERNAL_SERVER_ERROR.value,
    ) -> FlextApiResponseBuilder:
        """Set error response."""
        metadata = dict(self._response.metadata)
        metadata["error_code"] = code
        self._create_response(success=False, message=message, metadata=metadata)
        return self

    def with_metadata(self, key: str, value: object) -> FlextApiResponseBuilder:
        """Add metadata."""
        metadata = dict(self._response.metadata)
        metadata[key] = value
        self._create_response(metadata=metadata)
        return self

    def with_pagination(
        self,
        total: int,
        page: int,
        page_size: int,
    ) -> FlextApiResponseBuilder:
        """Add pagination metadata."""
        if total < 0:
            msg = "Total must be positive"
            raise ValueError(msg)
        if page <= 0:
            msg = "Page must be greater than 0"
            raise ValueError(msg)
        if page_size <= 0:
            msg = "Page size must be greater than 0"
            raise ValueError(msg)

        total_pages = math.ceil(total / page_size) if page_size > 0 else 0
        pagination: dict[str, object] = {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
        }

        # Add pagination data to metadata for test compatibility
        metadata = dict(self._response.metadata)
        metadata.update(pagination)

        self._create_response(metadata=metadata, pagination=pagination)
        return self

    def metadata(self, metadata: dict[str, object]) -> FlextApiResponseBuilder:
        """Set metadata (replaces existing metadata)."""
        self._create_response(metadata=metadata)
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


def build_paginated_response(  # noqa: PLR0913
    data: object,
    total: int,
    page: int,
    page_size: int,
    message: str = "Success",
    metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    """Build paginated response."""
    builder = (
        FlextApiResponseBuilder()
        .success(data=data, message=message)
        .with_pagination(total, page, page_size)
    )

    if metadata:
        for key, value in metadata.items():
            builder.with_metadata(key, value)

    return builder.build().to_dict()


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


def build_paginated_response_object(  # noqa: PLR0913
    data: object,
    total: int,
    page: int,
    page_size: int,
    message: str = "Success",
    metadata: dict[str, object] | None = None,
) -> FlextApiResponse:
    """Build paginated response as object."""
    builder = (
        FlextApiResponseBuilder()
        .success(data=data, message=message)
        .with_pagination(total, page, page_size)
    )

    if metadata:
        for key, value in metadata.items():
            builder.with_metadata(key, value)

    return builder.build()

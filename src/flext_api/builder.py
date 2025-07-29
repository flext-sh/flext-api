"""FLEXT API Builder - Using flext-core structural patterns.

Uses FlextValueObject, make_builder, and other flext-core patterns
for maximum code reduction and structural alignment.
"""

from __future__ import annotations

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
            msg = "Page must be positive"
            raise ValueError(msg)
        if self.page_size <= 0:
            msg = "Page size must be positive"
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
        self._query.filters.append({
            "field": field, "operator": "equals", "value": value,
        })
        return self

    def greater_than(self, field: str, value: object) -> FlextApiQueryBuilder:
        """Add greater than filter."""
        if not field or not field.strip():
            msg = "Field cannot be empty"
            raise ValueError(msg)
        self._query.filters.append({
            "field": field, "operator": "greater_than", "value": value,
        })
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

    def page(self, page: int, size: int) -> FlextApiQueryBuilder:
        """Set pagination."""
        if page <= 0:
            msg = "Page must be positive"
            raise ValueError(msg)
        if size <= 0:
            msg = "Page size must be positive"
            raise ValueError(msg)
        # Create new query with updated pagination
        self._query = FlextApiQuery(
            filters=self._query.filters,
            sorts=self._query.sorts,
            page=page,
            page_size=size,
        )
        return self

    def build(self) -> dict[str, object]:
        """Build query dictionary."""
        return self._query.to_dict()


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

    def success(
        self, *, data: object = None, message: str = "Success",
    ) -> FlextApiResponseBuilder:
        """Set success response."""
        self._response = FlextApiResponse(
            success=True,
            data=data,
            message=message,
            metadata=self._response.metadata,
            pagination=self._response.pagination,
        )
        return self

    def error(self, message: str, code: int = 500) -> FlextApiResponseBuilder:
        """Set error response."""
        metadata = dict(self._response.metadata)
        metadata["error_code"] = code
        self._response = FlextApiResponse(
            success=False,
            message=message,
            metadata=metadata,
            pagination=self._response.pagination,
        )
        return self

    def with_metadata(self, key: str, value: object) -> FlextApiResponseBuilder:
        """Add metadata."""
        metadata = dict(self._response.metadata)
        metadata[key] = value
        self._response = FlextApiResponse(
            success=self._response.success,
            data=self._response.data,
            message=self._response.message,
            metadata=metadata,
            pagination=self._response.pagination,
        )
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
            msg = "Page must be positive"
            raise ValueError(msg)
        if page_size <= 0:
            msg = "Page size must be positive"
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

        self._response = FlextApiResponse(
            success=self._response.success,
            data=self._response.data,
            message=self._response.message,
            metadata=self._response.metadata,
            pagination=pagination,
        )
        return self

    def build(self) -> dict[str, object]:
        """Build response dictionary."""
        return self._response.to_dict()


# Factory functions using flext-core patterns
def build_query(filters: dict[str, object] | None = None) -> dict[str, object]:
    """Build query from filters dictionary."""
    builder = FlextApiQueryBuilder()

    if filters:
        for field, value in filters.items():
            builder.equals(field, value)

    return builder.build()


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

    return builder.build()


def build_error_response(
    message: str,
    code: int = 500,
    details: object = None,
) -> dict[str, object]:
    """Build error response."""
    builder = FlextApiResponseBuilder().error(message, code)

    if details:
        builder.with_metadata("details", details)

    return builder.build()


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

    return builder.build()

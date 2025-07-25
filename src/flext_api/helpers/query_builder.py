"""FlextQueryBuilder - Powerful Query Construction Utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Advanced query builder for database operations and filtering.
"""

from __future__ import annotations

import contextlib
import warnings
from enum import Enum
from typing import Any

from flext_core import FlextResult


class FlextApiQueryOperator(Enum):
    """FlextApi query operators for filtering."""

    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"
    IN = "in"
    NOT_IN = "not_in"
    LIKE = "like"
    ILIKE = "ilike"  # Case-insensitive like
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    CONTAINS = "contains"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"
    BETWEEN = "between"


class FlextApiSortDirection(Enum):
    """FlextApi sort directions."""

    ASC = "asc"
    DESC = "desc"


class FlextApiQueryFilter:
    """FlextApi individual query filter."""

    def __init__(
        self,
        field: str,
        operator: FlextApiQueryOperator,
        value: Any = None,
    ) -> None:
        """Initialize filter.

        Args:
            field: Field name to filter on
            operator: Query operator
            value: Filter value (not needed for IS_NULL/IS_NOT_NULL)

        """
        self.field = field
        self.operator = operator
        self.value = value

    def to_dict(self) -> dict[str, Any]:
        """Convert filter to dictionary."""
        result = {
            "field": self.field,
            "operator": self.operator.value,
        }
        if self.value is not None:
            result["value"] = self.value
        return result


class FlextApiQuerySort:
    """FlextApi query sort specification."""

    def __init__(
        self, field: str, direction: FlextApiSortDirection = FlextApiSortDirection.ASC
    ) -> None:
        """Initialize sort.

        Args:
            field: Field name to sort by
            direction: Sort direction

        """
        self.field = field
        self.direction = direction

    def to_dict(self) -> dict[str, Any]:
        """Convert sort to dictionary."""
        return {
            "field": self.field,
            "direction": self.direction.value,
        }


class FlextApiQueryBuilder:
    """FlextApi powerful query builder for database operations.

    Provides a fluent interface for building complex queries with
    filtering, sorting, pagination, and more.

    Example:
        query = (FlextQueryBuilder()
                 .filter("status", FlextApiQueryOperator.EQUALS, "active")
                 .filter("created_at", FlextApiQueryOperator.GREATER_THAN, "2024-01-01")
                 .sort("name", FlextApiSortDirection.ASC)
                 .paginate(page=1, size=50)
                 .build())

        # Use with repository
        users = await user_repository.find_by_query(query)

    """

    def __init__(self) -> None:
        """Initialize query builder."""
        self._filters: list[FlextQueryFilter] = []
        self._sorts: list[FlextQuerySort] = []
        self._page: int | None = None
        self._page_size: int | None = None
        self._limit: int | None = None
        self._offset: int | None = None
        self._fields: list[str] | None = None
        self._include_total: bool = False
        self._metadata: dict[str, Any] = {}

    def filter(
        self,
        field: str,
        operator: FlextApiQueryOperator,
        value: Any = None,
    ) -> FlextApiQueryBuilder:
        """Add filter condition."""
        self._filters.append(FlextApiQueryFilter(field, operator, value))
        return self

    def equals(self, field: str, value: Any) -> FlextApiQueryBuilder:
        """Add equals filter."""
        return self.filter(field, FlextApiQueryOperator.EQUALS, value)

    def not_equals(self, field: str, value: Any) -> FlextApiQueryBuilder:
        """Add not equals filter."""
        return self.filter(field, FlextApiQueryOperator.NOT_EQUALS, value)

    def greater_than(self, field: str, value: Any) -> FlextApiQueryBuilder:
        """Add greater than filter."""
        return self.filter(field, FlextApiQueryOperator.GREATER_THAN, value)

    def less_than(self, field: str, value: Any) -> FlextApiQueryBuilder:
        """Add less than filter."""
        return self.filter(field, FlextApiQueryOperator.LESS_THAN, value)

    def in_values(self, field: str, values: list[Any]) -> FlextApiQueryBuilder:
        """Add IN filter."""
        return self.filter(field, FlextApiQueryOperator.IN, values)

    def like(self, field: str, pattern: str) -> FlextApiQueryBuilder:
        """Add LIKE filter."""
        return self.filter(field, FlextApiQueryOperator.LIKE, pattern)

    def contains(self, field: str, value: str) -> FlextApiQueryBuilder:
        """Add contains filter."""
        return self.filter(field, FlextApiQueryOperator.CONTAINS, value)

    def is_null(self, field: str) -> FlextApiQueryBuilder:
        """Add IS NULL filter."""
        return self.filter(field, FlextApiQueryOperator.IS_NULL)

    def is_not_null(self, field: str) -> FlextApiQueryBuilder:
        """Add IS NOT NULL filter."""
        return self.filter(field, FlextApiQueryOperator.IS_NOT_NULL)

    def between(self, field: str, start: Any, end: Any) -> FlextApiQueryBuilder:
        """Add BETWEEN filter."""
        return self.filter(field, FlextApiQueryOperator.BETWEEN, [start, end])

    def sort(
        self, field: str, direction: FlextApiSortDirection = FlextApiSortDirection.ASC
    ) -> FlextApiQueryBuilder:
        """Add sort condition."""
        self._sorts.append(FlextApiQuerySort(field, direction))
        return self

    def sort_asc(self, field: str) -> FlextApiQueryBuilder:
        """Add ascending sort."""
        return self.sort(field, FlextApiSortDirection.ASC)

    def sort_desc(self, field: str) -> FlextApiQueryBuilder:
        """Add descending sort."""
        return self.sort(field, FlextApiSortDirection.DESC)

    def paginate(self, page: int, size: int) -> FlextApiQueryBuilder:
        """Add pagination."""
        self._page = page
        self._page_size = size
        return self

    def limit(self, limit: int) -> FlextApiQueryBuilder:
        """Add limit."""
        self._limit = limit
        return self

    def offset(self, offset: int) -> FlextApiQueryBuilder:
        """Add offset."""
        self._offset = offset
        return self

    def select_fields(self, *fields: str) -> FlextApiQueryBuilder:
        """Select specific fields."""
        self._fields = list(fields)
        return self

    def include_total_count(self) -> FlextApiQueryBuilder:
        """Include total count in results."""
        self._include_total = True
        return self

    def with_metadata(self, key: str, value: Any) -> FlextApiQueryBuilder:
        """Add custom metadata."""
        self._metadata[key] = value
        return self

    def build(self) -> dict[str, Any]:
        """Build and return query dictionary."""
        query = {
            "filters": [f.to_dict() for f in self._filters],
            "sorts": [s.to_dict() for s in self._sorts],
        }

        # Add pagination
        if self._page is not None and self._page_size is not None:
            query["pagination"] = {
                "page": self._page,
                "page_size": self._page_size,
            }

        if self._limit is not None:
            query["limit"] = self._limit

        if self._offset is not None:
            query["offset"] = self._offset

        # Add field selection
        if self._fields:
            query["fields"] = self._fields

        # Add options
        if self._include_total:
            query["include_total"] = True

        # Add metadata
        query.update(self._metadata)

        return query

    def reset(self) -> FlextApiQueryBuilder:
        """Reset query builder."""
        self._filters.clear()
        self._sorts.clear()
        self._page = None
        self._page_size = None
        self._limit = None
        self._offset = None
        self._fields = None
        self._include_total = False
        self._metadata.clear()
        return self


# Convenience functions
def flext_api_create_filter(
    field: str, operator: FlextApiQueryOperator, value: Any = None
) -> FlextApiQueryFilter:
    """Create a single filter."""
    return FlextApiQueryFilter(field, operator, value)


def flext_api_create_sort(
    field: str, direction: FlextApiSortDirection = FlextApiSortDirection.ASC
) -> FlextApiQuerySort:
    """Create a single sort."""
    return FlextApiQuerySort(field, direction)


def flext_api_build_simple_query(
    filters: dict[str, Any] | None = None,
    sorts: dict[str, str] | None = None,
    page: int | None = None,
    page_size: int | None = None,
) -> dict[str, Any]:
    """Build a simple query from dictionaries.

    Args:
        filters: Dictionary of field->value filters (uses EQUALS)
        sorts: Dictionary of field->direction sorts
        page: Page number
        page_size: Page size

    Returns:
        Query dictionary

    """
    builder = FlextApiQueryBuilder()

    # Add filters
    if filters:
        for field, value in filters.items():
            builder.equals(field, value)

    # Add sorts
    if sorts:
        for field, direction in sorts.items():
            sort_dir = (
                FlextApiSortDirection.DESC
                if direction.lower() == "desc"
                else FlextApiSortDirection.ASC
            )
            builder.sort(field, sort_dir)

    # Add pagination
    if page is not None and page_size is not None:
        builder.paginate(page, page_size)

    return builder.build()


def flext_api_parse_query_params(params: dict[str, Any]) -> FlextApiQueryBuilder:
    """Parse query parameters into FlextQueryBuilder.

    Supports common query parameter patterns:
    - filter[field]=value (equals)
    - filter[field][operator]=value
    - sort=field:direction
    - page=1&page_size=50

    Args:
        params: Query parameters dictionary

    Returns:
        Configured FlextQueryBuilder

    """
    builder = FlextApiQueryBuilder()

    # Parse filters
    for key, value in params.items():
        if key.startswith("filter[") and key.endswith("]"):
            # Extract field name
            field_part = key[7:-1]  # Remove "filter[" and "]"

            if "[" in field_part and field_part.endswith("]"):
                # filter[field][operator]=value
                field, operator_part = field_part.split("[", 1)
                operator_str = operator_part[:-1]  # Remove "]"

                try:
                    operator = FlextApiQueryOperator(operator_str)
                    builder.filter(field, operator, value)
                except ValueError:
                    # Unknown operator, default to equals
                    builder.equals(field, value)
            else:
                # filter[field]=value (equals)
                builder.equals(field_part, value)

    # Parse sorts
    if "sort" in params:
        sort_param = params["sort"]
        if isinstance(sort_param, str):
            if ":" in sort_param:
                field, direction = sort_param.split(":", 1)
                sort_dir = (
                    FlextApiSortDirection.DESC
                    if direction.lower() == "desc"
                    else FlextApiSortDirection.ASC
                )
                builder.sort(field, sort_dir)
            else:
                builder.sort_asc(sort_param)

    # Parse pagination
    if "page" in params and "page_size" in params:
        try:
            page = int(params["page"])
            page_size = int(params["page_size"])
            builder.paginate(page, page_size)
        except (ValueError, TypeError):
            pass  # Invalid pagination params, ignore

    # Parse limit/offset
    if "limit" in params:
        with contextlib.suppress(ValueError, TypeError):
            builder.limit(int(params["limit"]))

    if "offset" in params:
        with contextlib.suppress(ValueError, TypeError):
            builder.offset(int(params["offset"]))

    return builder


# ===== LEGACY COMPATIBILITY ALIASES =====
# These will be deprecated in future versions


def _deprecation_warning(old_name: str, new_name: str) -> None:
    """Issue deprecation warning."""
    warnings.warn(
        f"{old_name} is deprecated, use {new_name} instead",
        DeprecationWarning,
        stacklevel=3,
    )


# Legacy class aliases
QueryOperator = FlextApiQueryOperator
SortDirection = FlextApiSortDirection
FlextQueryBuilder = FlextApiQueryBuilder
FlextQueryFilter = FlextApiQueryFilter
FlextQuerySort = FlextApiQuerySort


# Legacy function aliases
def build_simple_query(*args: Any, **kwargs: object) -> Any:
    """Legacy wrapper with deprecation warning."""
    _deprecation_warning("build_simple_query", "flext_api_build_simple_query")
    return flext_api_build_simple_query(*args, **kwargs)


def parse_query_params(*args: Any, **kwargs: object) -> Any:
    """Legacy wrapper with deprecation warning."""
    _deprecation_warning("parse_query_params", "flext_api_parse_query_params")
    return flext_api_parse_query_params(*args, **kwargs)


def create_filter(*args: Any, **kwargs: object) -> Any:
    """Legacy wrapper with deprecation warning."""
    _deprecation_warning("create_filter", "flext_api_create_filter")
    return flext_api_create_filter(*args, **kwargs)


def create_sort(*args: Any, **kwargs: object) -> Any:
    """Legacy wrapper with deprecation warning."""
    _deprecation_warning("create_sort", "flext_api_create_sort")
    return flext_api_create_sort(*args, **kwargs)

"""FLEXT API Builders System.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import cast

from flext_core import FlextResult, get_logger

logger = get_logger(__name__)


class FlextApiBuilder:
    """Base builder for API operations following FLEXT patterns."""

    def __init__(self) -> None:
        """Initialize builder."""
        self._data: dict[str, object] = {}

    def build(self) -> FlextResult[dict[str, object]]:
        """Build the final object."""
        return FlextResult[dict[str, object]].ok(self._data.copy())


class FlextApiQueryBuilder(FlextApiBuilder):
    """Query builder for constructing API queries."""

    def __init__(self) -> None:
        """Initialize query builder."""
        super().__init__()
        self._filters: dict[str, object] = {}
        self._sorting: list[dict[str, str]] = []
        self._pagination: dict[str, int] = {}

    def add_filter(self, field: str, value: object, operator: str = "eq") -> FlextApiQueryBuilder:
        """Add filter to query."""
        self._filters[field] = {"value": value, "operator": operator}
        return self

    def add_sort(self, field: str, direction: str = "asc") -> FlextApiQueryBuilder:
        """Add sorting to query."""
        self._sorting.append({"field": field, "direction": direction})
        return self

    def set_pagination(self, page: int = 1, size: int = 20) -> FlextApiQueryBuilder:
        """Set pagination parameters."""
        self._pagination = {"page": page, "size": size}
        return self

    def build_query(self) -> FlextResult[dict[str, object]]:
        """Build the complete query."""
        try:
            query = cast("dict[str, object]", {
                "filters": self._filters,
                "sorting": self._sorting,
                "pagination": self._pagination,
            })

            logger.debug("Query built successfully",
                        filters_count=len(self._filters),
                        sorts_count=len(self._sorting),
                        has_pagination=bool(self._pagination))

            return FlextResult[dict[str, object]].ok(query)

        except Exception as e:
            logger.exception("Query build failed", error=str(e))
            return FlextResult[dict[str, object]].fail(f"Query build error: {e}")

    def reset(self) -> FlextApiQueryBuilder:
        """Reset builder to initial state."""
        self._filters.clear()
        self._sorting.clear()
        self._pagination.clear()
        return self


class FlextApiResponseBuilder(FlextApiBuilder):
    """Response builder for constructing API responses."""

    def __init__(self) -> None:
        """Initialize response builder."""
        super().__init__()
        self._status_code: int = 200
        self._headers: dict[str, str] = {}
        self._body: object = None
        self._metadata: dict[str, object] = {}

    def set_status_code(self, code: int) -> FlextApiResponseBuilder:
        """Set response status code."""
        self._status_code = code
        return self

    def add_header(self, name: str, value: str) -> FlextApiResponseBuilder:
        """Add response header."""
        self._headers[name] = value
        return self

    def set_body(self, body: object) -> FlextApiResponseBuilder:
        """Set response body."""
        self._body = body
        return self

    def add_metadata(self, key: str, value: object) -> FlextApiResponseBuilder:
        """Add metadata to response."""
        self._metadata[key] = value
        return self

    def build_response(self) -> FlextResult[dict[str, object]]:
        """Build the complete response."""
        try:
            response = cast("dict[str, object]", {
                "status_code": self._status_code,
                "headers": self._headers.copy(),
                "body": self._body,
                "metadata": self._metadata.copy(),
            })

            logger.debug("Response built successfully",
                        status_code=self._status_code,
                        headers_count=len(self._headers),
                        has_body=self._body is not None,
                        metadata_count=len(self._metadata))

            return FlextResult[dict[str, object]].ok(response)

        except Exception as e:
            logger.exception("Response build failed", error=str(e))
            return FlextResult[dict[str, object]].fail(f"Response build error: {e}")

    def reset(self) -> FlextApiResponseBuilder:
        """Reset builder to initial state."""
        self._status_code = 200
        self._headers.clear()
        self._body = None
        self._metadata.clear()
        return self


class PaginatedResponseBuilder(FlextApiResponseBuilder):
    """Specialized builder for paginated responses."""

    def __init__(self) -> None:
        """Initialize paginated response builder."""
        super().__init__()
        self._page_info: dict[str, object] = {}

    def set_page_info(self,
                     current_page: int,
                     total_pages: int,
                     page_size: int,
                     total_items: int) -> PaginatedResponseBuilder:
        """Set pagination information."""
        self._page_info = {
            "current_page": current_page,
            "total_pages": total_pages,
            "page_size": page_size,
            "total_items": total_items,
            "has_next": current_page < total_pages,
            "has_previous": current_page > 1,
        }
        return self

    def build_paginated_response(self) -> FlextResult[dict[str, object]]:
        """Build paginated response with page information."""
        try:
            base_response_result = self.build_response()
            if not base_response_result.is_success:
                return base_response_result

            response = base_response_result.value
            response["pagination"] = self._page_info.copy()

            logger.debug("Paginated response built successfully",
                        current_page=self._page_info.get("current_page"),
                        total_pages=self._page_info.get("total_pages"),
                        total_items=self._page_info.get("total_items"))

            return FlextResult[dict[str, object]].ok(response)

        except Exception as e:
            logger.exception("Paginated response build failed", error=str(e))
            return FlextResult[dict[str, object]].fail(f"Paginated response build error: {e}")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "FlextApiBuilder",
    "FlextApiQueryBuilder",
    "FlextApiResponseBuilder",
    "PaginatedResponseBuilder",
]

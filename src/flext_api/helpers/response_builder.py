"""FlextResponseBuilder - Standardized API Response Builder.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Powerful response builder for consistent API responses.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from pydantic import BaseModel

if TYPE_CHECKING:
    from flext_core import FlextResult

T = TypeVar("T")


class FlextAPIResponse[T](BaseModel):
    """Standardized API response format."""

    success: bool
    message: str
    data: T | None = None
    error: str | None = None
    timestamp: str
    request_id: str | None = None

    # Metadata
    total_count: int | None = None
    page: int | None = None
    page_size: int | None = None

    # Performance metrics
    execution_time_ms: float | None = None
    cached: bool = False


class FlextApiResponseBuilder:
    """FlextApi powerful response builder for consistent API responses.

    This eliminates the need to manually construct response dictionaries
    and ensures all responses follow the same format.

    Example:
        # Success response
        response = (FlextResponseBuilder()
                   .success()
                   .with_data(user_data)
                   .with_message("User created successfully")
                   .build())

        # Error response
        response = (FlextResponseBuilder()
                   .error("Validation failed")
                   .with_details(validation_errors)
                   .build())

        # Paginated response
        response = (FlextResponseBuilder()
                   .success()
                   .with_data(users)
                   .with_pagination(total=1000, page=1, page_size=50)
                   .build())

    """

    def __init__(self) -> None:
        """Initialize response builder."""
        self._success = True
        self._message = ""
        self._data: Any = None
        self._error: str | None = None
        self._request_id: str | None = None
        self._total_count: int | None = None
        self._page: int | None = None
        self._page_size: int | None = None
        self._execution_time_ms: float | None = None
        self._cached = False
        self._metadata: dict[str, Any] = {}

    def success(
        self, message: str = "Operation completed successfully"
    ) -> FlextApiResponseBuilder:
        """Mark response as successful."""
        self._success = True
        self._message = message
        self._error = None
        return self

    def error(
        self, message: str, error_details: str | None = None
    ) -> FlextApiResponseBuilder:
        """Mark response as error."""
        self._success = False
        self._message = message
        self._error = error_details or message
        self._data = None
        return self

    def with_data(self, data: Any) -> FlextApiResponseBuilder:
        """Add data to response."""
        self._data = data
        return self

    def with_message(self, message: str) -> FlextApiResponseBuilder:
        """Set response message."""
        self._message = message
        return self

    def with_request_id(self, request_id: str) -> FlextApiResponseBuilder:
        """Set request ID for tracing."""
        self._request_id = request_id
        return self

    def with_pagination(
        self,
        total: int,
        page: int,
        page_size: int,
    ) -> FlextApiResponseBuilder:
        """Add pagination information."""
        self._total_count = total
        self._page = page
        self._page_size = page_size
        return self

    def with_performance(
        self,
        execution_time_ms: float,
        cached: bool = False,
    ) -> FlextApiResponseBuilder:
        """Add performance metrics."""
        self._execution_time_ms = execution_time_ms
        self._cached = cached
        return self

    def with_metadata(self, key: str, value: Any) -> FlextApiResponseBuilder:
        """Add custom metadata."""
        self._metadata[key] = value
        return self

    def from_result(self, result: FlextResult[Any]) -> FlextApiResponseBuilder:
        """Create response from FlextResult."""
        if result.success:
            return self.success().with_data(result.data)
        return self.error(result.error or "Operation failed")

    def build(self) -> dict[str, Any]:
        """Build and return the response dictionary."""
        response = {
            "success": self._success,
            "message": self._message,
            "timestamp": datetime.now().isoformat(),
        }

        # Add data if present
        if self._data is not None:
            response["data"] = self._data

        # Add error if present
        if self._error is not None:
            response["error"] = self._error

        # Add optional fields
        if self._request_id is not None:
            response["request_id"] = self._request_id

        if self._total_count is not None:
            response["total_count"] = self._total_count

        if self._page is not None:
            response["page"] = self._page

        if self._page_size is not None:
            response["page_size"] = self._page_size

        if self._execution_time_ms is not None:
            response["execution_time_ms"] = self._execution_time_ms
            response["cached"] = self._cached

        # Add custom metadata
        response.update(self._metadata)

        return response


# Convenience functions for common response types
def flext_api_success_response(
    data: Any = None,
    message: str = "Operation completed successfully",
    **kwargs: object,
) -> dict[str, Any]:
    """Create a success response quickly."""
    builder = FlextApiResponseBuilder().success(message)

    if data is not None:
        builder.with_data(data)

    for key, value in kwargs.items():
        builder.with_metadata(key, value)

    return builder.build()


def flext_api_error_response(
    message: str,
    error_details: str | None = None,
    **kwargs: object,
) -> dict[str, Any]:
    """Create an error response quickly."""
    builder = FlextApiResponseBuilder().error(message, error_details)

    for key, value in kwargs.items():
        builder.with_metadata(key, value)

    return builder.build()


def flext_api_paginated_response(
    data: Any,
    total: int,
    page: int,
    page_size: int,
    message: str = "Data retrieved successfully",
    **kwargs: object,
) -> dict[str, Any]:
    """Create a paginated response quickly."""
    builder = (
        FlextApiResponseBuilder()
        .success(message)
        .with_data(data)
        .with_pagination(total, page, page_size)
    )

    for key, value in kwargs.items():
        builder.with_metadata(key, value)

    return builder.build()


def flext_api_from_flext_result(
    result: FlextResult[Any],
    success_message: str = "Operation completed successfully",
    **kwargs: object,
) -> dict[str, Any]:
    """Create response from FlextResult."""
    if result.success:
        builder = (
            FlextApiResponseBuilder().success(success_message).with_data(result.data)
        )
    else:
        builder = FlextApiResponseBuilder().error(result.error or "Operation failed")

    for key, value in kwargs.items():
        builder.with_metadata(key, value)

    return builder.build()


# ===== LEGACY COMPATIBILITY ALIASES =====
# These will be deprecated in future versions
FlextResponseBuilder = FlextApiResponseBuilder
success_response = flext_api_success_response
error_response = flext_api_error_response
paginated_response = flext_api_paginated_response
from_flext_result = flext_api_from_flext_result

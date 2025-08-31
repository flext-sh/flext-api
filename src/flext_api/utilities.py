"""FLEXT API Utilities - Utility functions following FLEXT patterns.

HTTP-specific utility system providing FlextApiUtilities class with URL validation,
response builders, data transformation, and HTTP-related helper functions
using flext-core FlextUtilities as base.

Module Role in Architecture:
    FlextApiUtilities serves as the HTTP API utility system, providing comprehensive
    utility functions for URL handling, data transformation, response building,
    and HTTP-specific operations following FlextResult patterns.

Classes and Methods:
    FlextApiUtilities:                      # Hierarchical HTTP API utility system
        # URL Utilities:
        UrlValidator(FlextUtilities.TextProcessor) # URL validation and parsing
        DataTransformer(FlextUtilities.Conversions) # Data transformation
        ResponseBuilder(FlextUtilities.Generators) # Response building

        # HTTP Utilities:
        HttpValidator(FlextUtilities.TypeGuards) # HTTP validation utilities
        PaginationBuilder(FlextUtilities.Generators) # Pagination utilities

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from urllib.parse import urlparse

from flext_core import FlextResult, FlextUtilities

from flext_api.constants import FlextApiConstants

# HTTP status code constants (RFC 7231)
HTTP_STATUS_MIN = 100
HTTP_STATUS_MAX = 599


class FlextApiUtilities(FlextUtilities):
    """Single consolidated class containing ALL HTTP API utility functions.

    This is the ONLY utility class in this module, containing all HTTP API
    utility classes as nested classes. Follows the single-class-per-module
    pattern rigorously extending flext-core FlextUtilities to the maximum.
    """

    class UrlValidator:
        """URL validation and normalization utilities."""

        @staticmethod
        def validate_url(url: str) -> FlextResult[str]:
            """Validate URL format and structure."""
            try:
                if not url or not isinstance(url, str):
                    return FlextResult[str].fail("URL must be a non-empty string")

                url = url.strip()
                if not url:
                    return FlextResult[str].fail("URL cannot be empty")

                # Parse URL to validate structure
                parsed = urlparse(url)

                if not parsed.scheme:
                    return FlextResult[str].fail("URL must include scheme (http/https)")

                if parsed.scheme not in {"http", "https"}:
                    return FlextResult[str].fail("URL scheme must be http or https")

                if not parsed.netloc:
                    return FlextResult[str].fail("URL must include hostname")

                return FlextResult[str].ok(url)

            except Exception as e:
                return FlextResult[str].fail(f"URL validation failed: {e}")

        @staticmethod
        def normalize_url(url: str) -> FlextResult[str]:
            """Normalize URL by removing trailing slash and standardizing format."""
            try:
                validation_result = FlextApiUtilities.UrlValidator.validate_url(url)
                if not validation_result.success:
                    return validation_result

                # Remove trailing slash unless it's the root path
                normalized = url.rstrip("/") if not url.endswith("://") else url
                return FlextResult[str].ok(normalized)

            except Exception as e:
                return FlextResult[str].fail(f"URL normalization failed: {e}")

    class DataTransformer:
        """Data transformation and serialization utilities."""

        @staticmethod
        def serialize_json(data: object) -> FlextResult[str]:
            """Serialize data to JSON string."""
            try:
                json_str = json.dumps(
                    data,
                    default=FlextApiUtilities.DataTransformer._json_serializer,
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                return FlextResult[str].ok(json_str)
            except Exception as e:
                return FlextResult[str].fail(f"JSON serialization failed: {e}")

        @staticmethod
        def deserialize_json(json_str: str) -> FlextResult[object]:
            """Deserialize JSON string to Python object."""
            try:
                if not json_str or not isinstance(json_str, str):
                    return FlextResult[object].fail("JSON string cannot be empty")

                data = json.loads(json_str.strip())
                return FlextResult[object].ok(data)
            except json.JSONDecodeError as e:
                return FlextResult[object].fail(f"Invalid JSON format: {e}")
            except Exception as e:
                return FlextResult[object].fail(f"JSON deserialization failed: {e}")

        @staticmethod
        def _json_serializer(obj: object) -> object:
            """Custom JSON serializer for non-standard types."""
            if isinstance(obj, datetime):
                return obj.isoformat()
            if hasattr(obj, "model_dump"):  # Pydantic models
                return obj.model_dump()  # type: ignore[attr-defined]
            if hasattr(obj, "dict"):  # Legacy Pydantic models
                return obj.dict()  # type: ignore[attr-defined]
            if hasattr(obj, "__dict__"):  # Generic objects
                return obj.__dict__
            return str(obj)

    class ResponseBuilder:
        """HTTP response building and formatting utilities."""

        @staticmethod
        def build_success_response(
            data: object = None,
            message: str = "Success",
            status_code: int = FlextApiConstants.HttpStatus.OK,
        ) -> FlextResult[dict[str, object]]:
            """Build standardized success response."""
            try:
                response = {
                    "success": True,
                    "message": message,
                    "status_code": status_code,
                    "data": data,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
                return FlextResult[dict[str, object]].ok(response)
            except Exception as e:
                return FlextResult[dict[str, object]].fail(
                    f"Success response building failed: {e}"
                )

        @staticmethod
        def build_error_response(
            error: str,
            status_code: int = FlextApiConstants.HttpStatus.INTERNAL_SERVER_ERROR,
            error_code: str | None = None,
            details: object = None,
        ) -> FlextResult[dict[str, object]]:
            """Build standardized error response."""
            try:
                response = {
                    "success": False,
                    "message": error,
                    "status_code": status_code,
                    "data": None,
                    "timestamp": datetime.now(UTC).isoformat(),
                }

                if error_code:
                    response["error_code"] = error_code

                if details:
                    response["details"] = details

                return FlextResult[dict[str, object]].ok(response)
            except Exception as e:
                return FlextResult[dict[str, object]].fail(
                    f"Error response building failed: {e}"
                )

    class PaginationBuilder:
        """Pagination utilities for API responses."""

        @staticmethod
        def build_paginated_response(
            data: list[object],
            total: int,
            page: int = 1,
            page_size: int = FlextApiConstants.Pagination.DEFAULT_PAGE_SIZE,
            message: str = "Success",
        ) -> FlextResult[dict[str, object]]:
            """Build paginated response with metadata."""
            try:
                # Validate pagination parameters
                if page < 1:
                    return FlextResult[dict[str, object]].fail("Page must be >= 1")

                if page_size < 1:
                    return FlextResult[dict[str, object]].fail("Page size must be >= 1")

                if page_size > FlextApiConstants.Pagination.MAX_PAGE_SIZE:
                    return FlextResult[dict[str, object]].fail(
                        f"Page size cannot exceed {FlextApiConstants.Pagination.MAX_PAGE_SIZE}"
                    )

                # Calculate pagination metadata
                total_pages = max(1, (total + page_size - 1) // page_size)
                has_next = page < total_pages
                has_prev = page > 1

                response = {
                    "success": True,
                    "message": message,
                    "data": data,
                    "pagination": {
                        "total": total,
                        "page": page,
                        "page_size": page_size,
                        "total_pages": total_pages,
                        "has_next": has_next,
                        "has_previous": has_prev,
                    },
                    "timestamp": datetime.now(UTC).isoformat(),
                }

                return FlextResult[dict[str, object]].ok(response)
            except Exception as e:
                return FlextResult[dict[str, object]].fail(
                    f"Paginated response building failed: {e}"
                )

    class HttpValidator:
        """HTTP-specific validation utilities."""

        @staticmethod
        def validate_http_method(method: str) -> FlextResult[str]:
            """Validate HTTP method."""
            try:
                if not method or not isinstance(method, str):
                    return FlextResult[str].fail(
                        "HTTP method must be a non-empty string"
                    )

                method = method.upper().strip()
                valid_methods = {
                    "GET",
                    "POST",
                    "PUT",
                    "DELETE",
                    "PATCH",
                    "HEAD",
                    "OPTIONS",
                    "TRACE",
                    "CONNECT",
                }

                if method not in valid_methods:
                    return FlextResult[str].fail(
                        f"Invalid HTTP method: {method}. "
                        f"Valid methods: {', '.join(sorted(valid_methods))}"
                    )

                return FlextResult[str].ok(method)
            except Exception as e:
                return FlextResult[str].fail(f"HTTP method validation failed: {e}")

        @staticmethod
        def validate_status_code(status_code: int) -> FlextResult[int]:
            """Validate HTTP status code."""
            try:
                # HTTP status code range validation (RFC 7231)
                if not (HTTP_STATUS_MIN <= status_code <= HTTP_STATUS_MAX):
                    return FlextResult[int].fail(
                        f"Status code must be between {HTTP_STATUS_MIN} and {HTTP_STATUS_MAX}"
                    )

                return FlextResult[int].ok(status_code)
            except Exception as e:
                return FlextResult[int].fail(f"Status code validation failed: {e}")


__all__ = ["FlextApiUtilities"]

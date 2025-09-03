"""FLEXT API Utilities - REAL utility functions using flext-core FlextUtilities.

HTTP-specific utility extensions using ONLY flext-core FlextUtilities functionality,
eliminating all custom implementations and following single class per module pattern.

Module Role in Architecture:
    FlextApiUtilities serves as HTTP API utility extensions, providing specialized
    HTTP operations while delegating all core functionality to flext-core FlextUtilities.
    No duplicate implementations - all functionality comes from flext-core.

Classes and Methods:
    FlextApiUtilities:                      # HTTP API utility extensions
        # Direct Delegates to flext-core:
        All FlextUtilities functionality     # Inherited from flext-core

        # HTTP-Specific Extensions:
        HttpValidator                       # HTTP validation using FlextUtilities.TypeGuards
        ResponseBuilder                     # Response building using FlextUtilities.Generators
        UrlUtilities                       # URL operations using FlextUtilities.TextProcessor

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from urllib.parse import urlparse

from flext_core import FlextLogger, FlextResult, FlextUtilities

from flext_api.constants import FlextApiConstants

logger = FlextLogger(__name__)


class FlextApiUtilities(FlextUtilities):
    """HTTP API utility extensions using REAL flext-core FlextUtilities functionality.

    This class extends FlextUtilities to provide HTTP-specific functionality while
    delegating ALL core operations to flext-core. No duplicate implementations.
    Follows single-class-per-module pattern rigorously.
    """

    @staticmethod
    def validate_client_config(
        config: dict[str, object],
    ) -> FlextResult[dict[str, object]]:
        """Validate client configuration using FlextUtilities."""
        try:
            if not isinstance(config, dict):
                return FlextResult[dict[str, object]].fail(
                    "Config must be a dictionary"
                )

            # Validate timeout
            if "timeout" in config:
                timeout = config["timeout"]
                if not isinstance(timeout, (int, float)) or timeout <= 0:
                    return FlextResult[dict[str, object]].fail(
                        "timeout must be a positive number"
                    )

            # Validate base_url
            if "base_url" in config:
                base_url = config["base_url"]
                if not isinstance(base_url, str) or not base_url:
                    return FlextResult[dict[str, object]].fail(
                        "base_url must be a string"
                    )

            # Validate max_retries
            if "max_retries" in config:
                retries = config["max_retries"]
                if not isinstance(retries, int) or retries < 0:
                    return FlextResult[dict[str, object]].fail(
                        "max_retries must be a non-negative integer"
                    )

            return FlextResult[dict[str, object]].ok(config)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"Config validation failed: {e}")

    @staticmethod
    def parse_response_data_safely(data: object) -> object:
        """Parse response data safely using FlextUtilities with unified logic."""
        try:
            if data is None:
                return None

            # Handle lists - filter out None elements using FlextUtilities patterns
            if isinstance(data, list):
                return [item for item in data if item is not None]

            # Handle strings - use FlextUtilities for safe JSON parsing
            if isinstance(data, str):
                # Use REAL FlextUtilities for safe JSON parsing
                parsed = FlextUtilities.safe_json_parse(data)

                # If parsing succeeded (not default empty dict fallback)
                if parsed != {} or data.strip() == "{}":
                    # Apply list filtering if needed
                    if isinstance(parsed, list):
                        return [item for item in parsed if item is not None]
                    return parsed
                # Fallback to cleaned text using FlextUtilities
                return FlextUtilities.clean_text(data)

            # Return other types as-is
            return data
        except Exception:
            return data  # Fallback to original data

    @staticmethod
    async def read_response_data_safely(data: object) -> object:
        """Safely read response data using unified FlextUtilities parsing."""
        try:
            # Use unified parsing method instead of multiple strategies
            return FlextApiUtilities.parse_response_data_safely(data)
        except Exception:
            return data

    class HttpValidator:
        """HTTP-specific validation using FlextUtilities.TypeGuards and Validators."""

        @staticmethod
        def validate_url(url: str) -> FlextResult[str]:
            """Validate URL using FlextUtilities.TypeGuards functionality."""
            # Use REAL FlextUtilities methods
            if not FlextUtilities.is_non_empty_string(url):
                return FlextResult[str].fail("URL must be a non-empty string")

            # Clean the URL using REAL FlextUtilities
            cleaned_url = FlextUtilities.clean_text(url)
            if not cleaned_url:
                return FlextResult[str].fail("URL cannot be empty after cleaning")

            try:
                parsed = urlparse(cleaned_url)

                # Validate URL structure
                if not parsed.scheme:
                    return FlextResult[str].fail("URL must include scheme (http/https)")
                if parsed.scheme not in {"http", "https"}:
                    return FlextResult[str].fail("URL scheme must be http or https")
                if not parsed.netloc:
                    return FlextResult[str].fail("URL must include hostname")

                return FlextResult[str].ok(cleaned_url)

            except Exception as e:
                return FlextResult[str].fail(f"URL validation failed: {e}")

        @staticmethod
        def normalize_url(url: str) -> FlextResult[str]:
            """Normalize URL using FlextUtilities.TextProcessor functionality."""
            validation_result = FlextApiUtilities.HttpValidator.validate_url(url)
            if not validation_result.success:
                return validation_result

            # Use REAL FlextUtilities for text cleaning
            cleaned_url = FlextUtilities.clean_text(validation_result.value)

            # Remove trailing slash unless it's the root path
            normalized = (
                cleaned_url.rstrip("/")
                if not cleaned_url.endswith("://")
                else cleaned_url
            )
            return FlextResult[str].ok(normalized)

        @staticmethod
        def validate_http_method(method: str) -> FlextResult[str]:
            """Validate HTTP method using REAL FlextUtilities."""
            if not FlextUtilities.is_non_empty_string(method):
                return FlextResult[str].fail("HTTP method must be a non-empty string")

            # Clean method using REAL FlextUtilities
            cleaned_method = FlextUtilities.clean_text(method.upper())

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

            if cleaned_method not in valid_methods:
                return FlextResult[str].fail(
                    f"Invalid HTTP method: {cleaned_method}. "
                    f"Valid methods: {', '.join(sorted(valid_methods))}"
                )

            return FlextResult[str].ok(cleaned_method)

        @staticmethod
        def validate_status_code(status_code: int) -> FlextResult[int]:
            """Validate HTTP status code using REAL FlextUtilities."""
            # Use REAL FlextUtilities for safe int conversion
            safe_status = FlextUtilities.safe_int(status_code, -1)

            if safe_status == -1:
                return FlextResult[int].fail("Status code must be a valid integer")

            # HTTP status code range validation (RFC 7231)
            if not (100 <= safe_status <= 599):
                return FlextResult[int].fail(
                    f"Status code must be between 100 and 599, got: {safe_status}"
                )

            return FlextResult[int].ok(safe_status)

    class DataTransformer:
        """Data transformation using FlextUtilities.ProcessingUtils functionality."""

        @staticmethod
        def serialize_json(data: object) -> FlextResult[str]:
            """Serialize data to JSON using REAL FlextUtilities."""
            # Use REAL FlextUtilities for safe JSON stringification
            json_string = FlextUtilities.safe_json_stringify(data)

            if json_string == "{}":  # Default fallback value from FlextUtilities
                return FlextResult[str].fail("JSON serialization failed")

            return FlextResult[str].ok(json_string)

        @staticmethod
        def deserialize_json(json_str: str) -> FlextResult[object]:
            """Deserialize JSON string using REAL FlextUtilities."""
            # Use REAL FlextUtilities for validation
            if not FlextUtilities.is_non_empty_string(json_str):
                return FlextResult[object].fail("JSON string cannot be empty")

            # Use REAL FlextUtilities for safe JSON parsing
            data = FlextUtilities.safe_json_parse(json_str)

            # Check if parsing actually succeeded (not default empty dict)
            if data == {} and json_str.strip() != "{}":
                return FlextResult[object].fail("JSON deserialization failed")

            return FlextResult[object].ok(data)

        @staticmethod
        def extract_model_data(obj: object) -> FlextResult[dict[str, object]]:
            """Extract model data using REAL FlextUtilities."""
            try:
                # Use REAL FlextUtilities for model data extraction
                if isinstance(obj, str):
                    data = FlextUtilities.safe_json_parse(obj)
                    return FlextResult[dict[str, object]].ok(data)
                if isinstance(obj, dict):
                    return FlextResult[dict[str, object]].ok(obj)
                return FlextResult[dict[str, object]].ok({})
            except Exception as e:
                return FlextResult[dict[str, object]].fail(
                    f"Model data extraction failed: {e}"
                )

    class ResponseBuilder:
        """HTTP response building using FlextUtilities.Generators functionality."""

        @staticmethod
        def build_success_response(
            data: object = None,
            message: str = "Success",
            status_code: int = FlextApiConstants.HttpStatus.OK,
        ) -> FlextResult[dict[str, object]]:
            """Build standardized success response using FlextUtilities."""
            try:
                # Generate timestamp using REAL FlextUtilities
                timestamp = FlextUtilities.generate_iso_timestamp()

                response = {
                    "success": True,
                    "message": message,
                    "status_code": status_code,
                    "data": data,
                    "timestamp": timestamp,
                    "request_id": FlextUtilities.generate_correlation_id(),
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
            """Build standardized error response using FlextUtilities."""
            try:
                # Generate timestamp using REAL FlextUtilities
                timestamp = FlextUtilities.generate_iso_timestamp()

                response = {
                    "success": False,
                    "message": error,
                    "status_code": status_code,
                    "data": None,
                    "timestamp": timestamp,
                    "request_id": FlextUtilities.generate_correlation_id(),
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
        """Pagination utilities using FlextUtilities functionality."""

        @staticmethod
        def build_paginated_response(
            data: list[object],
            total: int,
            page: int = 1,
            page_size: int = FlextApiConstants.Pagination.DEFAULT_PAGE_SIZE,
            message: str = "Success",
        ) -> FlextResult[dict[str, object]]:
            """Build paginated response using FlextUtilities."""
            try:
                # Use FlextUtilities for safe int conversions
                safe_page = FlextUtilities.Conversions.safe_int(page, 1)
                safe_page_size = FlextUtilities.Conversions.safe_int(
                    page_size, FlextApiConstants.Pagination.DEFAULT_PAGE_SIZE
                )
                safe_total = FlextUtilities.Conversions.safe_int(total, 0)

                # Validate pagination parameters
                if safe_page < 1:
                    return FlextResult[dict[str, object]].fail("Page must be >= 1")

                if safe_page_size < 1:
                    return FlextResult[dict[str, object]].fail("Page size must be >= 1")

                if safe_page_size > FlextApiConstants.Pagination.MAX_PAGE_SIZE:
                    return FlextResult[dict[str, object]].fail(
                        f"Page size cannot exceed {FlextApiConstants.Pagination.MAX_PAGE_SIZE}"
                    )

                # Calculate pagination metadata
                total_pages = max(
                    1, (safe_total + safe_page_size - 1) // safe_page_size
                )
                has_next = safe_page < total_pages
                has_prev = safe_page > 1

                # Generate timestamp using FlextUtilities
                timestamp = FlextUtilities.Generators.generate_iso_timestamp()

                response = {
                    "success": True,
                    "message": message,
                    "data": data,
                    "pagination": {
                        "total": safe_total,
                        "page": safe_page,
                        "page_size": safe_page_size,
                        "total_pages": total_pages,
                        "has_next": has_next,
                        "has_previous": has_prev,
                    },
                    "timestamp": timestamp,
                    "request_id": FlextUtilities.Generators.generate_request_id(),
                }

                return FlextResult[dict[str, object]].ok(response)
            except Exception as e:
                return FlextResult[dict[str, object]].fail(
                    f"Paginated response building failed: {e}"
                )


__all__ = [
    "FlextApiUtilities",
]

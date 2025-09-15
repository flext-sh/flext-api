"""FLEXT API Utilities - HTTP utilities extending flext-core.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import time
from typing import TypeVar

from flext_core import (
    FlextResult,
    FlextTypeAdapters,
    FlextTypes,
    FlextUtilities,
    FlextValidations,
)

from flext_api.constants import FlextApiConstants, HttpMethods

T = TypeVar("T")


class FlextApiUtilities:
    """HTTP API utilities extending flext-core - ZERO DUPLICATION using existing functionality."""

    # =============================================================================
    # DIRECT RE-EXPORT of flext-core utilities - STOP DUPLICATING!
    # =============================================================================

    # Use existing FlextUtilities instead of duplicating
    TextProcessor = FlextUtilities.TextProcessor
    Validation = FlextUtilities.Validation
    Generators = FlextUtilities.Generators
    Conversions = FlextUtilities.Conversions
    TypeGuards = FlextUtilities.TypeGuards

    # URL validation - using flext-core validation patterns
    UrlValidator = FlextValidations.Validators

    # =============================================================================
    # HTTP-SPECIFIC BUILDER CLASSES - Using flext-core foundation
    # =============================================================================

    # Simple generator forwards for test compatibility
    @classmethod
    def generate_uuid(cls) -> str:
        """Generate a UUID string via flext-core Generators."""
        return FlextUtilities.Generators.generate_uuid()

    @classmethod
    def generate_id(cls) -> str:
        """Generate a short ID via flext-core Generators."""
        return FlextUtilities.Generators.generate_id()

    @classmethod
    def generate_entity_id(cls) -> str:
        """Generate an entity ID via flext-core Generators."""
        return FlextUtilities.Generators.generate_entity_id()

    @classmethod
    def generate_correlation_id(cls) -> str:
        """Generate a correlation ID via flext-core Generators."""
        return FlextUtilities.Generators.generate_correlation_id()

    @classmethod
    def generate_timestamp(cls) -> float:
        """Generate a UNIX timestamp via standard time module."""
        return time.time()

    @classmethod
    def generate_iso_timestamp(cls) -> str:
        """Generate an ISO 8601 timestamp via flext-core Generators."""
        return FlextUtilities.Generators.generate_iso_timestamp()

    class ResponseBuilder:
        """HTTP response builder using flext-core patterns."""

        @staticmethod
        def build_error_response(
            message: str | None = None,
            *,  # Python 3.13+ keyword-only parameters for clarity
            status_code: int = 500,
            data: object | None = None,
            error: str | None = None,
            error_code: str | None = None,
            details: object | None = None,
        ) -> FlextResult[FlextTypes.Core.Dict]:
            """Build error response using flext-core patterns."""
            try:
                final_message = (
                    message if message is not None else (error or "Unknown error")
                )
                response = {
                    "success": False,
                    "message": final_message,
                    "status_code": status_code,
                    "data": data,
                }
                if error and error != final_message:
                    response["error"] = error
                if error_code:
                    response["error_code"] = error_code
                if details:
                    response["details"] = details
                return FlextResult[FlextTypes.Core.Dict].ok(response)
            except Exception as e:
                return FlextResult[FlextTypes.Core.Dict].fail(str(e))

        @staticmethod
        def build_success_response(
            data: object = None, message: str = "Success", status_code: int = 200
        ) -> FlextResult[FlextTypes.Core.Dict]:
            """Build success response using flext-core patterns."""
            try:
                response = {
                    "success": True,
                    "message": message,
                    "status_code": status_code,
                    "data": data,
                    "timestamp": FlextUtilities.Generators.generate_iso_timestamp(),
                    "request_id": FlextUtilities.Generators.generate_request_id(),
                }
                return FlextResult[FlextTypes.Core.Dict].ok(response)
            except Exception as e:
                return FlextResult[FlextTypes.Core.Dict].fail(str(e))

    class PaginationBuilder:
        """HTTP pagination builder using flext-core patterns."""

        @staticmethod
        def build_paginated_response(
            data: list[object] | None,
            *,  # Python 3.13+ keyword-only for better API design
            page: int = 1,
            page_size: int = FlextApiConstants.DEFAULT_PAGE_SIZE,  # Use consistent defaults
            total: int | None = None,
            message: str | None = None,
        ) -> FlextResult[FlextTypes.Core.Dict]:
            """Build paginated response using flext-core patterns."""
            try:
                if page < 1:
                    return FlextResult[FlextTypes.Core.Dict].fail("Page must be >= 1")
                if page_size < 1:
                    return FlextResult[FlextTypes.Core.Dict].fail(
                        "Page size must be >= 1"
                    )
                if page_size > FlextApiConstants.Limits.MAX_PAGE_SIZE:
                    return FlextResult[FlextTypes.Core.Dict].fail(
                        f"Page size cannot exceed {FlextApiConstants.Limits.MAX_PAGE_SIZE}"
                    )

                if data is None or not isinstance(data, list):
                    data = []
                if total is None:
                    total = len(data)

                total_pages = (
                    max(1, (total + page_size - 1) // page_size) if total > 0 else 1
                )
                response = {
                    "success": True,
                    "data": data,
                    "pagination": {
                        "page": page,
                        "page_size": page_size,
                        "total": total,
                        "total_pages": total_pages,
                        "has_next": page < total_pages,
                        "has_previous": page > 1,
                    },
                }
                if message:
                    response["message"] = message
                return FlextResult[FlextTypes.Core.Dict].ok(response)
            except Exception as e:
                return FlextResult[FlextTypes.Core.Dict].fail(str(e))

    # =============================================================================
    # HTTP-SPECIFIC ALIASES - Direct use of flext-core functionality (NO DUPLICATIONS)
    # =============================================================================

    # Use flext-core validation directly - ZERO DUPLICATION
    class HttpValidator:
        """HTTP-specific validation using flext-core patterns."""

        # Use flext-core validators directly
        validate_url = FlextValidations.FieldValidators.validate_url

        @staticmethod
        def validate_http_method(method: str | None) -> FlextResult[str]:
            """Validate HTTP method using FlextCore patterns and Python 3.13+ StrEnum."""
            if not method or not isinstance(method, str):
                return FlextResult[str].fail("HTTP method must be a non-empty string")

            method_upper = method.upper()
            # Use Python 3.13+ StrEnum for validation - maximum FlextCore integration
            try:
                validated_method = HttpMethods(method_upper)
                return FlextResult[str].ok(validated_method.value)
            except ValueError:
                valid_methods = ", ".join(HttpMethods)
                return FlextResult[str].fail(
                    f"Invalid HTTP method. Valid methods: {valid_methods}"
                )

        @staticmethod
        def validate_status_code(code: int | str) -> FlextResult[int]:
            """Validate HTTP status code."""
            try:
                code_int = int(code)
                if (
                    code_int < FlextApiConstants.MIN_HTTP_STATUS
                    or code_int > FlextApiConstants.HttpStatus.MAX_HTTP_STATUS
                ):
                    return FlextResult[int].fail("Status code out of valid range")
                return FlextResult[int].ok(code_int)
            except (ValueError, TypeError):
                return FlextResult[int].fail("Status code must be a valid integer")

        @staticmethod
        def normalize_url(url: str) -> FlextResult[str]:
            """Normalize URL using flext-core text processing."""
            cleaned = FlextUtilities.TextProcessor.clean_text(url)
            if not cleaned:
                return FlextResult[str].fail("URL cannot be empty")
            normalized = cleaned.rstrip("/") if not cleaned.endswith("://") else cleaned
            return FlextResult[str].ok(normalized)

        # Removed complex lambda-based validators - using class methods instead

    # =============================================================================
    # STREAMLINED CONVENIENCE METHODS - Direct flext-core usage
    # =============================================================================

    @staticmethod
    def validate_url(url: str) -> FlextResult[str]:
        """Validate URL using flext-core validation."""
        return FlextValidations.FieldValidators.validate_url(url)

    @staticmethod
    def validate_config(config: object) -> FlextResult[FlextTypes.Core.Dict]:
        """Validate configuration using flext-core type adapters."""
        try:
            result_dict = FlextTypeAdapters.adapt_to_dict(config)
            return FlextResult[FlextTypes.Core.Dict].ok(result_dict)
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(str(e))

    class DataTransformer:
        """Data transformation utilities using flext-core patterns."""

        @staticmethod
        def to_json(data: object) -> FlextResult[str]:
            """Convert data to JSON string."""
            try:
                json_str = json.dumps(data, default=str)
                return FlextResult[str].ok(json_str)
            except Exception as e:
                return FlextResult[str].fail(f"JSON conversion failed: {e}")

        @staticmethod
        def from_json(json_str: str) -> FlextResult[object]:
            """Parse JSON string to object."""
            try:
                data = json.loads(json_str)
                return FlextResult[object].ok(data)
            except Exception as e:
                return FlextResult[object].fail(f"JSON parsing failed: {e}")

        @staticmethod
        def to_dict(data: object) -> FlextResult[dict[str, object]]:
            """Convert data to dictionary."""
            try:
                if isinstance(data, dict):
                    return FlextResult[dict[str, object]].ok(data)
                if hasattr(data, "model_dump") and callable(
                    getattr(data, "model_dump")
                ):
                    # Type-safe call to model_dump
                    model_data = getattr(data, "model_dump")()
                    return FlextResult[dict[str, object]].ok(model_data)
                if hasattr(data, "dict") and callable(getattr(data, "dict")):
                    # Type-safe call to dict method
                    dict_data = getattr(data, "dict")()
                    return FlextResult[dict[str, object]].ok(dict_data)
                return FlextResult[dict[str, object]].fail(
                    f"Cannot convert {type(data)} to dict"
                )
            except Exception as e:
                return FlextResult[dict[str, object]].fail(
                    f"Dict conversion failed: {e}"
                )

    # =============================================================================
    # Missing Utility Methods - Adding for API compatibility
    # =============================================================================

    @staticmethod
    def safe_bool_conversion(value: object) -> bool:
        """Safely convert value to boolean."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in {"true", "1", "yes", "on"}
        return bool(value)

    @staticmethod
    def safe_json_parse(json_str: str) -> FlextResult[dict[str, object]]:
        """Safely parse JSON string."""
        try:
            result = json.loads(json_str)
            if isinstance(result, dict):
                return FlextResult[dict[str, object]].ok(result)
            return FlextResult[dict[str, object]].fail(
                "JSON result is not a dictionary"
            )
        except json.JSONDecodeError as e:
            return FlextResult[dict[str, object]].fail(f"JSON parse error: {e}")
        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"Unexpected error: {e}")

    @staticmethod
    def safe_json_stringify(data: object) -> FlextResult[str]:
        """Safely stringify object to JSON."""
        try:
            result = json.dumps(data, default=str, ensure_ascii=False)
            return FlextResult[str].ok(result)
        except Exception as e:
            return FlextResult[str].fail(f"JSON stringify error: {e}")

    @staticmethod
    def is_non_empty_string(value: object) -> bool:
        """Check if value is a non-empty string."""
        return isinstance(value, str) and len(value.strip()) > 0

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text by removing extra whitespace."""
        return " ".join(text.split()) if text else ""

    @staticmethod
    def truncate(text: str, max_length: int = 100) -> str:
        """Truncate text to maximum length."""
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."

    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in seconds to human readable string."""
        seconds_per_minute = 60

        if seconds < 1:
            return f"{seconds * 1000:.1f}ms"
        if seconds < seconds_per_minute:
            return f"{seconds:.1f}s"
        minutes = int(seconds // seconds_per_minute)
        remaining_seconds = seconds % seconds_per_minute
        return f"{minutes}m {remaining_seconds:.1f}s"

    @staticmethod
    def get_elapsed_time(start_time: float, current_time: float | None = None) -> float:
        """Get elapsed time between two timestamps."""
        if current_time is None:
            current_time = time.time()
        return current_time - start_time

    @staticmethod
    def get_performance_metrics(start_time: float) -> dict[str, object]:
        """Get performance metrics for a timed operation."""
        current_time = time.time()
        elapsed = current_time - start_time
        return {
            "elapsed_time": elapsed,
            "elapsed_ms": elapsed * 1000,
            "start_time": start_time,
            "end_time": current_time,
            "formatted_duration": FlextApiUtilities.format_duration(elapsed),
        }

    @staticmethod
    def batch_process(items: list[T], batch_size: int = 100) -> list[list[T]]:
        """Process items in batches."""
        if batch_size <= 0:
            batch_size = 100

        batches = []
        for i in range(0, len(items), batch_size):
            batch = items[i : i + batch_size]
            batches.append(batch)
        return batches

    @staticmethod
    def safe_int_conversion(value: str) -> int | None:
        """Safely convert string to integer."""
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def safe_int_conversion_with_default(value: str, default: int = 0) -> int:
        """Safely convert string to integer with default value."""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    # Port constants for network validation
    MIN_PORT: int = 1
    MAX_PORT: int = 65535


__all__ = [
    "FlextApiUtilities",
]

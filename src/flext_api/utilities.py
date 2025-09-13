"""FLEXT API Utilities - HTTP utilities extending flext-core.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import (
    FlextResult,
    FlextTypeAdapters,
    FlextTypes,
    FlextUtilities,
    FlextValidations,
)

from flext_api.constants import FlextApiConstants, HttpMethods


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

    # =============================================================================
    # HTTP-SPECIFIC BUILDER CLASSES - Using flext-core foundation
    # =============================================================================

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
        def validate_http_method(method: str) -> FlextResult[str]:
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


__all__ = [
    "FlextApiUtilities",
]

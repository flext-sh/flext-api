"""FLEXT API Utilities - HTTP utilities extending flext-core.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from urllib.parse import urlparse

from flext_core import (
    FlextResult,
    FlextTypes,
    FlextUtilities,
    FlextValidations,
)

from flext_api.constants import FlextApiConstants


class FlextApiUtilities:
    """HTTP API utilities - ZERO TOLERANCE: NO wrappers, delegation, or duplication.

    MANDATORY: Use flext-core directly:
    - FlextUtilities.Generators.generate_uuid() instead of wrapper methods
    - FlextValidations.FieldValidators.validate_url() instead of delegation
    - FlextUtilities.TextProcessor.clean_text() instead of wrapper methods.
    """

    # HTTP-SPECIFIC BUILDER CLASSES ONLY - NO delegation methods
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
            page_size: int = FlextApiConstants.DEFAULT_PAGE_SIZE,
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

    class HttpValidator:
        """HTTP-specific validation using flext-core patterns."""

        @staticmethod
        def validate_url(url: str) -> FlextResult[str]:
            """Validate URL with additional port range checking."""
            # First use flext-core validation
            base_result = FlextValidations.FieldValidators.validate_url(url)
            if base_result.is_failure:
                return base_result

            # Additional port validation
            try:
                parsed = urlparse(url)
                if parsed.port is not None:
                    port = parsed.port
                    if port == 0:
                        return FlextResult[str].fail("Invalid port 0")
                    if port > FlextApiConstants.HttpValidation.MAX_PORT:
                        return FlextResult[str].fail(f"Invalid port {port}")

                # Check URL length
                if len(url) > FlextApiConstants.HttpValidation.MAX_URL_LENGTH:
                    return FlextResult[str].fail("URL is too long")

            except Exception as e:
                return FlextResult[str].fail(f"URL parsing failed: {e}")

            return base_result

        @staticmethod
        def validate_http_method(method: str | None) -> FlextResult[str]:
            """Validate HTTP method using FlextCore patterns and Python 3.13+ StrEnum."""
            if not method or not isinstance(method, str):
                return FlextResult[str].fail("HTTP method must be a non-empty string")

            method_upper = method.upper()
            # Use Python 3.13+ StrEnum for validation - maximum FlextCore integration
            try:
                validated_method = FlextApiConstants.HttpMethods(method_upper)
                return FlextResult[str].ok(validated_method.value)
            except ValueError:
                valid_methods = ", ".join(FlextApiConstants.HttpMethods)
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
                    return FlextResult[int].fail("Invalid HTTP status code")
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

    # Backward compatibility delegation methods for ecosystem integration
    @staticmethod
    def validate_url(url: str) -> FlextResult[str]:
        """Delegate to HttpValidator.validate_url() for ecosystem compatibility."""
        return FlextApiUtilities.HttpValidator.validate_url(url)

    @staticmethod
    def validate_config(config: object) -> FlextResult[FlextTypes.Core.Dict]:
        """Validate configuration object and return config details."""
        try:
            if config is None:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    "Configuration cannot be None"
                )

            # Extract config data
            if hasattr(config, "__dict__"):
                config_dict = config.__dict__
            elif isinstance(config, dict):
                config_dict = config
            else:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    "Configuration must be dict-like or have attributes"
                )

            # Determine config type based on attributes
            config_type = "generic"
            if "url" in config_dict and "method" in config_dict:
                config_type = "http_request"
            elif "error_code" in config_dict or "retry_count" in config_dict:
                config_type = "http_error"
            elif "rules" in config_dict or "validators" in config_dict:
                config_type = "validation"

            # Validate common HTTP configuration fields
            if "method" in config_dict:
                method_result = FlextApiUtilities.HttpValidator.validate_http_method(
                    config_dict["method"]
                )
                if method_result.is_failure:
                    return FlextResult[FlextTypes.Core.Dict].fail(
                        f"Invalid method: {method_result.error}"
                    )

            if "status_code" in config_dict:
                status_result = FlextApiUtilities.HttpValidator.validate_status_code(
                    config_dict["status_code"]
                )
                if status_result.is_failure:
                    return FlextResult[FlextTypes.Core.Dict].fail(
                        f"Invalid status code: {status_result.error}"
                    )

            # Return validation result with config details
            result_data = {
                "config_type": config_type,
                **config_dict,  # Include all original config data
            }

            return FlextResult[FlextTypes.Core.Dict].ok(result_data)
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Configuration validation failed: {e}"
            )


__all__ = [
    "FlextApiUtilities",
]

"""FLEXT API Utilities - HTTP utilities extending flext-core.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.constants import FlextApiConstants
from flext_core import (
    FlextModels,
    FlextResult,
    FlextTypes,
    FlextUtilities,
)


class FlextApiUtilities:
    """HTTP API utilities - ZERO TOLERANCE: NO wrappers, delegation, or duplication.

    MANDATORY: Use flext-core directly:
    - FlextUtilities.Generators.generate_uuid() instead of wrapper methods
    - FlextModels.create_validated_url() instead of delegation
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
        """HTTP-specific validation using centralized flext-core FlextModels."""

        @staticmethod
        def validate_url(url: str) -> FlextResult[str]:
            """Validate URL using centralized FlextModels.create_validated_http_url()."""
            # Use FlextModels centralized validation with HTTP-specific rules
            return FlextModels.create_validated_http_url(
                url,
                max_length=FlextApiConstants.HttpValidation.MAX_URL_LENGTH,
                max_port=FlextApiConstants.HttpValidation.MAX_PORT,
            )

        @staticmethod
        def validate_http_method(method: str | None) -> FlextResult[str]:
            """Validate HTTP method using centralized FlextModels validation."""
            return FlextModels.create_validated_http_method(method)

        @staticmethod
        def validate_status_code(code: int | str) -> FlextResult[int]:
            """Validate HTTP status code using centralized FlextModels validation."""
            return FlextModels.create_validated_http_status(code)

        @staticmethod
        def normalize_url(url: str) -> FlextResult[str]:
            """Normalize URL using centralized FlextModels.Url.normalize()."""
            # First create URL object then normalize
            url_result = FlextModels.Url.create(url)
            if url_result.is_failure:
                return FlextResult[str].fail(url_result.error or "Invalid URL")

            normalized_result = url_result.unwrap().normalize()
            if normalized_result.is_success:
                return FlextResult[str].ok(normalized_result.unwrap().value)
            return FlextResult[str].fail(
                normalized_result.error or "URL normalization failed"
            )

    # Backward compatibility delegation methods for ecosystem integration
    @staticmethod
    def validate_url(url: str) -> FlextResult[str]:
        """Delegate to centralized FlextModels HTTP URL validation."""
        return FlextModels.create_validated_http_url(
            url,
            max_length=FlextApiConstants.HttpValidation.MAX_URL_LENGTH,
            max_port=FlextApiConstants.HttpValidation.MAX_PORT,
        )

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

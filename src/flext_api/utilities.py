"""FLEXT API Utilities - REAL utility functions using flext-core FlextUtilities.

HTTP-specific utility extensions using ONLY flext-core FlextUtilities functionality,
eliminating all custom implementations and following single class per module pattern.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated
from urllib.parse import ParseResult, urlparse

from flext_core import FlextLogger, FlextModels, FlextResult, FlextUtilities
from pydantic import Field

from flext_api.constants import FlextApiConstants
from flext_api.typings import FlextApiTypes

logger = FlextLogger(__name__)


class FlextApiUtilities(FlextUtilities):
    """HTTP API utilities usando diretamente FlextApiTypes sem aliases locais.

    Decisão: remover classe 'Typings' para evitar shadowing/duplication. Todos os
    tipos são referenciados diretamente de `FlextApiTypes` ou dos modelos.
    """

    @classmethod
    def validate_config(
        cls,
        config: Annotated[
            FlextModels.Http.HttpRequestConfig
            | FlextModels.Http.HttpErrorConfig
            | FlextModels.Http.ValidationConfig,
            Field(discriminator="config_type"),
        ],
    ) -> FlextResult[FlextApiTypes.Core.Dict]:
        """Validate configuration using Python 3.13 + Advanced Pydantic V2 patterns."""
        # Python 3.13 match/case with type narrowing for configuration types
        match config:
            case FlextModels.Http.HttpRequestConfig() as http_config:
                return cls._validate_http_request_config(http_config)
            case FlextModels.Http.HttpErrorConfig() as error_config:
                return cls._validate_http_error_config(error_config)
            case FlextModels.Http.ValidationConfig() as validation_config:
                return cls._validate_validation_config(validation_config)

    @classmethod
    def _validate_http_request_config(
        cls,
        config: FlextModels.Http.HttpRequestConfig,
    ) -> FlextResult[FlextApiTypes.Core.Dict]:
        """Validate HTTP request configuration using FlextUtilities."""
        return (
            cls.HttpValidator.validate_url(config.url)
            .bind(lambda _: cls.HttpValidator.validate_http_method(config.method))
            .map(lambda _: config.model_dump())
        )

    @classmethod
    def _validate_http_error_config(
        cls,
        config: FlextModels.Http.HttpErrorConfig,
    ) -> FlextResult[FlextApiTypes.Core.Dict]:
        """Validate HTTP error configuration using FlextUtilities."""
        return cls.HttpValidator.validate_status_code(config.status_code).map(
            lambda _: config.model_dump(),
        )

    @classmethod
    def _validate_validation_config(
        cls,
        config: FlextModels.Http.ValidationConfig,
    ) -> FlextResult[FlextApiTypes.Core.Dict]:
        """Validate validation configuration - direct passthrough."""
        return FlextResult[FlextApiTypes.Core.Dict].ok(config.model_dump())

    # Convenience methods removed - use ResponseBuilder and PaginationBuilder directly

    @classmethod
    def validate_url(cls, url: object) -> FlextResult[str]:
        """Validate URL with type checking - convenience method."""
        if not isinstance(url, str):
            return FlextResult[str].fail("Invalid URL format")
        return cls.HttpValidator.validate_url(url)

    class HttpValidator:
        """HTTP-specific validation using FlextUtilities.TypeGuards and Validators."""

        @staticmethod
        def validate_url(url: str) -> FlextResult[str]:
            """Validate URL using Python 3.13 + Railway Pattern + FlextUtilities."""
            # Railway Pattern chaining for clean flow
            return (
                FlextApiUtilities.HttpValidator._validate_string(url)
                .bind(FlextApiUtilities.HttpValidator._clean_url)
                .bind(FlextApiUtilities.HttpValidator._validate_parsed_url)
            )

        @staticmethod
        def _validate_string(url: str) -> FlextResult[str]:
            """Validate input string using FlextUtilities + Python 3.13 patterns.

            Returns:
                FlextResult[str]: Validation result.

            """
            return (
                FlextResult[str].ok(url)
                if FlextUtilities.is_non_empty_string(url)
                else FlextResult[str].fail("URL must be a non-empty string")
            )

        @staticmethod
        def _clean_url(url: str) -> FlextResult[str]:
            """Clean URL using FlextUtilities + advanced validation."""
            cleaned = FlextUtilities.clean_text(url)
            return (
                FlextResult[str].ok(cleaned)
                if cleaned
                else FlextResult[str].fail("URL cannot be empty after cleaning")
            )

        @staticmethod
        def _validate_parsed_url(cleaned_url: str) -> FlextResult[str]:
            """Validate URL structure using Python 3.13 advanced match/case patterns."""
            try:
                parsed = urlparse(cleaned_url)

                # Python 3.13 Advanced Structural Pattern Matching

                if not parsed.scheme:
                    return FlextResult[str].fail("Invalid URL format")

                if parsed.scheme not in {"http", "https"}:
                    return FlextResult[str].fail("Invalid URL format")

                if not parsed.netloc:
                    return FlextResult[str].fail("URL must include hostname")

                # Valid URL - proceed to component validation
                return FlextApiUtilities.HttpValidator._validate_url_components(
                    parsed,
                    cleaned_url,
                )

            except Exception as e:
                return FlextResult[str].fail(f"URL parsing failed: {e}")

        @staticmethod
        def _validate_url_components(parsed: ParseResult, url: str) -> FlextResult[str]:
            """Advanced URL component validation using Python 3.13 pattern matching."""
            # Python 3.13 Advanced Pattern Matching for URL components
            max_hostname = FlextApiConstants.HttpValidation.MAX_HOSTNAME_LENGTH
            min_port = FlextApiConstants.HttpValidation.MIN_PORT_NUMBER
            max_port = FlextApiConstants.HttpValidation.MAX_PORT_NUMBER
            max_url = FlextApiConstants.HttpValidation.MAX_URL_LENGTH

            match parsed:
                case ParseResult(hostname=hostname) if (
                    hostname and len(hostname) > max_hostname
                ):
                    return FlextResult[str].fail(
                        f"Hostname too long (max {max_hostname} characters)",
                    )
                case ParseResult(port=port) if port is not None and not (
                    min_port <= port <= max_port
                ):
                    return FlextResult[str].fail(
                        f"Invalid port {port}, must be {min_port}-{max_port}",
                    )
                case _ if len(url) > max_url:
                    return FlextResult[str].fail(
                        f"URL too long (max {max_url} characters)",
                    )
                case _:
                    return FlextResult[str].ok(url)

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
            """Validate HTTP method using Python 3.13 advanced patterns + FlextUtilities."""
            if not FlextUtilities.is_non_empty_string(method):
                return FlextResult[str].fail("HTTP method must be a non-empty string")

            # Clean method using REAL FlextUtilities
            cleaned_method = FlextUtilities.clean_text(method.upper())

            # Python 3.13 Advanced Pattern Matching for HTTP Methods
            match cleaned_method:
                # Common methods - optimized path
                case "GET" | "POST" | "PUT" | "DELETE":
                    return FlextResult[str].ok(cleaned_method)

                # Extended methods - standard HTTP
                case "PATCH" | "HEAD" | "OPTIONS":
                    return FlextResult[str].ok(cleaned_method)

                # Rare but valid methods
                case "TRACE" | "CONNECT":
                    return FlextResult[str].ok(cleaned_method)

                # Custom/WebDAV methods pattern
                case method_name if method_name.startswith(
                    ("PROP", "COPY", "MOVE", "LOCK"),
                ):
                    return FlextResult[str].ok(cleaned_method)  # Allow WebDAV methods

                # Invalid method - comprehensive error
                case invalid_method:
                    return FlextResult[str].fail(
                        f"Invalid HTTP method: '{invalid_method}'. Valid methods: "
                        f"GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS, TRACE, CONNECT",
                    )

        @staticmethod
        def validate_status_code(status_code: int) -> FlextResult[int]:
            """Validate HTTP status code using Python 3.13 + FlextUtilities."""
            # Use REAL FlextUtilities for safe int conversion
            safe_status = FlextUtilities.safe_int(status_code, -1)

            if safe_status == -1:
                return FlextResult[int].fail("Status code must be a valid integer")

            # Python 3.13 Advanced Pattern Matching for HTTP Status Codes using constants
            status_ranges = FlextApiConstants.HttpStatus

            match safe_status:
                # 1xx Informational
                case code if (
                    status_ranges.INFORMATIONAL_MIN
                    <= code
                    <= status_ranges.INFORMATIONAL_MAX
                ):
                    return FlextResult[int].ok(safe_status)

                # 2xx Success
                case code if (
                    status_ranges.SUCCESS_MIN <= code <= status_ranges.SUCCESS_MAX
                ):
                    return FlextResult[int].ok(safe_status)

                # 3xx Redirection
                case code if (
                    status_ranges.REDIRECTION_MIN
                    <= code
                    <= status_ranges.REDIRECTION_MAX
                ):
                    return FlextResult[int].ok(safe_status)

                # 4xx Client Error
                case code if (
                    status_ranges.CLIENT_ERROR_MIN
                    <= code
                    <= status_ranges.CLIENT_ERROR_MAX
                ):
                    return FlextResult[int].ok(safe_status)

                # 5xx Server Error
                case code if (
                    status_ranges.SERVER_ERROR_MIN
                    <= code
                    <= status_ranges.SERVER_ERROR_MAX
                ):
                    return FlextResult[int].ok(safe_status)

                # Invalid status code
                case invalid_code:
                    return FlextResult[int].fail(
                        f"Invalid HTTP status code: {invalid_code}. "
                        f"Valid range: {status_ranges.INFORMATIONAL_MIN}-{status_ranges.SERVER_ERROR_MAX} (RFC 7231)",
                    )

    class ResponseBuilder:
        """HTTP response building using FlextUtilities.Generators functionality."""

        @staticmethod
        def build_success_response(
            data: object = None,
            message: str = "Success",
            status_code: int = FlextApiConstants.HttpStatus.OK,
        ) -> FlextResult[FlextApiTypes.Core.Dict]:
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
                return FlextResult[FlextApiTypes.Core.Dict].ok(response)
            except Exception as e:
                return FlextResult[FlextApiTypes.Core.Dict].fail(
                    f"Success response building failed: {e}",
                )

        @staticmethod
        def build_error_response(
            error: str,
            status_code: int = FlextApiConstants.HttpStatus.INTERNAL_SERVER_ERROR,
            error_code: str | None = None,
            details: object = None,
        ) -> FlextResult[FlextApiTypes.Core.Dict]:
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

                return FlextResult[FlextApiTypes.Core.Dict].ok(response)
            except Exception as e:
                return FlextResult[FlextApiTypes.Core.Dict].fail(
                    f"Error response building failed: {e}",
                )

    class PaginationBuilder:
        """Pagination utilities using FlextUtilities functionality."""

        @staticmethod
        def build_paginated_response(
            data: FlextApiTypes.Core.List,
            total: int,
            page: int = 1,
            page_size: int = FlextApiConstants.Pagination.DEFAULT_PAGE_SIZE,
            message: str = "Success",
        ) -> FlextResult[FlextApiTypes.Core.Dict]:
            """Build paginated response using FlextUtilities."""
            try:
                # Use FlextUtilities for safe int conversions
                safe_page = FlextUtilities.Conversions.safe_int(page, 1)
                safe_page_size = FlextUtilities.Conversions.safe_int(
                    page_size,
                    FlextApiConstants.Pagination.DEFAULT_PAGE_SIZE,
                )
                safe_total = FlextUtilities.Conversions.safe_int(total, 0)

                # Validate pagination parameters
                if safe_page < 1:
                    return FlextResult[FlextApiTypes.Core.Dict].fail(
                        "Page must be >= 1"
                    )

                if safe_page_size < 1:
                    return FlextResult[FlextApiTypes.Core.Dict].fail(
                        "Page size must be >= 1"
                    )

                if safe_page_size > FlextApiConstants.Pagination.MAX_PAGE_SIZE:
                    return FlextResult[FlextApiTypes.Core.Dict].fail(
                        f"Page size cannot exceed {FlextApiConstants.Pagination.MAX_PAGE_SIZE}",
                    )

                # Calculate pagination metadata
                total_pages = max(
                    1,
                    (safe_total + safe_page_size - 1) // safe_page_size,
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

                return FlextResult[FlextApiTypes.Core.Dict].ok(response)
            except Exception as e:
                return FlextResult[FlextApiTypes.Core.Dict].fail(
                    f"Paginated response building failed: {e}",
                )


__all__ = [
    "FlextApiUtilities",
]

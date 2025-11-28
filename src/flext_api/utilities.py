"""FLEXT API Utilities - HTTP utilities extending flext-core.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TypeVar
from urllib.parse import urlparse

from flext_core import FlextResult, FlextTypes, FlextUtilities
from flext_core.typings import GeneralValueType

from flext_api.constants import FlextApiConstants
from flext_api.typings import FlextApiTypes

T = TypeVar("T")


class FlextApiUtilities(FlextUtilities):
    """HTTP-specific utilities with complete flext-core integration."""

    class ValidationUtils:
        """Generic validation utilities for flext-api."""

        @staticmethod
        def validate_host(host: str) -> FlextResult[str]:
            """Validate host string using FlextCore."""
            return FlextUtilities.Validation.validate_hostname(host, perform_dns_lookup=False)

        @staticmethod
        def validate_port(port: int) -> FlextResult[int]:
            """Validate port number using FlextCore."""
            return FlextUtilities.Validation.validate_port_number(port)

        @staticmethod
        def validate_string_field(value: str, field_name: str) -> FlextResult[str]:
            """Validate string field using FlextCore."""
            try:
                return FlextResult[str].ok(FlextUtilities.Validation.validate_required_string(value, field_name))
            except ValueError as e:
                return FlextResult[str].fail(str(e))

    class FlextWebValidator:
        """HTTP validation utilities for flext-api."""

        @staticmethod
        def validate_http_method(
            method: FlextApiConstants.Method | str,
        ) -> bool:
            """Validate HTTP method using constants."""
            return method.upper() in FlextApiConstants.VALID_METHODS

        @staticmethod
        def normalize_url(url: str) -> str:
            """Normalize URL format using constants."""
            if not url:
                return ""

            parsed = urlparse(url)
            if not parsed.scheme:
                # Use HTTPS constant as default scheme
                return f"{FlextApiConstants.HTTP.Protocol.HTTPS}://{url}"

            return url

        @staticmethod
        def validate_url(url: str) -> FlextResult[str]:
            """Validate URL with FlextResult pattern."""
            if not url.strip():
                return FlextResult[str].fail("URL cannot be empty")

            # Check max length using constant directly
            max_len = FlextApiConstants.MAX_URL_LENGTH
            if len(url) > max_len:
                return FlextResult[str].fail(f"URL too long (max {max_len} characters)")

            try:
                parsed = urlparse(url)
                # Validate URL components
                if not parsed.scheme:
                    return FlextResult[str].fail("Invalid URL format: missing scheme")
                if not parsed.netloc:
                    return FlextResult[str].fail("Invalid URL format: missing netloc")

                # Validate port if present
                if ":" in parsed.netloc:
                    parts = parsed.netloc.rsplit(":", 1)
                    try:
                        port = int(parts[1])
                        if port < FlextApiConstants.MIN_PORT:
                            min_port = FlextApiConstants.MIN_PORT
                            return FlextResult[str].fail(
                                f"Invalid port {port}: below minimum {min_port}"
                            )
                        if port > FlextApiConstants.MAX_PORT:
                            max_port = FlextApiConstants.MAX_PORT
                            return FlextResult[str].fail(
                                f"Invalid port {port}: above maximum {max_port}"
                            )
                    except ValueError:
                        return FlextResult[str].fail("Invalid port number")

                return FlextResult[str].ok(url)
            except Exception as e:
                return FlextResult[str].fail(f"Invalid URL: {e}")

    class ResponseBuilder:
        """HTTP response builder using flext-core patterns."""

        @staticmethod
        def build_error_response(
            *,
            message: str,
            status_code: int = 500,
            error_code: str | None = None,
        ) -> FlextApiTypes.JsonObject:
            """Build error response."""
            code_value: str
            if error_code is not None:
                code_value = error_code
            else:
                code_value = f"ERROR_{status_code}"
            return {
                "success": False,
                "error": {
                    "message": message,
                    "code": code_value,
                    "status_code": status_code,
                },
            }

        @staticmethod
        def build_success_response(
            data: FlextApiTypes.JsonObject | None = None,
            message: str | None = None,
            status_code: int = 200,
            headers: FlextApiTypes.WebHeaders | None = None,
        ) -> FlextResult[FlextApiTypes.JsonObject]:
            """Build a successful HTTP response."""
            response_data: FlextApiTypes.JsonObject = {}
            if data is not None:
                response_data = data
            response_headers: FlextApiTypes.WebHeaders = {}
            if headers is not None:
                response_headers = headers
            response: FlextApiTypes.JsonObject = {
                "status": "success",
                "status_code": status_code,
                "data": response_data,
                "message": message,
                "headers": response_headers,
                "timestamp": datetime.now(UTC).isoformat(),
            }
            return FlextResult.ok(response)

        @staticmethod
        def build_error_result(
            error: str,
            status_code: int = 400,
            data: FlextApiTypes.JsonObject | None = None,
            headers: FlextApiTypes.WebHeaders | None = None,
        ) -> FlextResult[FlextApiTypes.JsonObject]:
            """Build an error HTTP response as FlextResult."""
            error_data: FlextApiTypes.JsonObject = {}
            if data is not None:
                error_data = data
            error_headers: FlextApiTypes.WebHeaders = {}
            if headers is not None:
                error_headers = headers
            response: FlextApiTypes.JsonObject = {
                "status": "error",
                "status_code": status_code,
                "error": error,
                "data": error_data,
                "headers": error_headers,
                "timestamp": datetime.now(UTC).isoformat(),
            }
            return FlextResult.ok(response)

    class PaginationBuilder:
        """HTTP pagination builder using flext-core patterns."""

        @staticmethod
        def extract_page_params(
            query_params: dict[str, str],
        ) -> FlextResult[tuple[int, int]]:
            """Extract page and page_size from query parameters - delegate to core."""
            return FlextUtilities.Pagination.extract_page_params(
                query_params,
                default_page=FlextApiConstants.PaginationDefaults.DEFAULT_PAGE,
                default_page_size=FlextApiConstants.DEFAULT_PAGE_SIZE,
                max_page_size=FlextApiConstants.MAX_PAGE_SIZE,
            )

        @staticmethod
        def build_paginated_response(
            data: list[object] | None,
            *,
            page: int = 1,
            page_size: int | None = None,
            total: int | None = None,
            message: str | None = None,
            config: object | None = None,
        ) -> FlextResult[FlextApiTypes.JsonObject]:
            """Build paginated response using flext-core patterns - delegate to core.

            Returns:
            FlextResult containing paginated response dictionary.

            """
            # Extract config using core utility
            config_dict = FlextUtilities.Pagination.extract_pagination_config(config)
            max_page_size_value = config_dict["max_page_size"]

            # Use core pagination utilities directly
            return (
                FlextUtilities.Pagination.validate_pagination_params(
                    page=page, page_size=page_size, max_page_size=max_page_size_value
                )
                .flat_map(
                    lambda params: FlextUtilities.Pagination.prepare_pagination_data(
                        data=data, total=total, page=params["page"], page_size=params["page_size"]
                    )
                )
                .flat_map(
                    lambda pagination_data: FlextUtilities.Pagination.build_pagination_response(
                        pagination_data, message
                    )
                )
            )

        @staticmethod
        def extract_pagination_config(config: object | None) -> dict[str, int]:
            """Extract pagination configuration values - delegate to core."""
            return FlextUtilities.Pagination.extract_pagination_config(config)

        @staticmethod
        def validate_pagination_params(
            *, page: int, page_size: int | None, max_page_size: int
        ) -> FlextResult[dict[str, int]]:
            """Validate pagination parameters - delegate to core."""
            return FlextUtilities.Pagination.validate_pagination_params(
                page=page, page_size=page_size, max_page_size=max_page_size
            )

        @staticmethod
        def prepare_pagination_data(
            *,
            data: list[object] | None,
            total: int | None,
            page: int,
            page_size: int,
            **_kwargs: object,
        ) -> FlextResult[FlextApiTypes.JsonObject]:
            """Prepare pagination data - delegate to core."""
            return FlextUtilities.Pagination.prepare_pagination_data(
                data=data, total=total, page=page, page_size=page_size
            )

        @staticmethod
        def build_pagination_response(
            pagination_data: FlextApiTypes.JsonObject, message: str | None = None
        ) -> FlextResult[FlextApiTypes.JsonObject]:
            """Build pagination response - delegate to core."""
            return FlextUtilities.Pagination.build_pagination_response(
                pagination_data, message
            )

    class JsonUtils:
        """JSON utility functions for type normalization."""

        @staticmethod
        def normalize_to_json_value(value: GeneralValueType) -> FlextTypes.JsonValue:
            """Normalize any object to JsonValue-compatible type - delegate to core."""
            return FlextUtilities.DataMapper.convert_to_json_value(value)


__all__ = [
    "FlextApiUtilities",
]

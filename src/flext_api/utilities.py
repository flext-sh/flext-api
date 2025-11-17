"""FLEXT API Utilities - HTTP utilities extending flext-core.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, TypeVar
from urllib.parse import urlparse

from flext_core import FlextResult, FlextUtilities

from flext_api.constants import FlextApiConstants

T = TypeVar("T")


class FlextApiUtilities(FlextUtilities):
    """HTTP-specific utilities with complete flext-core integration."""

    class FlextWebValidator:
        """HTTP validation utilities for flext-api."""

        @staticmethod
        def validate_http_method(method: str) -> bool:
            """Validate HTTP method using constants."""
            return method.upper() in FlextApiConstants.Method.VALID_METHODS

        @staticmethod
        def normalize_url(url: str) -> str:
            """Normalize URL format using constants."""
            if not url:
                return ""

            parsed = urlparse(url)
            if not parsed.scheme:
                # Use HTTPS constant as default scheme
                return f"{FlextApiConstants.HTTP.PROTOCOL_HTTPS}://{url}"

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
                            return FlextResult[str].fail(
                                f"Invalid port {port}: below minimum {FlextApiConstants.MIN_PORT}"
                            )
                        if port > FlextApiConstants.MAX_PORT:
                            return FlextResult[str].fail(
                                f"Invalid port {port}: above maximum {FlextApiConstants.MAX_PORT}"
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
        ) -> dict[str, Any]:
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
            data: dict[str, Any] | None = None,
            message: str | None = None,
            status_code: int = 200,
            headers: dict[str, Any] | None = None,
        ) -> FlextResult[dict[str, Any]]:
            """Build a successful HTTP response."""
            response_data: dict[str, Any] = {}
            if data is not None:
                response_data = data
            response_headers: dict[str, Any] = {}
            if headers is not None:
                response_headers = headers
            response: dict[str, Any] = {
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
            data: dict[str, Any] | None = None,
            headers: dict[str, Any] | None = None,
        ) -> FlextResult[dict[str, Any]]:
            """Build an error HTTP response as FlextResult."""
            error_data: dict[str, Any] = {}
            if data is not None:
                error_data = data
            error_headers: dict[str, Any] = {}
            if headers is not None:
                error_headers = headers
            response: dict[str, Any] = {
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
            """Extract page and page_size from query parameters."""
            page_str = str(FlextApiConstants.PaginationDefaults.DEFAULT_PAGE)
            if "page" in query_params:
                page_value = query_params["page"]
                if isinstance(page_value, str):
                    page_str = page_value

            page_size_str = (
                FlextApiConstants.PaginationDefaults.DEFAULT_PAGE_SIZE_STRING
            )
            if "page_size" in query_params:
                page_size_value = query_params["page_size"]
                if isinstance(page_size_value, str):
                    page_size_str = page_size_value

            try:
                page = int(page_str)
                page_size = int(page_size_str)

                if page < 1:
                    return FlextResult.fail("Page must be >= 1")
                if page_size < 1:
                    return FlextResult.fail("Page size must be >= 1")
                if page_size > FlextApiConstants.MAX_PAGE_SIZE:
                    return FlextResult.fail(
                        f"Page size must be <= {FlextApiConstants.MAX_PAGE_SIZE}"
                    )

                return FlextResult.ok((page, page_size))
            except ValueError as e:
                return FlextResult.fail(f"Invalid page parameters: {e}")

        @staticmethod
        def build_paginated_response(
            data: list[object] | None,
            *,
            page: int = 1,
            page_size: int | None = None,
            total: int | None = None,
            message: str | None = None,
            config: object | None = None,
        ) -> FlextResult[dict[str, Any]]:
            """Build paginated response using flext-core patterns.

            Returns:
            FlextResult containing paginated response dictionary.

            """
            # Extract config first (handle None case)
            config_dict = FlextApiUtilities.PaginationBuilder.extract_pagination_config(
                config
            )

            # Railway-oriented pagination building
            return (
                FlextResult[dict[str, object]]
                .ok(config_dict)
                .flat_map(
                    lambda cfg_dict: FlextApiUtilities.PaginationBuilder.validate_pagination_params(
                        page=page,
                        page_size=page_size,
                        max_page_size=cfg_dict["max_page_size"],
                    )
                )
                .flat_map(
                    lambda params: FlextApiUtilities.PaginationBuilder.prepare_pagination_data(
                        data=data, total=total, **params
                    )
                )
                .flat_map(
                    lambda pagination_data: FlextApiUtilities.PaginationBuilder.build_pagination_response(
                        pagination_data, message
                    )
                )
            )

        @staticmethod
        def extract_pagination_config(config: object | None) -> dict[str, Any]:
            """Extract pagination configuration values - no fallbacks."""
            # Use Constants defaults when config is None
            default_page_size = FlextApiConstants.DEFAULT_PAGE_SIZE
            max_page_size = FlextApiConstants.MAX_PAGE_SIZE

            if config is not None:
                if hasattr(config, "default_page_size"):
                    default_page_size_value = config.default_page_size
                    if (
                        isinstance(default_page_size_value, int)
                        and default_page_size_value > 0
                    ):
                        default_page_size = default_page_size_value

                if hasattr(config, "max_page_size"):
                    max_page_size_value = config.max_page_size
                    if isinstance(max_page_size_value, int) and max_page_size_value > 0:
                        max_page_size = max_page_size_value

            return {
                "default_page_size": default_page_size,
                "max_page_size": max_page_size,
            }

        @staticmethod
        def validate_pagination_params(
            *, page: int, page_size: int | None, max_page_size: int
        ) -> FlextResult[dict[str, object]]:
            """Validate pagination parameters."""
            # Use default from constants if page_size is None
            if page_size is None:
                effective_page_size = FlextApiConstants.DEFAULT_PAGE_SIZE
            else:
                effective_page_size = page_size

            if page < 1:
                return FlextResult.fail("Page must be >= 1")
            if effective_page_size < 1:
                return FlextResult.fail("Page size must be >= 1")
            if effective_page_size > max_page_size:
                return FlextResult.fail(f"Page size cannot exceed {max_page_size}")

            return FlextResult.ok({
                "page": page,
                "page_size": effective_page_size,
                "max_page_size": max_page_size,
            })

        @staticmethod
        def prepare_pagination_data(
            *,
            data: list[object] | None,
            total: int | None,
            page: int,
            page_size: int,
            **_kwargs: object,
        ) -> FlextResult[dict[str, object]]:
            """Prepare pagination data and calculations - no fallbacks."""
            # data can be None (empty list) or actual list
            final_data: list[object] = data if data is not None else []
            # total must be provided or calculated from data length
            final_total: int = total if total is not None else len(final_data)

            total_pages = (
                max(1, (final_total + page_size - 1) // page_size)
                if final_total > 0
                else 1
            )

            return FlextResult.ok({
                "data": final_data,
                "total": final_total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
                "next_page": page + 1 if page < total_pages else None,
                "prev_page": page - 1 if page > 1 else None,
            })

        @staticmethod
        def build_pagination_response(
            pagination_data: dict, message: str | None = None
        ) -> FlextResult[dict[str, object]]:
            """Build the final pagination response."""
            response = {
                "success": True,
                "data": pagination_data["data"],
                "pagination": {
                    "page": pagination_data["page"],
                    "page_size": pagination_data["page_size"],
                    "total": pagination_data["total"],
                    "total_pages": pagination_data["total_pages"],
                    "has_next": pagination_data["has_next"],
                    "has_prev": pagination_data["has_prev"],
                    "next_page": pagination_data["next_page"],
                    "prev_page": pagination_data["prev_page"],
                },
            }

            if message:
                response["message"] = message

            return FlextResult.ok(response)


__all__ = [
    "FlextApiUtilities",
]

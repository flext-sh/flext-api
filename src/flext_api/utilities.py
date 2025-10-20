"""FLEXT API Utilities - HTTP utilities extending flext-core.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TypeVar
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
            """Validate HTTP method."""
            valid_methods = {
                "GET",
                "POST",
                "PUT",
                "DELETE",
                "PATCH",
                "HEAD",
                "OPTIONS",
                "CONNECT",
                "TRACE",
            }
            return method.upper() in valid_methods

        @staticmethod
        def normalize_url(url: str) -> str:
            """Normalize URL format."""
            if not url:
                return ""

            parsed = urlparse(url)
            if not parsed.scheme:
                return f"https://{url}"

            return url

        @staticmethod
        def validate_url(url: str) -> FlextResult[str]:
            """Validate URL with FlextResult pattern."""
            if not url or not url.strip():
                return FlextResult[str].fail("URL cannot be empty")

            # Check max length
            max_len: object = FlextApiConstants.VALIDATION_LIMITS.get(
                "MAX_URL_LENGTH", 2048
            )
            if len(url) > int(max_len):
                return FlextResult[str].fail(
                    f"URL too long (max {max_len} characters)"
                )

            try:
                parsed = urlparse(url)
                # Validate URL components
                if not parsed.scheme or not parsed.netloc:
                    return FlextResult[str].fail("Invalid URL format")

                # Validate port if present
                if ":" in parsed.netloc:
                    parts = parsed.netloc.rsplit(":", 1)
                    try:
                        port = int(parts[1])
                        if port <= 0 or port > 65535:
                            return FlextResult[str].fail(f"Invalid port {port}")
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
        ) -> dict[str, object]:
            """Build error response."""
            return {
                "success": False,
                "error": {
                    "message": message,
                    "code": error_code or f"ERROR_{status_code}",
                    "status_code": status_code,
                },
            }

        @staticmethod
        def build_success_response(
            data: dict[str, object] | None = None,
            message: str | None = None,
            status_code: int = 200,
            headers: dict[str, object] | None = None,
        ) -> FlextResult[dict[str, object]]:
            """Build a successful HTTP response."""
            response: dict[str, object] = {
                "status": "success",
                "status_code": status_code,
                "data": data or {},
                "message": message,
                "headers": headers or {},
                "timestamp": datetime.now(UTC).isoformat(),
            }
            return FlextResult.ok(response)

        @staticmethod
        def build_error_result(
            error: str,
            status_code: int = 400,
            data: dict[str, object] | None = None,
            headers: dict[str, object] | None = None,
        ) -> FlextResult[dict[str, object]]:
            """Build an error HTTP response as FlextResult."""
            response: dict[str, object] = {
                "status": "error",
                "status_code": status_code,
                "error": error,
                "data": data or {},
                "headers": headers or {},
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
            try:
                page = int(query_params.get("page", "1"))
                page_size = int(query_params.get("page_size", "20"))

                if page < 1:
                    return FlextResult.fail("Page must be >= 1")
                if page_size < 1 or page_size > FlextApiConstants.MAX_PAGE_SIZE:
                    return FlextResult.fail(
                        f"Page size must be between 1 and {FlextApiConstants.MAX_PAGE_SIZE}"
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
        ) -> FlextResult[dict[str, object]]:
            """Build paginated response using flext-core patterns.

            Returns:
                FlextResult containing paginated response dictionary.

            """
            # Railway-oriented pagination building
            return (
                FlextResult[object]
                .ok(config)
                .map(FlextApiUtilities.PaginationBuilder.extract_pagination_config)
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
        def extract_pagination_config(config: object | None) -> dict[str, object]:
            """Extract pagination configuration values."""
            default_page_size = (
                getattr(config, "default_page_size", 20) if config else 20
            )
            max_page_size = getattr(config, "max_page_size", 1000) if config else 1000
            return {
                "default_page_size": default_page_size,
                "max_page_size": max_page_size,
            }

        @staticmethod
        def validate_pagination_params(
            *, page: int, page_size: int | None, max_page_size: int
        ) -> FlextResult[dict]:
            """Validate pagination parameters."""
            # If page_size is explicitly provided (not None), use it directly
            # Otherwise, use default but don't override explicit 0
            effective_page_size = page_size if page_size is not None else 20

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
        ) -> FlextResult[dict]:
            """Prepare pagination data and calculations."""
            final_data = data or []
            final_total = total if total is not None else len(final_data)

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
        ) -> FlextResult[dict]:
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

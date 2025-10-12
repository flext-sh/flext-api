"""FLEXT API Utilities - HTTP utilities extending flext-core.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TypeVar
from urllib.parse import urlparse, urlunparse

from flext_core import FlextCore

from flext_api.constants import FlextApiConstants

T = TypeVar("T")


class FlextApiUtilities(FlextCore.Utilities):
    """HTTP-specific utilities with complete flext-core integration."""

    class ResponseBuilder:
        """HTTP response builder using flext-core patterns."""

        @staticmethod
        def build_success_response(
            data: FlextCore.Types.Dict | None = None,
            message: str | None = None,
            status_code: int = 200,
            headers: FlextCore.Types.Dict | None = None,
        ) -> FlextCore.Result[dict[str, object]]:
            """Build a successful HTTP response."""
            response: dict[str, object] = {
                "status": "success",
                "status_code": status_code,
                "data": data or {},
                "message": message,
                "headers": headers or {},
                "timestamp": datetime.now(UTC).isoformat(),
            }
            return FlextCore.Result.ok(response)

        @staticmethod
        def build_error_response(
            error: str,
            status_code: int = 400,
            data: FlextCore.Types.Dict | None = None,
            headers: FlextCore.Types.Dict | None = None,
        ) -> FlextCore.Result[dict[str, object]]:
            """Build an error HTTP response."""
            response: dict[str, object] = {
                "status": "error",
                "status_code": status_code,
                "error": error,
                "data": data or {},
                "headers": headers or {},
                "timestamp": datetime.now(UTC).isoformat(),
            }
            return FlextCore.Result.ok(response)

    class PaginationBuilder:
        """HTTP pagination builder using flext-core patterns."""

        @staticmethod
        def extract_page_params(
            query_params: dict[str, str],
        ) -> FlextCore.Result[tuple[int, int]]:
            """Extract page and page_size from query parameters."""
            try:
                page = int(query_params.get("page", "1"))
                page_size = int(query_params.get("page_size", "20"))

                if page < 1:
                    return FlextCore.Result.fail("Page must be >= 1")
                if page_size < 1 or page_size > FlextApiConstants.MAX_PAGE_SIZE:
                    return FlextCore.Result.fail(
                        f"Page size must be between 1 and {FlextApiConstants.MAX_PAGE_SIZE}"
                    )

                return FlextCore.Result.ok((page, page_size))
            except ValueError as e:
                return FlextCore.Result.fail(f"Invalid page parameters: {e}")

        @staticmethod
        def build_paginated_response(
            data: FlextCore.Types.List | None,
            *,
            page: int = 1,
            page_size: int | None = None,
            total: int | None = None,
            message: str | None = None,
            config: object | None = None,
        ) -> FlextCore.Result[FlextCore.Types.Dict]:
            """Build paginated response using flext-core patterns.

            Returns:
                FlextCore.Result containing paginated response dictionary.

            """
            # Railway-oriented pagination building
            return (
                FlextCore.Result[object]
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
        def extract_pagination_config(config: object | None) -> dict:
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
        ) -> FlextCore.Result[dict]:
            """Validate pagination parameters."""
            effective_page_size = page_size or 20  # Will be overridden by config

            if page < 1:
                return FlextCore.Result.fail("Page must be >= 1")
            if effective_page_size < 1:
                return FlextCore.Result.fail("Page size must be >= 1")
            if effective_page_size > max_page_size:
                return FlextCore.Result.fail(f"Page size cannot exceed {max_page_size}")

            return FlextCore.Result.ok({
                "page": page,
                "page_size": effective_page_size,
                "max_page_size": max_page_size,
            })

        @staticmethod
        def prepare_pagination_data(
            *,
            data: FlextCore.Types.List | None,
            total: int | None,
            page: int,
            page_size: int,
            **_kwargs: object,
        ) -> FlextCore.Result[dict]:
            """Prepare pagination data and calculations."""
            final_data = data or []
            final_total = total if total is not None else len(final_data)

            total_pages = (
                max(1, (final_total + page_size - 1) // page_size)
                if final_total > 0
                else 1
            )

            return FlextCore.Result.ok({
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
        ) -> FlextCore.Result[dict]:
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

            return FlextCore.Result.ok(response)

    class HttpValidator:
        """HTTP validation utilities."""

        MAX_URL_LENGTH: int = FlextApiConstants.MAX_URL_LENGTH

        @staticmethod
        def validate_and_normalize_url(url: str) -> FlextCore.Result[str]:
            """Validate and normalize a URL."""
            if not url or not url.strip():
                return FlextCore.Result[str].fail("URL cannot be empty")

            if len(url) > FlextApiConstants.MAX_URL_LENGTH:
                return FlextCore.Result[str].fail(
                    f"URL too long (max {FlextApiConstants.MAX_URL_LENGTH} characters)"
                )

            # Add http:// if no scheme
            if not url.startswith(("http://", "https://")):
                url = f"http://{url}"

            try:
                parsed = urlparse(url)
                if not parsed.netloc:
                    return FlextCore.Result.fail("Invalid URL format")

                # Reconstruct URL to normalize
                normalized = urlunparse(parsed)
                return FlextCore.Result.ok(str(normalized))
            except Exception as e:
                return FlextCore.Result.fail(f"Invalid URL: {e}")

        @staticmethod
        def validate_url(url: str) -> FlextCore.Result[str]:
            """Validate a URL without normalizing."""
            if not url or not url.strip():
                return FlextCore.Result.fail("URL cannot be empty")

            if len(url) > FlextApiConstants.MAX_URL_LENGTH:
                return FlextCore.Result.fail(
                    f"URL too long (max {FlextApiConstants.MAX_URL_LENGTH} characters)"
                )

            try:
                parsed = urlparse(url)
                if not parsed.scheme or not parsed.netloc:
                    return FlextCore.Result.fail("Invalid URL format")
                return FlextCore.Result.ok(url)
            except Exception as e:
                return FlextCore.Result.fail(f"Invalid URL: {e}")


__all__ = [
    "FlextApiUtilities",
]

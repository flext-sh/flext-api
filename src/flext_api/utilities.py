"""FlextApi utilities module."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, TypeIs
from urllib.parse import urlparse

from flext_core import FlextUtilities, r
from pydantic import BeforeValidator

from flext_api.typings import t

# Local constants to avoid circular import with constants.py
MAX_HOSTNAME_LENGTH: int = 253
MAX_PORT: int = 65535
VALID_HTTP_METHODS: frozenset[str] = frozenset({
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "PATCH",
    "HEAD",
    "OPTIONS",
    "CONNECT",
    "TRACE",
})


class FlextApiUtilities(FlextUtilities):
    """FlextApi utilities extending FlextUtilities with API-specific helpers.

    Architecture: Advanced utilities with ZERO code bloat through:
    - TypeIs/TypeGuard for narrowing (PEP 742)
    - BeforeValidator factories for Pydantic coercion
    - @validated decorators eliminating manual validation
    - Generic parsing utilities for StrEnums (inherited from parent)
    """

    # ═══════════════════════════════════════════════════════════════════
    # API NAMESPACE: Project-specific utilities
    # ═══════════════════════════════════════════════════════════════════

    class Api:
        """API-specific utility namespace.

        This namespace groups all API-specific utilities for better organization
        and cross-project access. Access via FlextUtilities.Api.* pattern.

        Example:
            from flext_api.utilities import u
            result = FlextUtilities.Api.Collection.parse_sequence(Status, ["active", "pending"])
            parsed = FlextUtilities.Api.Args.parse_kwargs(kwargs, enum_fields)

        """

        class Collection(FlextUtilities.Collection):
            """Collection utilities extending u.Collection via inheritance.

            Exposes all flext-core Collection methods through inheritance hierarchy.
            Access via FlextUtilities.Api.Collection.* pattern.
            """

        class Args(FlextUtilities.Args):
            """Args utilities extending u.Args via inheritance.

            Exposes all flext-core Args methods through inheritance hierarchy,
            including validated, validated_with_result, parse_kwargs, and get_enum_params.
            Access via FlextUtilities.Api.Args.* pattern.
            """

        class Model(FlextUtilities.Model):
            """Model utilities extending u.Model via inheritance.

            Exposes all flext-core Model methods through inheritance hierarchy.
            Access via FlextUtilities.Api.Model.* pattern.
            """

        class Pydantic:
            """Annotated type factories."""

            @staticmethod
            def coerced_enum[E: StrEnum](enum_cls: type[E]) -> t.GeneralValueType:
                """Create Annotated type with automatic enum coercion."""
                return Annotated[
                    enum_cls,
                    BeforeValidator(FlextUtilities.Enum.coerce_validator(enum_cls)),
                ]

        class RequestUtils:
            """Request utilities for extracting and validating HTTP request components."""

            @staticmethod
            def to_json_value(value: t.GeneralValueType) -> t.JsonValue:
                """Normalize arbitrary value to JsonValue."""
                if value is None or isinstance(value, str | int | float | bool):
                    return value
                if isinstance(value, Mapping):
                    converted: t.JsonObject = {}
                    for key, item in value.items():
                        converted[str(key)] = (
                            FlextApiUtilities.Api.RequestUtils.to_json_value(item)
                        )
                    return converted
                if isinstance(value, Sequence) and not isinstance(value, str | bytes):
                    return [
                        FlextApiUtilities.Api.RequestUtils.to_json_value(item)
                        for item in value
                    ]
                if isinstance(value, bytes):
                    return value.decode("utf-8", errors="replace")
                return str(value)

            @staticmethod
            def to_request_body(value: t.GeneralValueType) -> t.Api.RequestBody:
                """Convert arbitrary value to RequestBody-compatible payload."""
                if isinstance(value, str | bytes):
                    return value
                if isinstance(value, Mapping):
                    normalized: t.Api.JsonObject = {}
                    for key, item in value.items():
                        key_str = str(key)
                        normalized[key_str] = (
                            FlextApiUtilities.Api.RequestUtils.to_json_value(item)
                        )
                    return normalized
                return str(value)

            @staticmethod
            def extract_body_from_kwargs(
                data: t.Api.RequestBody | None,
                kwargs: Mapping[str, t.ApiJsonValue] | None,
            ) -> r[t.Api.RequestBody]:
                """Extract body from data or kwargs - returns empty dict if no body found."""
                if data is not None:
                    return r[t.Api.RequestBody].ok(data)
                if kwargs is not None and "data" in kwargs:
                    raw_data = kwargs["data"]
                    return r[t.Api.RequestBody].ok(
                        FlextApiUtilities.Api.RequestUtils.to_request_body(raw_data)
                    )
                if kwargs is not None and "json" in kwargs:
                    raw_json = kwargs["json"]
                    return r[t.Api.RequestBody].ok(
                        FlextApiUtilities.Api.RequestUtils.to_request_body(raw_json)
                    )
                return r[t.Api.RequestBody].ok({})

            @staticmethod
            def merge_headers(
                headers: Mapping[str, str] | None,
                kwargs: Mapping[str, t.ApiJsonValue] | None,
            ) -> r[Mapping[str, str]]:
                """Merge headers from headers dict and kwargs."""
                merged: dict[str, str] = {}
                if headers:
                    merged.update(headers)
                if kwargs and "headers" in kwargs:
                    headers_value = kwargs["headers"]
                    if u.is_dict_like(headers_value):
                        merged.update({k: str(v) for k, v in headers_value.items()})
                return r.ok(merged)

            @staticmethod
            def validate_and_extract_timeout(
                timeout: float | str | None,
                kwargs: Mapping[str, t.ApiJsonValue] | None,
            ) -> r[float]:
                """Validate and extract timeout from timeout value or kwargs.

                Returns default timeout of 30.0 if not specified.
                Coerces string/int values to float.
                Fails if timeout is explicitly provided but invalid.
                """
                # If timeout is explicitly provided, it must be valid
                if timeout is not None:
                    try:
                        timeout_float = float(timeout)
                        if timeout_float > 0:
                            return r.ok(timeout_float)
                        return r.fail("Invalid timeout value: must be positive")
                    except (ValueError, TypeError):
                        return r.fail(f"Invalid timeout value: {timeout}")

                # Check kwargs for timeout
                if kwargs and "timeout" in kwargs:
                    timeout_value = kwargs["timeout"]
                    if not isinstance(timeout_value, int | float | str):
                        return r.fail(f"Invalid timeout value: {timeout_value}")
                    try:
                        timeout_float = float(timeout_value)
                        if timeout_float > 0:
                            return r.ok(timeout_float)
                        return r.fail("Invalid timeout value: must be positive")
                    except (ValueError, TypeError):
                        return r.fail(f"Invalid timeout value: {timeout_value}")

                # No timeout specified - use default
                return r.ok(30.0)

    # ═══════════════════════════════════════════════════════════════════
    # RESPONSE BUILDER: Nested inside FlextApiUtilities
    # ═══════════════════════════════════════════════════════════════════

    class ResponseBuilder:
        """Response builder for API responses."""

        @staticmethod
        def build_success_response(
            data: t.ApiJsonValue = None,
            message: str = "Success",
            status_code: int = 200,
            headers: Mapping[str, str] | None = None,
        ) -> r[Mapping[str, t.ApiJsonValue]]:
            """Build success response with optional data and message."""
            response: dict[str, t.ApiJsonValue] = {
                "status": "success",
                "data": data,
                "message": message,
                "status_code": status_code,
                "timestamp": datetime.now(tz=UTC).isoformat(),
            }
            if headers:
                response["headers"] = headers
            return r.ok(response)

        @staticmethod
        def build_error_result(
            error: str,
            status_code: int = 400,
            data: t.ApiJsonValue | None = None,
            headers: Mapping[str, str] | None = None,
        ) -> r[Mapping[str, t.ApiJsonValue]]:
            """Build error result - returns FlextResult with error response."""
            response: dict[str, t.ApiJsonValue] = {
                "error": error,
                "status_code": status_code,
            }
            if data is not None:
                response["data"] = data
            if headers:
                response["headers"] = headers
            return r.ok(response)

        @staticmethod
        def build_error_response(
            message: str,
            status_code: int = 400,
            error_code: str | None = None,
        ) -> Mapping[str, t.ApiJsonValue]:
            """Build error response - returns plain dict."""
            return {
                "success": False,
                "error": {
                    "message": message,
                    "status_code": status_code,
                    "code": error_code,
                },
            }

    # ═══════════════════════════════════════════════════════════════════
    # PAGINATION BUILDER: Nested inside FlextApiUtilities
    # ═══════════════════════════════════════════════════════════════════

    class PaginationBuilder:
        """Pagination builder for paginated responses."""

        @staticmethod
        def extract_page_params(
            params: Mapping[str, t.ApiJsonValue],
        ) -> r[tuple[int, int]]:
            """Extract and validate page and page_size from params dict.

            Returns tuple of (page, page_size).
            Defaults: page=1, page_size=20
            """
            try:
                page_str = params.get("page", "1")
                page_size_str = params.get("page_size", "20")

                if isinstance(page_str, int | float | str):
                    page = int(page_str)
                else:
                    return r.fail("Invalid page parameter")

                if isinstance(page_size_str, int | float | str):
                    page_size = int(page_size_str)
                else:
                    return r.fail("Invalid page_size parameter")

                if page < 1 or page_size < 1:
                    return r.fail("Page and page_size must be >= 1")

                return r.ok((page, page_size))
            except (ValueError, TypeError):
                return r.fail("Invalid page or page_size parameters")

        @staticmethod
        def extract_pagination_config(
            config: t.GeneralValueType,
        ) -> Mapping[str, t.ApiJsonValue]:
            """Extract pagination configuration from config object.

            Reads attributes: default_page_size, max_page_size.
            Provides defaults if not found.
            """
            result: dict[str, t.ApiJsonValue] = {}

            default_page_size = getattr(config, "default_page_size", 20)
            max_page_size = getattr(config, "max_page_size", 1000)

            result["default_page_size"] = (
                FlextApiUtilities.Api.RequestUtils.to_json_value(default_page_size)
            )
            result["max_page_size"] = FlextApiUtilities.Api.RequestUtils.to_json_value(
                max_page_size
            )

            return result

        @staticmethod
        def validate_pagination_params(
            page: int,
            page_size: int,
            max_page_size: int = 1000,
        ) -> r[tuple[int, int]]:
            """Validate pagination parameters.

            Returns tuple of (page, page_size) if valid.
            """
            if page < 1:
                return r.fail("Page must be >= 1")
            if page_size < 1:
                return r.fail("Page size must be >= 1")
            if page_size > max_page_size:
                return r.fail(f"Page size cannot exceed {max_page_size}")

            return r.ok((page, page_size))

        @staticmethod
        def prepare_pagination_data(
            data: list[t.ApiJsonValue],
            total: int,
            page: int,
            page_size: int,
        ) -> r[Mapping[str, t.ApiJsonValue]]:
            """Prepare pagination metadata for response.

            Calculates total_pages, has_next, has_prev, next_page, prev_page.
            """
            if page < 1 or page_size < 1:
                return r.fail("Page and page_size must be >= 1")

            total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
            has_next = page < total_pages
            has_prev = page > 1
            next_page = page + 1 if has_next else None
            prev_page = page - 1 if has_prev else None

            return r.ok({
                "data": data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev,
                "next_page": next_page,
                "prev_page": prev_page,
            })

        @staticmethod
        def build_pagination_response(
            pagination_data: Mapping[str, t.ApiJsonValue],
        ) -> r[Mapping[str, t.ApiJsonValue]]:
            """Build full pagination response from pagination data dict."""
            if "data" not in pagination_data:
                return r.fail("pagination_data must contain 'data' key")

            return r.ok({
                "success": True,
                "pagination": pagination_data,
            })

        @staticmethod
        def build_paginated_response(
            data: list[t.ApiJsonValue],
            page: int,
            page_size: int,
            total: int | None = None,
        ) -> r[Mapping[str, t.ApiJsonValue]]:
            """Build paginated response."""
            if page < 1:
                return r.fail("Page must be >= 1")
            if page_size < 1:
                return r.fail("Page size must be >= 1")

            total_items = total if total is not None else len(data)
            total_pages = (
                (total_items + page_size - 1) // page_size if page_size > 0 else 0
            )

            return r.ok({
                "success": True,
                "data": data,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total_items,
                    "total_pages": total_pages,
                },
            })

    # ═══════════════════════════════════════════════════════════════════
    # WEB VALIDATOR: Nested inside FlextApiUtilities
    # ═══════════════════════════════════════════════════════════════════

    class FlextWebValidator:
        """Web validation utilities for URLs and HTTP methods."""

        @staticmethod
        def validate_hostname(host: str) -> r[str]:
            """Validate hostname format."""
            if not host or not host.strip():
                return r.fail("Hostname cannot be empty")

            if len(host) > MAX_HOSTNAME_LENGTH:
                return r.fail("Hostname too long")

            pattern = r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$|^localhost$|^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$"
            if not re.match(pattern, host):
                return r.fail("Invalid hostname format")

            return r.ok(host)

        @staticmethod
        def validate_url(url: str) -> r[str]:
            """Validate URL format and structure."""
            if not url or not url.strip():
                return r.fail("URL cannot be empty")

            try:
                parsed = urlparse(url)
                if not parsed.scheme or parsed.scheme not in {"http", "https"}:
                    return r.fail(f"Invalid URL scheme: {parsed.scheme}")
                if not parsed.netloc:
                    return r.fail("URL must have a valid host")
                if parsed.port is not None and (
                    parsed.port < 1 or parsed.port > MAX_PORT
                ):
                    return r.fail(f"Invalid port {parsed.port}")
                return r.ok(url)
            except (ValueError, TypeError, KeyError, ConnectionError) as e:
                return r.fail(f"Invalid URL: {e}")

        @staticmethod
        def is_valid_port_number(port: t.GeneralValueType) -> TypeIs[int]:
            """Check if port is a valid port number (TypeIs for precise narrowing)."""
            if not isinstance(port, int):
                return False
            return 1 <= port <= MAX_PORT

        @staticmethod
        def validate_port_number(port: int) -> r[int]:
            """Validate port number range."""
            if port < 1 or port > MAX_PORT:
                return r.fail(f"Port must be between 1 and {MAX_PORT}")
            return r.ok(port)

        @staticmethod
        def validate_http_method(method: str) -> bool:
            """Validate HTTP method."""
            return method.upper() in VALID_HTTP_METHODS

        @staticmethod
        def normalize_url(url: str) -> str:
            """Normalize URL by adding https:// if no scheme."""
            if not url:
                return ""
            if not url.startswith(("http://", "https://")):
                return f"https://{url}"
            return url


# Short alias for runtime access
u = FlextApiUtilities

__all__ = [
    "FlextApiUtilities",
    "u",
]

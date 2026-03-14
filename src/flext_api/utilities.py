"""FlextApi utilities module."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, TypeIs
from urllib.parse import urlparse

from flext_core import FlextUtilities, r
from flext_web import FlextWebUtilities
from pydantic import BeforeValidator

from flext_api import t

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


class FlextApiUtilities(FlextWebUtilities):
    """FlextApi utilities extending FlextUtilities with API-specific helpers.

    Architecture: Advanced utilities with ZERO code bloat through:
    - TypeIs/TypeGuard for narrowing (PEP 742)
    - BeforeValidator factories for Pydantic coercion
    - @validated decorators eliminating manual validation
    - Generic parsing utilities for StrEnums (inherited from parent)
    """

    class Api:
        """API-specific utility namespace.

        This namespace groups all API-specific utilities for better organization
        and cross-project access. Access via FlextUtilities.Api.* pattern.

        Example:
            from flext_api import u
            result = FlextUtilities.Api.Collection.parse_sequence(Status, ["active", "pending"])
            parsed = FlextUtilities.Api.Args.parse_kwargs(kwargs, enum_fields)

        """

        class Pydantic:
            """Annotated type factories."""

            @staticmethod
            def coerced_enum[E: StrEnum](enum_cls: type[E]) -> t.ContainerValue:
                """Create Annotated type with automatic enum coercion."""
                return Annotated[
                    enum_cls,
                    BeforeValidator(FlextUtilities.Enum.coerce_validator(enum_cls)),
                ]

        class RequestUtils:
            """Request utilities for extracting and validating HTTP request components."""

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
                    if isinstance(headers_value, dict):
                        merged.update({k: str(v) for k, v in headers_value.items()})
                return r[Mapping[str, str]].ok(merged)

            @staticmethod
            def to_json_value(value: t.ContainerValue) -> t.ApiJsonValue:
                """Normalize arbitrary value to object."""
                if value is None or isinstance(value, t.PRIMITIVES_TYPES):
                    return value
                if isinstance(value, Mapping):
                    converted: t.JsonObject = {}
                    for key, item in value.items():
                        converted[str(key)] = (
                            FlextApiUtilities.Api.RequestUtils.to_json_value(item)
                        )
                    return converted
                if isinstance(value, Sequence) and (not isinstance(value, str | bytes)):
                    return [
                        FlextApiUtilities.Api.RequestUtils.to_json_value(item)
                        for item in value
                    ]
                if isinstance(value, bytes):
                    return value.decode("utf-8", errors="replace")
                return str(value)

            @staticmethod
            def to_request_body(value: t.ContainerValue) -> t.Api.RequestBody:
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
            def validate_and_extract_timeout(
                timeout: float | str | None, kwargs: Mapping[str, t.ApiJsonValue] | None
            ) -> r[float]:
                """Validate and extract timeout from timeout value or kwargs.

                Returns default timeout of 30.0 if not specified.
                Coerces string/int values to float.
                Fails if timeout is explicitly provided but invalid.
                """
                if timeout is not None:
                    try:
                        timeout_float = float(timeout)
                        if timeout_float > 0:
                            return r[float].ok(timeout_float)
                        return r[float].fail("Invalid timeout value: must be positive")
                    except (ValueError, TypeError):
                        return r[float].fail(f"Invalid timeout value: {timeout}")
                if kwargs and "timeout" in kwargs:
                    timeout_value = kwargs["timeout"]
                    if not isinstance(timeout_value, int | float | str):
                        return r[float].fail(f"Invalid timeout value: {timeout_value}")
                    try:
                        timeout_float = float(timeout_value)
                        if timeout_float > 0:
                            return r[float].ok(timeout_float)
                        return r[float].fail("Invalid timeout value: must be positive")
                    except (ValueError, TypeError):
                        return r[float].fail(f"Invalid timeout value: {timeout_value}")
                return r[float].ok(30.0)

    class ResponseBuilder:
        """Response builder for API responses."""

        @staticmethod
        def build_error_response(
            message: str, status_code: int = 400, error_code: str | None = None
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

        @staticmethod
        def build_error_result(
            error: str,
            status_code: int = 400,
            data: t.ApiJsonValue | None = None,
            headers: Mapping[str, str] | None = None,
        ) -> r[Mapping[str, t.ApiJsonValue]]:
            """Build error result - returns r with error response."""
            response: dict[str, t.ApiJsonValue] = {
                "error": error,
                "status_code": status_code,
            }
            if data is not None:
                response["data"] = data
            if headers:
                response["headers"] = headers
            return r[Mapping[str, t.ApiJsonValue]].ok(response)

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
            return r[Mapping[str, t.ApiJsonValue]].ok(response)

    class PaginationBuilder:
        """Pagination builder for paginated responses."""

        @staticmethod
        def build_paginated_response(
            data: list[t.ApiJsonValue],
            page: int,
            page_size: int,
            total: int | None = None,
        ) -> r[Mapping[str, t.ApiJsonValue]]:
            """Build paginated response."""
            if page < 1:
                return r[Mapping[str, t.ApiJsonValue]].fail("Page must be >= 1")
            if page_size < 1:
                return r[Mapping[str, t.ApiJsonValue]].fail("Page size must be >= 1")
            total_items = total if total is not None else len(data)
            total_pages = (
                (total_items + page_size - 1) // page_size if page_size > 0 else 0
            )
            return r[Mapping[str, t.ApiJsonValue]].ok({
                "success": True,
                "data": data,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total_items,
                    "total_pages": total_pages,
                },
            })

        @staticmethod
        def build_pagination_response(
            pagination_data: Mapping[str, t.ApiJsonValue],
        ) -> r[Mapping[str, t.ApiJsonValue]]:
            """Build full pagination response from pagination data dict."""
            if "data" not in pagination_data:
                return r[Mapping[str, t.ApiJsonValue]].fail(
                    "pagination_data must contain 'data' key"
                )
            return r[Mapping[str, t.ApiJsonValue]].ok({
                "success": True,
                "pagination": pagination_data,
            })

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
                    return r[tuple[int, int]].fail("Invalid page parameter")
                if isinstance(page_size_str, int | float | str):
                    page_size = int(page_size_str)
                else:
                    return r[tuple[int, int]].fail("Invalid page_size parameter")
                if page < 1 or page_size < 1:
                    return r[tuple[int, int]].fail("Page and page_size must be >= 1")
                return r[tuple[int, int]].ok((page, page_size))
            except (ValueError, TypeError):
                return r[tuple[int, int]].fail("Invalid page or page_size parameters")

        @staticmethod
        def extract_pagination_config(
            config: t.ContainerValue,
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
        def prepare_pagination_data(
            data: list[t.ApiJsonValue], total: int, page: int, page_size: int
        ) -> r[Mapping[str, t.ApiJsonValue]]:
            """Prepare pagination metadata for response.

            Calculates total_pages, has_next, has_prev, next_page, prev_page.
            """
            if page < 1 or page_size < 1:
                return r[Mapping[str, t.ApiJsonValue]].fail(
                    "Page and page_size must be >= 1"
                )
            total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
            has_next = page < total_pages
            has_prev = page > 1
            next_page = page + 1 if has_next else None
            prev_page = page - 1 if has_prev else None
            return r[Mapping[str, t.ApiJsonValue]].ok({
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
        def validate_pagination_params(
            page: int, page_size: int, max_page_size: int = 1000
        ) -> r[tuple[int, int]]:
            """Validate pagination parameters.

            Returns tuple of (page, page_size) if valid.
            """
            if page < 1:
                return r[tuple[int, int]].fail("Page must be >= 1")
            if page_size < 1:
                return r[tuple[int, int]].fail("Page size must be >= 1")
            if page_size > max_page_size:
                return r[tuple[int, int]].fail(
                    f"Page size cannot exceed {max_page_size}"
                )
            return r[tuple[int, int]].ok((page, page_size))

    class FlextWebValidator:
        """Web validation utilities for URLs and HTTP methods."""

        @staticmethod
        def is_valid_port_number(port: t.ContainerValue) -> TypeIs[int]:
            """Check if port is a valid port number (TypeIs for precise narrowing)."""
            if not isinstance(port, int):
                return False
            return 1 <= port <= MAX_PORT

        @staticmethod
        def normalize_url(url: str) -> str:
            """Normalize URL by adding https:// if no scheme."""
            if not url:
                return ""
            if not url.startswith(("http://", "https://")):
                return f"https://{url}"
            return url

        @staticmethod
        def validate_hostname(host: str) -> r[str]:
            """Validate hostname format."""
            if not host or not host.strip():
                return r[str].fail("Hostname cannot be empty")
            if len(host) > MAX_HOSTNAME_LENGTH:
                return r[str].fail("Hostname too long")
            pattern = "^[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$|^localhost$|^[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+$"
            if not re.match(pattern, host):
                return r[str].fail("Invalid hostname format")
            return r[str].ok(host)

        @staticmethod
        def validate_http_method(method: str) -> bool:
            """Validate HTTP method."""
            return method.upper() in VALID_HTTP_METHODS

        @staticmethod
        def validate_port_number(port: int) -> r[int]:
            """Validate port number range."""
            if port < 1 or port > MAX_PORT:
                return r[int].fail(f"Port must be between 1 and {MAX_PORT}")
            return r[int].ok(port)

        @staticmethod
        def validate_url(url: str) -> r[str]:
            """Validate URL format and structure."""
            if not url or not url.strip():
                return r[str].fail("URL cannot be empty")
            try:
                parsed = urlparse(url)
                if not parsed.scheme or parsed.scheme not in {"http", "https"}:
                    return r[str].fail(f"Invalid URL scheme: {parsed.scheme}")
                if not parsed.netloc:
                    return r[str].fail("URL must have a valid host")
                if parsed.port is not None and (
                    parsed.port < 1 or parsed.port > MAX_PORT
                ):
                    return r[str].fail(f"Invalid port {parsed.port}")
                return r[str].ok(url)
            except (ValueError, TypeError, KeyError, ConnectionError) as e:
                return r[str].fail(f"Invalid URL: {e}")


u = FlextApiUtilities
__all__ = ["FlextApiUtilities", "u"]

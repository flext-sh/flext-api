"""FlextApi utilities module."""

from __future__ import annotations

import re
from collections.abc import Mapping, MutableMapping
from datetime import UTC, datetime
from enum import StrEnum
from typing import TypeIs
from urllib.parse import urlparse

from flext_cli import FlextCliUtilities

from flext_api import t
from flext_core import r, u as core_u
from flext_web import FlextWebUtilities


class FlextApiUtilities(FlextWebUtilities, FlextCliUtilities):
    """FlextApi utilities extending FlextUtilities with API-specific helpers.

    Architecture: Advanced utilities with ZERO code bloat through:
    - TypeIs/TypeGuard for narrowing (PEP 742)
    - BeforeValidator factories for Pydantic coercion
    - @validated decorators eliminating manual validation
    - Generic parsing utilities for StrEnums (inherited from parent)
    """

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
            def coerced_enum_validator(
                enum_cls: type[StrEnum],
            ) -> core_u.BeforeValidator:
                """Create a BeforeValidator for automatic enum coercion.

                Usage in Pydantic models:
                    field: Annotated[MyEnum, u.Api.Pydantic.coerced_enum_validator(MyEnum)]
                """

                def _coerce(v: str | StrEnum) -> StrEnum:
                    result = FlextWebUtilities.parse_enum(enum_cls, v)
                    if result.failure:
                        msg = result.error or f"Invalid {enum_cls.__name__}: {v!r}"
                        raise ValueError(msg)
                    return enum_cls(v) if not isinstance(v, enum_cls) else v

                return core_u.BeforeValidator(_coerce)

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
                    if raw_data is not None:
                        return r[t.Api.RequestBody].ok(
                            FlextApiUtilities.Api.RequestUtils.to_request_body(
                                raw_data,
                            ),
                        )
                if kwargs is not None and "json" in kwargs:
                    raw_json = kwargs["json"]
                    if raw_json is not None:
                        return r[t.Api.RequestBody].ok(
                            FlextApiUtilities.Api.RequestUtils.to_request_body(
                                raw_json,
                            ),
                        )
                return r[t.Api.RequestBody].ok({})

            @staticmethod
            def merge_headers(
                headers: t.StrMapping | None,
                kwargs: Mapping[str, t.ApiJsonValue] | None,
            ) -> r[t.StrMapping]:
                """Merge headers from headers dict and kwargs."""
                merged: t.MutableStrMapping = {}
                if headers:
                    merged.update(headers)
                if kwargs and "headers" in kwargs:
                    headers_value = kwargs["headers"]
                    if headers_value is not None:
                        if not isinstance(headers_value, Mapping):
                            return r[t.StrMapping].fail("Headers must be a mapping")
                        validated_headers = t.Api.STR_MAPPING_ADAPTER.validate_python(
                            headers_value,
                        )
                        merged.update(validated_headers)
                return r[t.StrMapping].ok(merged)

            @staticmethod
            def to_json_value(value: t.ApiJsonValue) -> t.ContainerValue:
                """Validate arbitrary value as ContainerValue using centralized Pydantic contracts."""
                if value is None:
                    return ""
                return t.Api.CONTAINER_VALUE_ADAPTER.validate_python(value)

            @staticmethod
            def to_request_body(value: t.ContainerValue) -> t.Api.RequestBody:
                """Validate arbitrary value as RequestBody using centralized Pydantic contracts."""
                return t.Api.REQUEST_BODY_ADAPTER.validate_python(value)

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
                    if not isinstance(timeout_value, (int, float, str)):
                        return r[float].fail(f"Invalid timeout value: {timeout_value}")
                    try:
                        timeout_float = float(timeout_value)
                        if timeout_float > 0:
                            return r[float].ok(timeout_float)
                        return r[float].fail("Invalid timeout value: must be positive")
                    except (ValueError, TypeError):
                        return r[float].fail(f"Invalid timeout value: {timeout_value}")
                return r[float].ok(30.0)

            @staticmethod
            def extract_query_params(
                request_kwargs: t.Api.RequestKwargs | None,
            ) -> r[t.Api.WebParams]:
                """Extract and normalize query parameters from request kwargs."""
                query_params: t.Api.WebParams = {}
                if request_kwargs is None or "params" not in request_kwargs:
                    return r[t.Api.WebParams].ok(query_params)
                params_value = request_kwargs["params"]
                if params_value is None:
                    return r[t.Api.WebParams].ok(query_params)
                if not isinstance(params_value, Mapping):
                    return r[t.Api.WebParams].fail(
                        f"Invalid params type: {type(params_value)}",
                    )
                params_result: t.MutableStrMapping = {}
                for key, value in params_value.items():
                    if isinstance(value, str):
                        params_result[key] = value
                    elif isinstance(value, (int, float, bool)):
                        params_result[key] = f"{value}"
                    else:
                        params_result[key] = ""
                return r[t.Api.WebParams].ok(params_result)

            @staticmethod
            def build_request_payload(
                *,
                method: str,
                url: str,
                data: t.Api.RequestBody | None = None,
                headers: t.StrMapping | None = None,
                request_kwargs: t.Api.RequestKwargs | None = None,
                timeout: float | str | None = None,
            ) -> r[t.ConfigMap]:
                """Build one normalized request payload for HttpRequest validation."""
                body_result = (
                    FlextApiUtilities.Api.RequestUtils.extract_body_from_kwargs(
                        data,
                        request_kwargs,
                    )
                )
                if body_result.failure:
                    return r[t.ConfigMap].fail(
                        body_result.error or "Body extraction failed",
                    )
                headers_result = FlextApiUtilities.Api.RequestUtils.merge_headers(
                    headers,
                    request_kwargs,
                )
                if headers_result.failure:
                    return r[t.ConfigMap].fail(
                        headers_result.error or "Header extraction failed",
                    )
                timeout_result = (
                    FlextApiUtilities.Api.RequestUtils.validate_and_extract_timeout(
                        timeout,
                        request_kwargs,
                    )
                )
                if timeout_result.failure:
                    return r[t.ConfigMap].fail(
                        timeout_result.error or "Timeout extraction failed",
                    )
                query_params_result = (
                    FlextApiUtilities.Api.RequestUtils.extract_query_params(
                        request_kwargs,
                    )
                )
                if query_params_result.failure:
                    return r[t.ConfigMap].fail(
                        query_params_result.error or "Query params extraction failed",
                    )
                return r[t.ConfigMap].ok(
                    t.ConfigMap(
                        root={
                            "method": method,
                            "url": url,
                            "body": body_result.value,
                            "headers": dict(headers_result.value),
                            "query_params": query_params_result.value,
                            "timeout": timeout_result.value,
                        },
                    ),
                )

    class ResponseBuilder:
        """Response builder for API responses."""

        @staticmethod
        def build_error_response(
            message: str,
            status_code: int = 400,
            error_code: str | None = None,
        ) -> Mapping[str, t.ApiJsonValue]:
            """Build error response - returns plain dict."""
            error_detail: t.MutableContainerValueMapping = {
                "message": message,
                "status_code": status_code,
            }
            if error_code is not None:
                error_detail["code"] = error_code
            result: MutableMapping[str, t.ApiJsonValue] = {
                "success": False,
                "error": error_detail,
            }
            return result

        @staticmethod
        def build_error_result(
            error: str,
            status_code: int = 400,
            data: t.ApiJsonValue | None = None,
            headers: t.StrMapping | None = None,
        ) -> r[Mapping[str, t.ApiJsonValue]]:
            """Build error result - returns r with error response."""
            response: MutableMapping[str, t.ApiJsonValue] = {
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
            headers: t.StrMapping | None = None,
        ) -> r[Mapping[str, t.ApiJsonValue]]:
            """Build success response with optional data and message."""
            response: MutableMapping[str, t.ApiJsonValue] = {
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
            data: t.ContainerValueList,
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
            pagination_info: t.ContainerValueMapping = {
                "page": page,
                "page_size": page_size,
                "total": total_items,
                "total_pages": total_pages,
            }
            response: MutableMapping[str, t.ApiJsonValue] = {
                "success": True,
                "data": data,
                "pagination": pagination_info,
            }
            return r[Mapping[str, t.ApiJsonValue]].ok(response)

        @staticmethod
        def build_pagination_response(
            pagination_data: t.ContainerValueMapping,
        ) -> r[Mapping[str, t.ApiJsonValue]]:
            """Build full pagination response from pagination data dict."""
            if "data" not in pagination_data:
                return r[Mapping[str, t.ApiJsonValue]].fail(
                    "pagination_data must contain 'data' key",
                )
            result: MutableMapping[str, t.ApiJsonValue] = {
                "success": True,
                "pagination": pagination_data,
            }
            return r[Mapping[str, t.ApiJsonValue]].ok(result)

        @staticmethod
        def extract_page_params(
            params: Mapping[str, t.ApiJsonValue],
        ) -> r[t.IntPair]:
            """Extract and validate page and page_size from params dict.

            Returns tuple of (page, page_size).
            Defaults: page=1, page_size=20
            """
            try:
                page_str = params.get("page", "1")
                page_size_str = params.get("page_size", "20")
                if isinstance(page_str, (int, float, str)):
                    page = int(page_str)
                else:
                    return r[t.IntPair].fail("Invalid page parameter")
                if isinstance(page_size_str, (int, float, str)):
                    page_size = int(page_size_str)
                else:
                    return r[t.IntPair].fail("Invalid page_size parameter")
                if page < 1 or page_size < 1:
                    return r[t.IntPair].fail("Page and page_size must be >= 1")
                return r[t.IntPair].ok((page, page_size))
            except (ValueError, TypeError):
                return r[t.IntPair].fail("Invalid page or page_size parameters")

        @staticmethod
        def extract_pagination_config(
            settings: t.ContainerValue,
        ) -> Mapping[str, t.ApiJsonValue]:
            """Extract pagination configuration from settings t.RecursiveContainer.

            Reads attributes: default_page_size, max_page_size.
            Provides defaults if not found.
            """
            result: MutableMapping[str, t.ApiJsonValue] = {}
            default_page_size = getattr(settings, "default_page_size", 20)
            max_page_size = getattr(settings, "max_page_size", 1000)
            result["default_page_size"] = (
                FlextApiUtilities.Api.RequestUtils.to_json_value(default_page_size)
            )
            result["max_page_size"] = FlextApiUtilities.Api.RequestUtils.to_json_value(
                max_page_size,
            )
            return result

        @staticmethod
        def prepare_pagination_data(
            data: t.ContainerValueList,
            total: int,
            page: int,
            page_size: int,
        ) -> r[Mapping[str, t.ApiJsonValue]]:
            """Prepare pagination metadata for response.

            Calculates total_pages, has_next, has_prev, next_page, prev_page.
            """
            if page < 1 or page_size < 1:
                return r[Mapping[str, t.ApiJsonValue]].fail(
                    "Page and page_size must be >= 1",
                )
            total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
            has_next = page < total_pages
            has_prev = page > 1
            next_page: int = page + 1 if has_next else 0
            prev_page: int = page - 1 if has_prev else 0
            result: MutableMapping[str, t.ApiJsonValue] = {
                "data": data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev,
                "next_page": next_page,
                "prev_page": prev_page,
            }
            return r[Mapping[str, t.ApiJsonValue]].ok(result)

        @staticmethod
        def validate_pagination_params(
            page: int,
            page_size: int,
            max_page_size: int = 1000,
        ) -> r[t.IntPair]:
            """Validate pagination parameters.

            Returns tuple of (page, page_size) if valid.
            """
            if page < 1:
                return r[t.IntPair].fail("Page must be >= 1")
            if page_size < 1:
                return r[t.IntPair].fail("Page size must be >= 1")
            if page_size > max_page_size:
                return r[t.IntPair].fail(
                    f"Page size cannot exceed {max_page_size}",
                )
            return r[t.IntPair].ok((page, page_size))

    class FlextWebValidator:
        """Web validation utilities for URLs and HTTP methods."""

        @staticmethod
        def valid_port_number(port: t.ContainerValue) -> TypeIs[int]:
            """Check if port is a valid port number (TypeIs for precise narrowing)."""
            if not isinstance(port, int):
                return False
            return 1 <= port <= FlextApiUtilities.MAX_PORT

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
            if len(host) > FlextApiUtilities.MAX_HOSTNAME_LENGTH:
                return r[str].fail("Hostname too long")
            pattern = "^[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$|^localhost$|^[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+$"
            if not re.match(pattern, host):
                return r[str].fail("Invalid hostname format")
            return r[str].ok(host)

        @staticmethod
        def validate_http_method(method: str) -> bool:
            """Validate HTTP method."""
            return method.upper() in FlextApiUtilities.VALID_HTTP_METHODS

        @staticmethod
        def validate_port_number(port: int) -> r[int]:
            """Validate port number range."""
            if port < 1 or port > FlextApiUtilities.MAX_PORT:
                return r[int].fail(
                    f"Port must be between 1 and {FlextApiUtilities.MAX_PORT}",
                )
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
                    parsed.port < 1 or parsed.port > FlextApiUtilities.MAX_PORT
                ):
                    return r[str].fail(f"Invalid port {parsed.port}")
                return r[str].ok(url)
            except (ValueError, TypeError, KeyError, ConnectionError) as e:
                return r[str].fail(f"Invalid URL: {e}")


__all__: list[str] = ["FlextApiUtilities", "u"]

u = FlextApiUtilities

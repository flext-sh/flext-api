"""FlextApi utilities module."""

from __future__ import annotations

from collections.abc import (
    Mapping,
)
from enum import StrEnum

from flext_api import (
    FlextApiUtilitiesSerializers,
    FlextApiUtilitiesSettingsManager,
    p,
    r,
    t,
)
from flext_core import c
from flext_web import m, u


class FlextApiUtilities(
    u,
    FlextApiUtilitiesSerializers,
    FlextApiUtilitiesSettingsManager,
):
    """FlextApi utilities extending FlextUtilities with API-specific helpers.

    Architecture: Advanced utilities with ZERO code bloat through:
    - TypeIs/TypeGuard for narrowing (PEP 742)
    - m.BeforeValidator factories for Pydantic coercion
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
            ) -> m.BeforeValidator:
                """Create a m.BeforeValidator for automatic enum coercion.

                Usage in Pydantic models:
                    field: Annotated[MyEnum, u.Api.Pydantic.coerced_enum_validator(MyEnum)]
                """

                def _coerce(v: str | StrEnum) -> StrEnum:
                    result = u.parse(v, enum_cls)
                    if result.failure:
                        msg = result.error or f"Invalid {enum_cls.__name__}: {v!r}"
                        raise ValueError(msg)
                    return enum_cls(v) if not isinstance(v, enum_cls) else v

                return m.BeforeValidator(_coerce)

        class RequestUtils:
            """Request utilities for extracting and validating HTTP request components."""

            @staticmethod
            def coerce_positive_timeout(
                timeout_value: float | str,
            ) -> p.Result[float]:
                """Coerce timeout to a positive float."""
                try:
                    timeout_float = float(timeout_value)
                except c.EXC_TYPE_VALIDATION:
                    return r[float].fail(f"Invalid timeout value: {timeout_value}")
                if timeout_float <= 0:
                    return r[float].fail("Invalid timeout value: must be positive")
                return r[float].ok(timeout_float)

            @staticmethod
            def extract_body_from_kwargs(
                data: t.Api.RequestBody | None,
                kwargs: t.Api.RequestKwargs | None,
            ) -> p.Result[t.Api.RequestBody]:
                """Extract body from data or kwargs - returns empty dict if no body found."""
                if data is not None:
                    return r[t.Api.RequestBody].ok(data)
                if kwargs is not None and "data" in kwargs:
                    raw_data = kwargs["data"]
                    if raw_data is not None:
                        return r[t.Api.RequestBody].ok(
                            t.Api.REQUEST_BODY_ADAPTER.validate_python(raw_data),
                        )
                if kwargs is not None and "json" in kwargs:
                    raw_json = kwargs["json"]
                    if raw_json is not None:
                        return r[t.Api.RequestBody].ok(
                            t.Api.REQUEST_BODY_ADAPTER.validate_python(raw_json),
                        )
                return r[t.Api.RequestBody].ok({})

            @staticmethod
            def merge_headers(
                headers: t.StrMapping | None,
                kwargs: t.Api.RequestKwargs | None,
            ) -> p.Result[t.StrMapping]:
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
            def to_json_value(
                value: (
                    t.JsonValue | t.StrMapping | t.ScalarMapping | t.Api.WebHeaders
                ),
            ) -> t.JsonValue:
                """Validate arbitrary value as JsonValue using centralized Pydantic contracts."""
                if value is None:
                    return None
                return t.Api.API_JSON_VALUE_ADAPTER.validate_python(value)

            @staticmethod
            def validate_and_extract_timeout(
                timeout: float | str | None,
                kwargs: t.Api.RequestKwargs | None,
            ) -> p.Result[float]:
                """Validate and extract timeout from timeout value or kwargs.

                Returns default timeout of c.DEFAULT_TIMEOUT_SECONDS if not specified.
                Coerces string/int values to float.
                Fails if timeout is explicitly provided but invalid.
                """
                if timeout is not None:
                    return FlextApiUtilities.Api.RequestUtils.coerce_positive_timeout(
                        timeout,
                    )
                if kwargs and "timeout" in kwargs:
                    timeout_value = kwargs["timeout"]
                    if not isinstance(timeout_value, (int, float, str)):
                        return r[float].fail(f"Invalid timeout value: {timeout_value}")
                    return FlextApiUtilities.Api.RequestUtils.coerce_positive_timeout(
                        timeout_value,
                    )
                return r[float].ok(float(c.DEFAULT_TIMEOUT_SECONDS))

            @staticmethod
            def extract_query_params(
                request_kwargs: t.Api.RequestKwargs | None,
            ) -> p.Result[t.Api.WebParams]:
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
            ) -> p.Result[m.ConfigMap]:
                """Build one normalized request payload for HttpRequest validation."""
                body_result = (
                    FlextApiUtilities.Api.RequestUtils.extract_body_from_kwargs(
                        data,
                        request_kwargs,
                    )
                )
                if body_result.failure:
                    return r[m.ConfigMap].fail(
                        body_result.error or "Body extraction failed",
                    )
                headers_result = FlextApiUtilities.Api.RequestUtils.merge_headers(
                    headers,
                    request_kwargs,
                )
                if headers_result.failure:
                    return r[m.ConfigMap].fail(
                        headers_result.error or "Header extraction failed",
                    )
                timeout_result = (
                    FlextApiUtilities.Api.RequestUtils.validate_and_extract_timeout(
                        timeout,
                        request_kwargs,
                    )
                )
                if timeout_result.failure:
                    return r[m.ConfigMap].fail(
                        timeout_result.error or "Timeout extraction failed",
                    )
                query_params_result = (
                    FlextApiUtilities.Api.RequestUtils.extract_query_params(
                        request_kwargs,
                    )
                )
                if query_params_result.failure:
                    return r[m.ConfigMap].fail(
                        query_params_result.error or "Query params extraction failed",
                    )
                return r[m.ConfigMap].ok(
                    m.ConfigMap(
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


__all__: list[str] = ["FlextApiUtilities", "u"]

u = FlextApiUtilities

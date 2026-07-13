"""API request utility shard."""

from __future__ import annotations

from collections.abc import Mapping

from flext_api import c, p, t
from flext_core.result import r
from flext_web import m


class FlextApiUtilitiesRequestUtils:
    """Request utility namespace shard for ``u.Api``."""

    class RequestUtils:
        """Request utilities for HTTP request components."""

        @staticmethod
        def coerce_positive_timeout(timeout_value: float | str) -> p.Result[float]:
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
            """Extract body from data or kwargs."""
            if data is not None:
                return r[t.Api.RequestBody].ok(data)
            if kwargs is not None and "data" in kwargs and kwargs["data"] is not None:
                return r[t.Api.RequestBody].ok(
                    t.Api.REQUEST_BODY_ADAPTER.validate_python(kwargs["data"]),
                )
            if kwargs is not None and "json" in kwargs and kwargs["json"] is not None:
                return r[t.Api.RequestBody].ok(
                    t.Api.REQUEST_BODY_ADAPTER.validate_python(kwargs["json"]),
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
                    validated = t.Api.STR_MAPPING_ADAPTER.validate_python(
                        headers_value,
                    )
                    merged.update(validated)
            return r[t.StrMapping].ok(merged)

        @staticmethod
        def to_json_value(
            value: t.JsonValue | t.StrMapping | t.ScalarMapping | t.Api.WebHeaders,
        ) -> t.JsonValue:
            """Validate arbitrary value as JsonValue."""
            if value is None:
                return None
            return t.Api.API_JSON_VALUE_ADAPTER.validate_python(value)

        @staticmethod
        def validate_and_extract_timeout(
            timeout: float | str | None,
            kwargs: t.Api.RequestKwargs | None,
        ) -> p.Result[float]:
            """Validate and extract timeout from timeout value or kwargs."""
            request_utils = FlextApiUtilitiesRequestUtils.RequestUtils
            if timeout is not None:
                return request_utils.coerce_positive_timeout(timeout)
            if kwargs and "timeout" in kwargs:
                timeout_value = kwargs["timeout"]
                if not isinstance(timeout_value, (int, float, str)):
                    return r[float].fail(f"Invalid timeout value: {timeout_value}")
                return request_utils.coerce_positive_timeout(timeout_value)
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
            normalized: t.MutableStrMapping = {}
            for key, value in params_value.items():
                if isinstance(value, str):
                    normalized[key] = value
                elif isinstance(value, (int, float, bool)):
                    normalized[key] = f"{value}"
                else:
                    normalized[key] = ""
            return r[t.Api.WebParams].ok(normalized)

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
            request_utils = FlextApiUtilitiesRequestUtils.RequestUtils
            body_result = request_utils.extract_body_from_kwargs(data, request_kwargs)
            if body_result.failure:
                return r[m.ConfigMap].fail(
                    body_result.error or "Body extraction failed",
                )
            headers_result = request_utils.merge_headers(headers, request_kwargs)
            if headers_result.failure:
                return r[m.ConfigMap].fail(
                    headers_result.error or "Header extraction failed",
                )
            timeout_result = request_utils.validate_and_extract_timeout(
                timeout,
                request_kwargs,
            )
            if timeout_result.failure:
                return r[m.ConfigMap].fail(
                    timeout_result.error or "Timeout extraction failed",
                )
            query_result = request_utils.extract_query_params(request_kwargs)
            if query_result.failure:
                return r[m.ConfigMap].fail(
                    query_result.error or "Query params extraction failed",
                )
            return r[m.ConfigMap].ok(
                m.ConfigMap(
                    root={
                        "method": method,
                        "url": url,
                        "body": body_result.value,
                        "headers": dict(headers_result.value),
                        "query_params": query_result.value,
                        "timeout": timeout_result.value,
                    },
                ),
            )


__all__: t.MutableSequenceOf[str] = ["FlextApiUtilitiesRequestUtils"]

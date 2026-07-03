"""HTTP client serialization helpers."""

from __future__ import annotations

import httpx

from flext_api import c, p, t
from flext_core.result import r
from flext_web import u


class FlextApiClientCodecMixin:
    """Serialize requests and deserialize responses for FlextApiClient."""

    @staticmethod
    def _deserialize_body(response: httpx.Response) -> p.Result[t.Api.ResponseBody]:
        """Deserialize response body based on content-type."""
        content_type = response.headers.get("content-type", "").lower()
        if any(
            token in content_type for token in ("application/octet-stream", "binary")
        ):
            return FlextApiClientCodecMixin._deserialize_bytes(response)
        if any(
            token in content_type for token in ("application/json", "application/vnd")
        ):
            return FlextApiClientCodecMixin._deserialize_json(response)
        if "text/" in content_type:
            return FlextApiClientCodecMixin._deserialize_text(response)
        for strategy in (
            FlextApiClientCodecMixin._deserialize_json,
            FlextApiClientCodecMixin._deserialize_text,
            FlextApiClientCodecMixin._deserialize_bytes,
        ):
            result = strategy(response)
            if result.success:
                return result
        return r[t.Api.ResponseBody].fail(
            "Failed to deserialize response body: no valid format found",
        )

    @staticmethod
    def _deserialize_bytes(response: httpx.Response) -> p.Result[t.Api.ResponseBody]:
        """Deserialize response as bytes."""
        return r[t.Api.ResponseBody].ok(response.content)

    @staticmethod
    def _deserialize_json(response: httpx.Response) -> p.Result[t.Api.ResponseBody]:
        """Deserialize response as JSON."""
        try:
            json_data = response.json()
            validated: p.Result[t.Api.ResponseBody] = u.validate_value(
                t.Api.RESPONSE_BODY_ADAPTER,
                json_data,
            )
            return validated
        except (
            AttributeError,
            ValueError,
            TypeError,
            KeyError,
            httpx.HTTPError,
            ConnectionError,
            c.ValidationError,
        ) as exc:
            return r[t.Api.ResponseBody].fail_op("JSON deserialization", exc)

    @staticmethod
    def _deserialize_text(response: httpx.Response) -> p.Result[t.Api.ResponseBody]:
        """Deserialize response as text."""
        return r[t.Api.ResponseBody].ok(response.text)

    @staticmethod
    def _serialize_body(body: t.Api.RequestBody | None) -> p.Result[bytes]:
        """Serialize request body to bytes."""
        result: p.Result[bytes]
        if body is None or (isinstance(body, dict) and not body):
            result = r[bytes].ok(b"")
        elif isinstance(body, bytes):
            result = r[bytes].ok(body)
        elif isinstance(body, str):
            result = r[bytes].ok(body.encode(c.DEFAULT_ENCODING))
        elif isinstance(body, dict):
            try:
                result = r[bytes].ok(t.Api.DICT_BODY_ADAPTER.dump_json(body))
            except c.EXC_TYPE_VALIDATION as exc:
                result = r[bytes].fail(f"Failed to serialize body: {exc}")
        else:
            result = r[bytes].fail("Request body must be bytes, str, or JSON object")
        return result


__all__: list[str] = ["FlextApiClientCodecMixin"]

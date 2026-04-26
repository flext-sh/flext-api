"""Generic HTTP Client - Domain-agnostic HTTP operations.

Pure HTTP client wrapper with FLEXT patterns. Single responsibility:
Execute HTTP requests and return r. All retry, timeout, and
configuration handled via FlextApiSettings model passed at construction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar, override

import httpx

from flext_api import (
    FlextApiSettings,
    c,
    m,
    p,
    r,
    t,
)
from flext_core import FlextSettings, s
from flext_web import u


class FlextApiClient(s[bool]):
    """Generic HTTP client using FLEXT patterns.

    Single responsibility: Execute HTTP requests with r error handling.
    All configuration through FlextApiSettings model (Pydantic v2).
    Domain-agnostic - works with any HTTP endpoint.

    Uses httpx for HTTP operations, delegates to models for data validation.
    """

    config_type: ClassVar[type[FlextApiSettings]] = FlextApiSettings

    def __init__(
        self,
        *,
        settings: FlextApiSettings | None = None,
    ) -> None:
        """Public bootstrap surface using the canonical ``settings=`` call form."""
        super().__init__(runtime_settings=settings)

    @property
    @override
    def settings(self) -> FlextApiSettings:
        """Return the typed API settings namespace."""
        settings = super().settings
        if isinstance(settings, FlextApiSettings):
            return settings
        return FlextSettings.fetch_global().fetch_namespace("api", FlextApiSettings)

    @property
    def base_url(self) -> str:
        """Access base_url from configuration."""
        return str(self.settings.base_url)

    @property
    def timeout(self) -> float:
        """Access timeout from configuration."""
        return float(self.settings.timeout)

    @staticmethod
    def _deserialize_body(
        response: httpx.Response,
    ) -> p.Result[t.Api.ResponseBody]:
        """Deserialize response body based on content-type."""
        content_type = response.headers.get("content-type", "").lower()
        if "application/octet-stream" in content_type or "binary" in content_type:
            bytes_result = FlextApiClient._deserialize_bytes(response)
            if bytes_result.success:
                return bytes_result
        if "application/json" in content_type or "application/vnd" in content_type:
            json_result = FlextApiClient._deserialize_json(response)
            if json_result.success:
                return json_result
        json_result = FlextApiClient._deserialize_json(response)
        if json_result.success:
            return json_result
        if "text/" in content_type:
            text_result = FlextApiClient._deserialize_text(response)
            if text_result.success:
                return text_result
        text_result = FlextApiClient._deserialize_text(response)
        if text_result.success:
            return text_result
        bytes_result = FlextApiClient._deserialize_bytes(response)
        if bytes_result.success:
            return bytes_result
        return r[t.Api.ResponseBody].fail(
            "Failed to deserialize response body: no valid format found",
        )

    @staticmethod
    def _deserialize_bytes(
        response: httpx.Response,
    ) -> p.Result[t.Api.ResponseBody]:
        """Deserialize response as bytes."""
        return r[t.Api.ResponseBody].ok(response.content)

    @staticmethod
    def _deserialize_json(
        response: httpx.Response,
    ) -> p.Result[t.Api.ResponseBody]:
        """Deserialize response as JSON."""
        try:
            json_data = response.json()
            return u.validate_value(t.Api.RESPONSE_BODY_ADAPTER, json_data)
        except (
            AttributeError,
            ValueError,
            TypeError,
            KeyError,
            httpx.HTTPError,
            ConnectionError,
            c.ValidationError,
        ) as e:
            return r[t.Api.ResponseBody].fail(
                f"JSON deserialization failed: {e}",
            )

    @staticmethod
    def _deserialize_text(
        response: httpx.Response,
    ) -> p.Result[t.Api.ResponseBody]:
        """Deserialize response as text."""
        return r[t.Api.ResponseBody].ok(response.text)

    @staticmethod
    def _serialize_body(
        body: t.Api.RequestBody | None,
    ) -> p.Result[bytes]:
        """Serialize request body to bytes - None and empty dict map to empty bytes."""
        result: p.Result[bytes]
        is_empty_mapping = isinstance(body, dict) and not body
        if body is None or is_empty_mapping:
            result = r[bytes].ok(b"")
        elif isinstance(body, bytes):
            result = r[bytes].ok(body)
        elif isinstance(body, str):
            result = r[bytes].ok(body.encode(c.DEFAULT_ENCODING))
        elif isinstance(body, dict):
            try:
                result = r[bytes].ok(t.Api.DICT_BODY_ADAPTER.dump_json(body))
            except (TypeError, ValueError) as e:
                result = r[bytes].fail(f"Failed to serialize body: {e}")
        else:
            result = r[bytes].fail(
                "Request body must be bytes, str, or JSON object",
            )
        return result

    def execute(
        self,
        **kwargs: t.Scalar,
    ) -> p.Result[FlextApiSettings]:
        """Execute s interface - return configuration."""
        if kwargs:
            self.logger.info(f"Execute called with kwargs keys: {list(kwargs.keys())}")
        return r[FlextApiSettings].ok(self.settings)

    def request(
        self,
        request: m.Api.HttpRequest,
    ) -> p.Result[m.Api.HttpResponse]:
        """Execute HTTP request from model using monadic patterns.

        Args:
        request: HttpRequest Value Object with method, url, headers, body.

        Returns:
        r[HttpResponse]: Success with HttpResponse or error message.

        """
        url_result = self._build_url(request.url)
        if url_result.failure:
            return r[m.Api.HttpResponse].fail(
                url_result.error or "URL validation failed"
            )
        request_body: t.Api.RequestBody = (
            request.body if request.body is not None else b""
        )
        body_result = self._serialize_body(request_body)
        if body_result.failure:
            return r[m.Api.HttpResponse].fail(
                body_result.error or "Body serialization failed",
            )
        return self._execute_http_request(
            request=request,
            url=url_result.value,
            serialized_body=body_result.value,
        )

    def _build_url(self, path: str) -> p.Result[str]:
        """Build full URL from base_url and path."""
        if not path:
            return r[str].fail("URL path cannot be empty")
        path_stripped = path.strip()
        if not path_stripped:
            return r[str].fail("URL path cannot be empty")
        if not self.settings.base_url.strip():
            return r[str].ok(path_stripped)
        base = self.settings.base_url.strip().rstrip("/")
        if path_stripped.startswith("/"):
            return r[str].ok(f"{base}{path_stripped}")
        return r[str].ok(f"{base}/{path_stripped}")

    def _execute_http_request(
        self,
        request: m.Api.HttpRequest,
        url: str,
        serialized_body: bytes,
    ) -> p.Result[m.Api.HttpResponse]:
        """Execute HTTP request using httpx client."""
        try:
            headers: t.StrMapping = {
                **self.settings.default_headers,
                **request.headers,
            }
            with httpx.Client(timeout=request.timeout) as client:
                request_method: str = request.method
                request_url: str = url
                request_headers: t.StrMapping = headers
                request_params: t.Api.WebParams = request.query_params or {}
                response = client.request(
                    method=request_method,
                    url=request_url,
                    headers=request_headers,
                    params=request_params,
                    content=serialized_body or None,
                )
            if response.status_code >= c.Api.HTTP_ERROR_MIN:
                return r[m.Api.HttpResponse].fail(
                    f"HTTP {response.status_code}: {response.reason_phrase}",
                )
            return self._deserialize_body(response).flat_map(
                lambda body: u.try_(
                    lambda: m.Api.HttpResponse.model_validate({
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "body": body,
                        "request_id": "",
                    }),
                    catch=(c.ValidationError, ValueError, TypeError),
                ).map_error(lambda e: f"Response model validation failed: {e}"),
            )
        except (
            ValueError,
            TypeError,
            KeyError,
            httpx.HTTPError,
            ConnectionError,
        ) as exc:
            return r[m.Api.HttpResponse].fail(
                f"HTTP client request failed: {exc}",
            )


__all__: t.MutableSequenceOf[str] = ["FlextApiClient"]

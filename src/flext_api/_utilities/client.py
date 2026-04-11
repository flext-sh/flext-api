"""Generic HTTP Client - Domain-agnostic HTTP operations.

Pure HTTP client wrapper with FLEXT patterns. Single responsibility:
Execute HTTP requests and return r. All retry, timeout, and
configuration handled via FlextApiSettings model passed at construction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Self, override

import httpx
from pydantic import ValidationError

from flext_api import FlextApiSettings, c, m, t
from flext_core import r, s


class FlextApiClient(s[FlextApiSettings]):
    """Generic HTTP client using FLEXT patterns.

    Single responsibility: Execute HTTP requests with r error handling.
    All configuration through FlextApiSettings model (Pydantic v2).
    Domain-agnostic - works with any HTTP endpoint.

    Uses httpx for HTTP operations, delegates to models for data validation.
    """

    def __new__(
        cls,
        config: FlextApiSettings | None = None,
        **_kwargs: t.Scalar,
    ) -> Self:
        """Intercept positional config argument and convert to kwargs.

        Args:
            config: Optional FlextApiSettings (passed to __init__ via attribute).

        """
        instance = super().__new__(cls)
        if config is not None:
            object.__setattr__(instance, "_init_config", config)
        return instance

    def __init__(
        self,
        config: FlextApiSettings | None = None,
        **kwargs: t.Scalar,
    ) -> None:
        """Initialize with optional configuration model.

        Args:
        config: Optional FlextApiSettings model with base_url, timeout, headers, etc.
                If None, uses default configuration.
        **kwargs: Additional Pydantic model fields (ignored for this service).

        """
        _ = kwargs
        super().__init__()
        init_config = getattr(self, "_init_config", None)
        if init_config is not None:
            api_config = init_config
        elif config is not None:
            api_config = config
        else:
            api_config = FlextApiSettings.model_validate({})
        object.__setattr__(self, "_config", api_config)

    @property
    def base_url(self) -> str:
        """Access base_url from configuration."""
        return self._get_config().base_url

    @property
    def timeout(self) -> float:
        """Access timeout from configuration."""
        return self._get_config().timeout

    @staticmethod
    def _deserialize_body(response: httpx.Response) -> r[t.Api.ResponseBody]:
        """Deserialize response body based on content-type."""
        content_type = response.headers.get("content-type", "").lower()
        if "application/octet-stream" in content_type or "binary" in content_type:
            bytes_result = FlextApiClient._deserialize_bytes(response)
            if bytes_result.success:
                return bytes_result.map(lambda v: v)
        if "application/json" in content_type or "application/vnd" in content_type:
            json_result = FlextApiClient._deserialize_json(response)
            if json_result.success:
                return json_result.map(lambda v: v)
        json_result = FlextApiClient._deserialize_json(response)
        if json_result.success:
            return json_result.map(lambda v: v)
        if "text/" in content_type:
            text_result = FlextApiClient._deserialize_text(response)
            if text_result.success:
                return text_result.map(lambda v: v)
        text_result = FlextApiClient._deserialize_text(response)
        if text_result.success:
            return text_result.map(lambda v: v)
        bytes_result = FlextApiClient._deserialize_bytes(response)
        if bytes_result.success:
            return bytes_result.map(lambda v: v)
        return r[t.Api.ResponseBody].fail(
            "Failed to deserialize response body: no valid format found",
        )

    @staticmethod
    def _deserialize_bytes(response: httpx.Response) -> r[t.Api.ResponseBody]:
        """Deserialize response as bytes."""
        return r[t.Api.ResponseBody].ok(response.content)

    @staticmethod
    def _deserialize_json(response: httpx.Response) -> r[t.Api.ResponseBody]:
        """Deserialize response as JSON."""
        try:
            json_data = response.json()
            validated = t.Api.RESPONSE_BODY_ADAPTER.validate_python(json_data)
            return r[t.Api.ResponseBody].ok(validated)
        except (
            AttributeError,
            ValueError,
            TypeError,
            KeyError,
            httpx.HTTPError,
            ConnectionError,
            ValidationError,
        ) as e:
            return r[t.Api.ResponseBody].fail(f"JSON deserialization failed: {e}")

    @staticmethod
    def _deserialize_text(response: httpx.Response) -> r[t.Api.ResponseBody]:
        """Deserialize response as text."""
        return r[t.Api.ResponseBody].ok(response.text)

    @staticmethod
    def _serialize_body(body: t.Api.RequestBody) -> r[bytes]:
        """Serialize request body to bytes - no None, empty dict is valid."""
        if isinstance(body, dict) and not body:
            return r[bytes].ok(b"")
        if isinstance(body, bytes):
            return r[bytes].ok(body)
        if isinstance(body, dict):
            try:
                serialized = t.Api.DICT_BODY_ADAPTER.dump_json(body)
                return r[bytes].ok(serialized)
            except (TypeError, ValueError) as e:
                return r[bytes].fail(f"Failed to serialize body: {e}")
        if isinstance(body, str):
            return r[bytes].ok(body.encode("utf-8"))
        return r[bytes].fail("Request body must be bytes, str, or JSON object")

    @override
    def execute(self, **kwargs: t.Scalar) -> r[FlextApiSettings]:
        """Execute s interface - return configuration."""
        if kwargs:
            self.logger.info(f"Execute called with kwargs keys: {list(kwargs.keys())}")
        return r[FlextApiSettings].ok(self._get_config())

    def request(self, request: m.Api.HttpRequest) -> r[m.Api.HttpResponse]:
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
        body_result = self._serialize_body(request.body)
        if body_result.failure:
            return r[m.Api.HttpResponse].fail(
                body_result.error or "Body serialization failed",
            )
        return self._execute_http_request(
            request=request,
            url=url_result.value,
            serialized_body=body_result.value,
        )

    def _build_url(self, path: str) -> r[str]:
        """Build full URL from base_url and path."""
        if not path:
            return r[str].fail("URL path cannot be empty")
        path_stripped = path.strip()
        if not path_stripped:
            return r[str].fail("URL path cannot be empty")
        api_config = self._get_config()
        if not api_config.base_url.strip():
            return r[str].ok(path_stripped)
        base = api_config.base_url.strip().rstrip("/")
        if path_stripped.startswith("/"):
            return r[str].ok(f"{base}{path_stripped}")
        return r[str].ok(f"{base}/{path_stripped}")

    def _execute_http_request(
        self,
        request: m.Api.HttpRequest,
        url: str,
        serialized_body: bytes,
    ) -> r[m.Api.HttpResponse]:
        """Execute HTTP request using httpx client."""
        try:
            api_config = self._get_config()
            headers: t.StrMapping = {
                **api_config.default_headers,
                **request.headers,
            }
            with httpx.Client(timeout=request.timeout) as client:
                request_method: str = request.method
                request_url: str = url
                request_headers: t.StrMapping = headers
                request_params: t.Api.WebParams = request.query_params
                if serialized_body:
                    response = client.request(
                        method=request_method,
                        url=request_url,
                        headers=request_headers,
                        params=request_params,
                        content=serialized_body,
                    )
                else:
                    response = client.request(
                        method=request_method,
                        url=request_url,
                        headers=request_headers,
                        params=request_params,
                    )
            if response.status_code >= c.Api.HTTP_ERROR_MIN:
                return r[m.Api.HttpResponse].fail(
                    f"HTTP {response.status_code}: {response.reason_phrase}",
                )
            return self._deserialize_body(response).map(
                lambda body: m.Api.HttpResponse(
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    body=body,
                    request_id="",
                ),
            )
        except (
            ValueError,
            TypeError,
            KeyError,
            httpx.HTTPError,
            ConnectionError,
        ) as exc:
            return r[m.Api.HttpResponse].fail(f"HTTP client request failed: {exc}")

    def _get_config(self) -> FlextApiSettings:
        """Get FlextApiSettings with proper type narrowing."""
        config = self._config
        if isinstance(config, FlextApiSettings):
            return config
        return FlextApiSettings.model_validate({})


__all__ = ["FlextApiClient"]

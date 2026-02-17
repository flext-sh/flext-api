"""Generic HTTP Client - Domain-agnostic HTTP operations.

Pure HTTP client wrapper with FLEXT patterns. Single responsibility:
Execute HTTP requests and return FlextResult. All retry, timeout, and
configuration handled via FlextApiSettings model passed at construction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
from typing import Self

import httpx
from flext_core import FlextRuntime, r, s

from flext_api.constants import FlextApiConstants
from flext_api.models import FlextApiModels
from flext_api.settings import FlextApiSettings
from flext_api.typings import t

# HTTP status codes


class FlextApiClient(s[FlextApiSettings]):
    """Generic HTTP client using FLEXT patterns.

    Single responsibility: Execute HTTP requests with FlextResult error handling.
    All configuration through FlextApiSettings model (Pydantic v2).
    Domain-agnostic - works with any HTTP endpoint.

    Uses httpx for HTTP operations, delegates to models for data validation.
    """

    def __new__(cls, config: FlextApiSettings | None = None) -> Self:
        """Intercept positional config argument and convert to kwargs.

        Args:
            config: Optional FlextApiSettings (passed to __init__ via attribute).

        """
        instance = super().__new__(cls)
        if config is not None:
            # Type-safe attribute assignment for __new__ pattern
            # Use object.__setattr__ to bypass type checker for dynamic attribute
            object.__setattr__(instance, "_init_config", config)
        return instance

    def __init__(
        self,
        config: FlextApiSettings | None = None,
        **kwargs: t.JsonValue | str | int | bool,
    ) -> None:
        """Initialize with optional configuration model.

        Args:
        config: Optional FlextApiSettings model with base_url, timeout, headers, etc.
                If None, uses default configuration.
        **kwargs: Additional Pydantic model fields (ignored for this service).

        """
        # Type narrowing: convert kwargs to expected type
        kwargs_typed: dict[str, t.GeneralValueType] = {
            k: FlextRuntime.normalize_to_general_value(v) for k, v in kwargs.items()
        }
        super().__init__(**kwargs_typed)

        # Determine which config to use - follow FlextService pattern with _config
        init_config = getattr(self, "_init_config", None)
        if init_config is not None:
            api_config = init_config
        elif config is not None:
            api_config = config
        else:
            api_config = FlextApiSettings()

        # Set _config to FlextApiSettings (standard FlextService pattern)
        object.__setattr__(self, "_config", api_config)

    def _get_config(self) -> FlextApiSettings:
        """Get FlextApiSettings with proper type narrowing."""
        return (
            self._config
            if isinstance(self._config, FlextApiSettings)
            else FlextApiSettings()
        )

    def execute(
        self,
        **kwargs: t.JsonValue | str | int | bool,
    ) -> r[FlextApiSettings]:
        """Execute FlextService interface - return configuration."""
        if kwargs:
            self.logger.info("Execute called with kwargs: %s", kwargs)
        return r[FlextApiSettings].ok(self._get_config())

    @property
    def base_url(self) -> str:
        """Access base_url from configuration."""
        return self._get_config().base_url

    @property
    def timeout(self) -> float:
        """Access timeout from configuration."""
        return self._get_config().timeout

    def request(
        self,
        request: FlextApiModels.HttpRequest,
    ) -> r[FlextApiModels.HttpResponse]:
        """Execute HTTP request from model using monadic patterns.

        Args:
        request: HttpRequest Value Object with method, url, headers, body.

        Returns:
        r[HttpResponse]: Success with HttpResponse or error message.

        """
        # Build URL and serialize body using monadic patterns
        url_result = self._build_url(request.url)
        if url_result.is_failure:
            return r[FlextApiModels.HttpResponse].fail(
                url_result.error or "URL validation failed",
            )

        body_result = self._serialize_body(request.body)
        if body_result.is_failure:
            return r[FlextApiModels.HttpResponse].fail(
                body_result.error or "Body serialization failed",
            )

        # Execute request with validated URL and body
        return self._execute_http_request(
            request=request,
            url=url_result.value,
            serialized_body=body_result.value,
        )

    def _execute_http_request(
        self,
        request: FlextApiModels.HttpRequest,
        url: str,
        serialized_body: bytes,
    ) -> r[FlextApiModels.HttpResponse]:
        """Execute HTTP request using httpx client."""
        try:
            api_config = self._get_config()
            headers: dict[str, str] = {
                **api_config.default_headers,
                **request.headers,
            }

            with httpx.Client(timeout=request.timeout) as client:
                # Build request with correct types for httpx
                request_method: str = request.method
                request_url: str = url
                request_headers: dict[str, str] = headers
                request_params: dict[str, str | list[str]] = request.query_params

                # Call httpx with explicit typed parameters
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

            if response.status_code >= FlextApiConstants.Api.HTTP_ERROR_MIN:
                return r[FlextApiModels.HttpResponse].fail(
                    f"HTTP {response.status_code}: {response.reason_phrase}",
                )

            return self._deserialize_body(response).map(
                lambda body: FlextApiModels.HttpResponse(
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    body=body,
                ),
            )
        except Exception as exc:
            return r[FlextApiModels.HttpResponse].fail(str(exc))

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

    @staticmethod
    def _serialize_body(
        body: t.Api.RequestBody,
    ) -> r[bytes]:
        """Serialize request body to bytes - no None, empty dict is valid."""
        # Empty dict serializes to empty bytes
        if isinstance(body, dict) and len(body) == 0:
            return r[bytes].ok(b"")
        if isinstance(body, bytes):
            return r[bytes].ok(body)
        if isinstance(body, str):
            return r[bytes].ok(body.encode("utf-8"))
        if isinstance(body, dict):
            try:
                serialized = json.dumps(body).encode("utf-8")
                return r[bytes].ok(serialized)
            except (TypeError, ValueError) as e:
                return r[bytes].fail(f"Failed to serialize body: {e}")
        return r[bytes].fail(f"Invalid body type: {type(body)}")

    @staticmethod
    def _deserialize_body(
        response: httpx.Response,
    ) -> r[t.Api.ResponseBody]:
        """Deserialize response body based on content-type."""
        # Check content-type to prioritize deserialization
        content_type = response.headers.get("content-type", "").lower()

        # For binary content types, prioritize bytes
        if "application/octet-stream" in content_type or "binary" in content_type:
            bytes_result = FlextApiClient._deserialize_bytes(response)
            if bytes_result.is_success:
                return bytes_result.map(lambda v: v)

        # Try JSON first for JSON content types
        if "application/json" in content_type or "application/vnd" in content_type:
            json_result = FlextApiClient._deserialize_json(response)
            if json_result.is_success:
                return json_result.map(lambda v: v)

        # Try JSON for any content (may succeed)
        json_result = FlextApiClient._deserialize_json(response)
        if json_result.is_success:
            return json_result.map(lambda v: v)

        # Try text for text content types
        if "text/" in content_type:
            text_result = FlextApiClient._deserialize_text(response)
            if text_result.is_success:
                return text_result.map(lambda v: v)

        # Try text as fallback
        text_result = FlextApiClient._deserialize_text(response)
        if text_result.is_success:
            return text_result.map(lambda v: v)

        # Try bytes as last resort
        bytes_result = FlextApiClient._deserialize_bytes(response)
        if bytes_result.is_success:
            return bytes_result.map(lambda v: v)

        return r[t.Api.ResponseBody].fail(
            "Failed to deserialize response body: no valid format found",
        )

    @staticmethod
    def _deserialize_json(
        response: httpx.Response,
    ) -> r[t.Api.ResponseBody]:
        """Deserialize response as JSON."""
        try:
            json_data = response.model_dump_json()
            # ResponseBody = JsonObject | str | bytes
            if isinstance(json_data, dict):
                return r[t.Api.ResponseBody].ok(json_data)
            if isinstance(json_data, str):
                return r[t.Api.ResponseBody].ok(json_data)
            if isinstance(json_data, bytes):
                return r[t.Api.ResponseBody].ok(json_data)
            # Convert other types to dict (JsonObject)
            return r[t.Api.ResponseBody].ok({"value": json_data})
        except (AttributeError, ValueError, TypeError, Exception) as e:
            return r[t.Api.ResponseBody].fail(
                f"JSON deserialization failed: {e}",
            )

    @staticmethod
    def _deserialize_text(
        response: httpx.Response,
    ) -> r[t.Api.ResponseBody]:
        """Deserialize response as text."""
        if not hasattr(response, "text"):
            return r[t.Api.ResponseBody].fail(
                "Response does not have text attribute",
            )
        if not isinstance(response.text, str):
            return r[t.Api.ResponseBody].fail(
                f"Response text is not a string: {type(response.text)}",
            )
        return r[t.Api.ResponseBody].ok(response.text)

    @staticmethod
    def _deserialize_bytes(
        response: httpx.Response,
    ) -> r[t.Api.ResponseBody]:
        """Deserialize response as bytes."""
        if not hasattr(response, "content"):
            return r[t.Api.ResponseBody].fail(
                "Response does not have content attribute",
            )
        if not isinstance(response.content, bytes):
            return r[t.Api.ResponseBody].fail(
                f"Response content is not bytes: {type(response.content)}",
            )
        return r[t.Api.ResponseBody].ok(response.content)


__all__ = ["FlextApiClient"]

"""Generic HTTP Client - Domain-agnostic HTTP operations.

Pure HTTP client wrapper with FLEXT patterns. Single responsibility:
Execute HTTP requests and return FlextResult. All retry, timeout, and
configuration handled via FlextApiConfig model passed at construction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
from typing import Self

import httpx
from flext_core import FlextResult, FlextService

from flext_api.config import FlextApiConfig
from flext_api.models import FlextApiModels
from flext_api.typings import FlextApiTypes


class FlextApiClient(FlextService[FlextApiConfig]):
    """Generic HTTP client using FLEXT patterns.

    Single responsibility: Execute HTTP requests with FlextResult error handling.
    All configuration through FlextApiConfig model (Pydantic v2).
    Domain-agnostic - works with any HTTP endpoint.

    Uses httpx for HTTP operations, delegates to models for data validation.
    """

    def __new__(cls, config: FlextApiConfig | None = None) -> Self:
        """Intercept positional config argument and convert to kwargs.

        Args:
            config: Optional FlextApiConfig (passed to __init__ via attribute).

        """
        instance = super().__new__(cls)
        if config is not None:
            instance._flext_api_config = config
        return instance

    def __init__(self, config: FlextApiConfig | None = None, **kwargs: object) -> None:
        """Initialize with optional configuration model.

        Args:
        config: Optional FlextApiConfig model with base_url, timeout, headers, etc.
                If None, uses default configuration.
        **kwargs: Additional Pydantic model fields (ignored for this service).

        """
        super().__init__(**kwargs)
        api_config = getattr(self, "_flext_api_config", None)
        if api_config is not None:
            self._config = api_config
            delattr(self, "_flext_api_config")
        elif config is not None:
            self._config = config
        else:
            self._config = FlextApiConfig()

    def execute(self) -> FlextResult[FlextApiConfig]:
        """Execute FlextService interface - return configuration."""
        return FlextResult[FlextApiConfig].ok(self._config)

    def request(
        self, request: FlextApiModels.HttpRequest
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Execute HTTP request from model using monadic patterns.

        Args:
        request: HttpRequest Value Object with method, url, headers, body.

        Returns:
        FlextResult[HttpResponse]: Success with HttpResponse or error message.

        """
        return (
            self._build_url(request.url)
            .flat_map(
                lambda url: self._serialize_body(request.body).map(
                    lambda body: (url, body)
                )
            )
            .flat_map(
                lambda url_body: self._execute_http_request(
                    request=request,
                    url=url_body[0],
                    serialized_body=url_body[1],
                )
            )
        )

    def _execute_http_request(
        self,
        request: FlextApiModels.HttpRequest,
        url: str,
        serialized_body: bytes,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Execute HTTP request using httpx client."""
        try:
            headers: dict[str, str] = {
                **self._config.default_headers,
                **request.headers,
            }

            with httpx.Client(timeout=request.timeout) as client:
                request_kwargs: dict[str, object] = {
                    "method": request.method,
                    "url": url,
                    "headers": headers,
                    "params": request.query_params,
                }
                if serialized_body:
                    request_kwargs["content"] = serialized_body
                response = client.request(**request_kwargs)

            return self._deserialize_body(response).map(
                lambda body: FlextApiModels.HttpResponse(
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    body=body,
                )
            )
        except Exception as exc:
            return FlextResult[FlextApiModels.HttpResponse].fail(str(exc))

    def _build_url(self, path: str) -> FlextResult[str]:
        """Build full URL from base_url and path."""
        if not path:
            return FlextResult[str].fail("URL path cannot be empty")

        path_stripped = path.strip()
        if not path_stripped:
            return FlextResult[str].fail("URL path cannot be empty")

        base_url_stripped = self._config.base_url.strip()
        if not base_url_stripped:
            return FlextResult[str].ok(path_stripped)

        base = base_url_stripped.rstrip("/")
        if path_stripped.startswith("/"):
            return FlextResult[str].ok(f"{base}{path_stripped}")
        return FlextResult[str].ok(f"{base}/{path_stripped}")

    @staticmethod
    def _serialize_body(
        body: FlextApiTypes.RequestBody | None,
    ) -> FlextResult[bytes]:
        """Serialize request body to bytes."""
        if body is None:
            return FlextResult[bytes].ok(b"")
        if isinstance(body, bytes):
            return FlextResult[bytes].ok(body)
        if isinstance(body, str):
            return FlextResult[bytes].ok(body.encode("utf-8"))
        try:
            serialized = json.dumps(body).encode("utf-8")
            return FlextResult[bytes].ok(serialized)
        except (TypeError, ValueError) as e:
            return FlextResult[bytes].fail(f"Failed to serialize body: {e}")

    @staticmethod
    def _deserialize_body(
        response: httpx.Response,
    ) -> FlextResult[FlextApiTypes.ResponseBody]:
        """Deserialize response body based on content-type."""
        json_result = FlextApiClient._deserialize_json(response)
        if json_result.is_success:
            return json_result

        text_result = FlextApiClient._deserialize_text(response)
        if text_result.is_success:
            return text_result

        bytes_result = FlextApiClient._deserialize_bytes(response)
        if bytes_result.is_success:
            return bytes_result

        return FlextResult[FlextApiTypes.ResponseBody].fail(
            "Failed to deserialize response body: no valid format found"
        )

    @staticmethod
    def _deserialize_json(
        response: httpx.Response,
    ) -> FlextResult[FlextApiTypes.ResponseBody]:
        """Deserialize response as JSON."""
        try:
            json_data = response.json()
            if isinstance(json_data, dict):
                return FlextResult[FlextApiTypes.ResponseBody].ok(json_data)
            if isinstance(json_data, (str, bytes)):
                return FlextResult[FlextApiTypes.ResponseBody].ok(json_data)
            return FlextResult[FlextApiTypes.ResponseBody].ok(str(json_data))
        except (AttributeError, ValueError, TypeError, Exception) as e:
            return FlextResult[FlextApiTypes.ResponseBody].fail(
                f"JSON deserialization failed: {e}"
            )

    @staticmethod
    def _deserialize_text(response: httpx.Response) -> FlextResult[str]:
        """Deserialize response as text."""
        if not hasattr(response, "text"):
            return FlextResult[str].fail("Response does not have text attribute")
        response_text = response.text
        if not isinstance(response_text, str):
            return FlextResult[str].fail(
                f"Response text is not a string: {type(response_text)}"
            )
        return FlextResult[str].ok(response_text)

    @staticmethod
    def _deserialize_bytes(response: httpx.Response) -> FlextResult[bytes]:
        """Deserialize response as bytes."""
        if not hasattr(response, "content"):
            return FlextResult[bytes].fail("Response does not have content attribute")
        response_content = response.content
        if not isinstance(response_content, bytes):
            return FlextResult[bytes].fail(
                f"Response content is not bytes: {type(response_content)}"
            )
        return FlextResult[bytes].ok(response_content)


__all__ = ["FlextApiClient"]

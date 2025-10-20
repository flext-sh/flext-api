"""Generic HTTP Client - Domain-agnostic HTTP operations.

Pure HTTP client wrapper with FLEXT patterns. Single responsibility:
Execute HTTP requests and return FlextResult. All retry, timeout, and
configuration handled via FlextApiConfig model passed at construction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
from typing import Any

import httpx
from flext_core import FlextResult, FlextService

from flext_api.config import FlextApiConfig
from flext_api.models import FlextApiModels


class FlextApiClient(FlextService[FlextApiConfig]):
    """Generic HTTP client using FLEXT patterns.

    Single responsibility: Execute HTTP requests with FlextResult error handling.
    All configuration through FlextApiConfig model (Pydantic v2).
    Domain-agnostic - works with any HTTP endpoint.

    Uses httpx for HTTP operations, delegates to models for data validation.
    """

    def __init__(self, config: FlextApiConfig) -> None:
        """Initialize with configuration model.

        Args:
            config: FlextApiConfig model with base_url, timeout, headers, etc.

        """
        super().__init__()
        self._config = config

    def execute(self) -> FlextResult[FlextApiConfig]:
        """Execute FlextService interface - return configuration."""
        return FlextResult[FlextApiConfig].ok(self._config)

    def request(
        self, request: FlextApiModels.HttpRequest
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Execute HTTP request from model.

        Args:
            request: HttpRequest Value Object with method, url, headers, body.

        Returns:
            FlextResult[HttpResponse]: Success with HttpResponse or error message.

        """
        try:
            headers = {**self._config.headers, **request.headers}
            url = self._build_url(request.url)

            with httpx.Client(timeout=request.timeout) as client:
                response = client.request(
                    method=request.method,
                    url=url,
                    headers=headers,
                    params=request.query_params,
                    content=self._serialize_body(request.body),
                )

            return FlextResult[FlextApiModels.HttpResponse].ok(
                FlextApiModels.HttpResponse(
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    body=self._deserialize_body(response),
                )
            )

        except Exception as e:
            return FlextResult[FlextApiModels.HttpResponse].fail(str(e))

    def _build_url(self, path: str) -> str:
        """Build full URL from base_url and path."""
        if not self._config.base_url:
            return path
        base = self._config.base_url.rstrip("/")
        return f"{base}{path}" if path.startswith("/") else f"{base}/{path}"

    @staticmethod
    def _serialize_body(body: Any) -> bytes | None:
        """Serialize request body to bytes."""
        if body is None:
            return None
        if isinstance(body, bytes):
            return body
        if isinstance(body, str):
            return body.encode("utf-8")
        return json.dumps(body).encode("utf-8")

    @staticmethod
    def _deserialize_body(response: httpx.Response) -> Any:
        """Deserialize response body based on content-type."""
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                return response.json()
            except Exception:
                return response.text
        return response.text


__all__ = ["FlextApiClient"]

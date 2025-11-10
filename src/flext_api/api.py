"""FLEXT API - Unified HTTP Facade.

Single entry point for all HTTP operations. Delegates to FlextApiClient for
actual HTTP work, to FlextApiModels for data validation. 100% GENERIC.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar

from flext_core import FlextResult, FlextService

from flext_api.client import FlextApiClient
from flext_api.config import FlextApiConfig
from flext_api.models import FlextApiModels
from flext_api.typings import FlextApiTypes


class FlextApi(FlextService[FlextApiConfig]):
    """Unified HTTP API facade - pure delegation pattern.

    Single responsibility: Delegate HTTP operations to FlextApiClient.
    All configuration through FlextApiConfig model.
    All data validation through FlextApiModels.
    100% GENERIC - no domain coupling.
    """

    # Unified namespace - direct access to FLEXT components
    Models: ClassVar = FlextApiModels
    Config: ClassVar = FlextApiConfig

    def __init__(self, config: FlextApiConfig | None = None) -> None:
        """Initialize with optional config.

        Args:
        config: FlextApiConfig model or None for defaults.

        """
        super().__init__()
        self._config = config or FlextApiConfig()
        self._client = FlextApiClient(self._config)

    def execute(self) -> FlextResult[FlextApiConfig]:
        """Execute FlextService interface."""
        return FlextResult[FlextApiConfig].ok(self._config)

    def request(
        self, request: FlextApiModels.HttpRequest
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Execute HTTP request - pure delegation to client.

        Args:
        request: HttpRequest model.

        Returns:
        FlextResult[HttpResponse]: Response or error.

        """
        return self._client.request(request)

    def _http_method(
        self,
        method: str,
        url: str,
        data: FlextApiTypes.RequestBody | None = None,
        headers: dict[str, str] | None = None,
        request_kwargs: FlextApiTypes.RequestKwargs | None = None,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Generic HTTP method executor - eliminates code duplication.

        Args:
        method: HTTP method (GET, POST, etc.).
        url: Request URL.
        data: Optional body.
        headers: Optional headers.
        request_kwargs: Additional parameters aligned with FlextApiModels.HttpRequest.

        Returns:
        FlextResult[HttpResponse]: Response or error.

        """
        http_request = self._build_http_request(
            method=method,
            url=url,
            explicit_body=data,
            explicit_headers=headers,
            request_kwargs=request_kwargs,
        )
        return self.request(http_request)

    def _build_http_request(
        self,
        method: str,
        url: str,
        explicit_body: FlextApiTypes.RequestBody | None,
        explicit_headers: dict[str, str] | None,
        request_kwargs: FlextApiTypes.RequestKwargs | None,
    ) -> FlextApiModels.HttpRequest:
        body = self._resolve_body(explicit_body, request_kwargs)
        headers = self._resolve_headers(explicit_headers, request_kwargs)
        timeout_value = self._resolve_timeout(request_kwargs)
        query_params = self._resolve_query_params(request_kwargs)

        return FlextApiModels.HttpRequest(
            method=method,
            url=url,
            body=body,
            headers=headers,
            query_params=query_params,
            timeout=timeout_value,
        )

    def _resolve_body(
        self,
        explicit_body: FlextApiTypes.RequestBody | None,
        request_kwargs: FlextApiTypes.RequestKwargs | None,
    ) -> FlextApiTypes.RequestBody | None:
        if explicit_body is not None:
            return explicit_body
        if not request_kwargs:
            return None
        json_payload = request_kwargs.get("json")
        if json_payload is not None:
            return json_payload
        data_payload = request_kwargs.get("data")
        if data_payload is not None:
            return data_payload
        return None

    def _resolve_headers(
        self,
        explicit_headers: dict[str, str] | None,
        request_kwargs: FlextApiTypes.RequestKwargs | None,
    ) -> dict[str, str]:
        combined_headers: dict[str, str] = {}
        if request_kwargs:
            kw_headers = request_kwargs.get("headers")
            if kw_headers:
                combined_headers.update(kw_headers)
        if explicit_headers:
            combined_headers.update(explicit_headers)
        return combined_headers

    def _resolve_timeout(
        self, request_kwargs: FlextApiTypes.RequestKwargs | None
    ) -> float:
        if request_kwargs:
            timeout_value = request_kwargs.get("timeout")
            if timeout_value is not None:
                return float(timeout_value)
        return self._config.timeout

    @staticmethod
    def _resolve_query_params(
        request_kwargs: FlextApiTypes.RequestKwargs | None,
    ) -> FlextApiTypes.WebParams | None:
        if not request_kwargs:
            return None
        params = request_kwargs.get("params")
        if params is None:
            return None
        return params

    def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        request_kwargs: FlextApiTypes.RequestKwargs | None = None,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """HTTP GET - delegates to generic method."""
        return self._http_method(
            method="GET",
            url=url,
            headers=headers,
            request_kwargs=request_kwargs,
        )

    def post(
        self,
        url: str,
        data: FlextApiTypes.RequestBody | None = None,
        headers: dict[str, str] | None = None,
        request_kwargs: FlextApiTypes.RequestKwargs | None = None,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """HTTP POST - delegates to generic method."""
        return self._http_method(
            method="POST",
            url=url,
            data=data,
            headers=headers,
            request_kwargs=request_kwargs,
        )

    def put(
        self,
        url: str,
        data: FlextApiTypes.RequestBody | None = None,
        headers: dict[str, str] | None = None,
        request_kwargs: FlextApiTypes.RequestKwargs | None = None,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """HTTP PUT - delegates to generic method."""
        return self._http_method(
            method="PUT",
            url=url,
            data=data,
            headers=headers,
            request_kwargs=request_kwargs,
        )

    def delete(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        request_kwargs: FlextApiTypes.RequestKwargs | None = None,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """HTTP DELETE - delegates to generic method."""
        return self._http_method(
            method="DELETE",
            url=url,
            headers=headers,
            request_kwargs=request_kwargs,
        )

    def patch(
        self,
        url: str,
        data: FlextApiTypes.RequestBody | None = None,
        headers: dict[str, str] | None = None,
        request_kwargs: FlextApiTypes.RequestKwargs | None = None,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """HTTP PATCH - delegates to generic method."""
        return self._http_method(
            method="PATCH",
            url=url,
            data=data,
            headers=headers,
            request_kwargs=request_kwargs,
        )


__all__ = ["FlextApi"]

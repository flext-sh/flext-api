"""FLEXT API - Unified HTTP Facade.

Single entry point for all HTTP operations. Delegates to FlextApiClient for
actual HTTP work, to FlextApiModels for data validation. 100% GENERIC.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Any, ClassVar

from flext_core import FlextResult, FlextService

from flext_api.client import FlextApiClient
from flext_api.config import FlextApiConfig
from flext_api.models import FlextApiModels
from flext_api.typings import FlextApiTypes

# Type for HTTP method kwargs (common httpx parameters)
HttpMethodKwargs = dict[str, Any]


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
        **kwargs: HttpMethodKwargs,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Generic HTTP method executor - eliminates code duplication.

        Args:
        method: HTTP method (GET, POST, etc.).
        url: Request URL.
        data: Optional body.
        headers: Optional headers.
        **kwargs: Additional parameters.

        Returns:
        FlextResult[HttpResponse]: Response or error.

        """
        # Extract only HttpRequest-compatible parameters from kwargs
        timeout_value = None
        if "timeout" in kwargs:
            timeout_val = kwargs["timeout"]
            if isinstance(timeout_val, (int, float)):
                timeout_value = float(timeout_val)

        req = FlextApiModels.HttpRequest(
            method=method,
            url=url,
            body=data,
            headers=headers or {},
            timeout=timeout_value or 30.0,
        )
        return self.request(req)

    def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        **kwargs: HttpMethodKwargs,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """HTTP GET - delegates to generic method."""
        return self._http_method("GET", url, headers=headers, **kwargs)

    def post(
        self,
        url: str,
        data: FlextApiTypes.RequestBody | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: HttpMethodKwargs,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """HTTP POST - delegates to generic method."""
        return self._http_method("POST", url, data, headers, **kwargs)

    def put(
        self,
        url: str,
        data: FlextApiTypes.RequestBody | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: HttpMethodKwargs,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """HTTP PUT - delegates to generic method."""
        return self._http_method("PUT", url, data, headers, **kwargs)

    def delete(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        **kwargs: HttpMethodKwargs,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """HTTP DELETE - delegates to generic method."""
        return self._http_method("DELETE", url, headers=headers, **kwargs)

    def patch(
        self,
        url: str,
        data: FlextApiTypes.RequestBody | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: HttpMethodKwargs,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """HTTP PATCH - delegates to generic method."""
        return self._http_method("PATCH", url, data, headers, **kwargs)


__all__ = ["FlextApi"]

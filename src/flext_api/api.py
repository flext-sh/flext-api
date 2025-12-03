"""FLEXT API - Unified HTTP Facade.

Single entry point for all HTTP operations. Delegates to FlextApiClient for
actual HTTP work, to FlextApiModels for data validation. 100% GENERIC.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar, Self

from flext_core import FlextService, r

from flext_api.client import FlextApiClient
from flext_api.config import FlextApiConfig
from flext_api.constants import FlextApiConstants
from flext_api.models import FlextApiModels
from flext_api.typings import FlextApiTypes
from flext_api.utilities import FlextApiUtilities


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

    def __new__(cls, config: FlextApiConfig | None = None) -> Self:
        """Intercept positional config argument and convert to kwargs.

        Args:
            config: Optional FlextApiConfig (passed to __init__ via attribute).

        """
        instance = super().__new__(cls)
        if config is not None:
            # Type-safe attribute assignment for __new__ pattern
            # Use object.__setattr__ to bypass type checker for dynamic attribute
            object.__setattr__(instance, "_flext_api_config", config)
        return instance

    def __init__(
        self,
        config: FlextApiConfig | None = None,
        **kwargs: FlextApiTypes.JsonValue | str | int | bool,
    ) -> None:
        """Initialize with optional config.

        Args:
        config: FlextApiConfig model or None for defaults.
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
        self._client = FlextApiClient(config=self._config)

    def execute(
        self, **_kwargs: FlextApiTypes.JsonValue | str | int | bool
    ) -> r[FlextApiConfig]:
        """Execute FlextService interface."""
        return r[FlextApiConfig].ok(self._config)

    def request(
        self, request: FlextApiModels.HttpRequest
    ) -> r[FlextApiModels.HttpResponse]:
        """Execute HTTP request - pure delegation to client.

        Args:
        request: HttpRequest model.

        Returns:
        r[HttpResponse]: Response or error.

        """
        return self._client.request(request)

    def _http_method(
        self,
        method: str,
        url: str,
        data: FlextApiTypes.RequestBody | None = None,
        headers: dict[str, str] | None = None,
        request_kwargs: FlextApiTypes.RequestKwargs | None = None,
        timeout: float | None = None,
    ) -> r[FlextApiModels.HttpResponse]:
        """Generic HTTP method executor using monadic patterns - no fallbacks.

        Args:
        method: HTTP method (GET, POST, etc.).
        url: Request URL.
        data: Optional body.
        headers: Optional headers.
        request_kwargs: Additional parameters aligned with FlextApiModels.HttpRequest.
        timeout: Optional timeout override.

        Returns:
        r[HttpResponse]: Response or error.

        """
        # Extract body using monadic pattern
        body_result = FlextApiUtilities.RequestUtils.extract_body_from_kwargs(
            data, request_kwargs
        )
        if body_result.is_failure:
            return r[FlextApiModels.HttpResponse].fail(
                body_result.error or "Body extraction failed"
            )

        # Merge headers using monadic pattern
        headers_result = FlextApiUtilities.RequestUtils.merge_headers(
            headers, request_kwargs
        )
        if headers_result.is_failure:
            return r[FlextApiModels.HttpResponse].fail(
                headers_result.error or "Header extraction failed"
            )

        # Validate timeout using monadic pattern
        timeout_result = FlextApiUtilities.RequestUtils.validate_and_extract_timeout(
            timeout, request_kwargs
        )
        if timeout_result.is_failure:
            return r[FlextApiModels.HttpResponse].fail(
                timeout_result.error or "Timeout extraction failed"
            )

        # Extract query params - use empty dict if not present
        query_params: FlextApiTypes.WebParams = {}
        if request_kwargs is not None and "params" in request_kwargs:
            params_value = request_kwargs["params"]
            if params_value is not None:
                # Convert dict[str, str] to WebParams (dict[str, str | list[str]])
                if isinstance(params_value, dict):
                    query_params = {
                        k: (v if isinstance(v, (str, list)) else str(v))
                        for k, v in params_value.items()
                    }
                else:
                    return r[FlextApiModels.HttpResponse].fail(
                        f"Invalid params type: {type(params_value)}"
                    )

        # Use body value directly (HttpRequest accepts empty dict or actual body)
        body_value = body_result.unwrap()
        body_final: FlextApiTypes.RequestBody = body_value

        # Create request model
        http_request = FlextApiModels.HttpRequest(
            method=method,
            url=url,
            body=body_final,
            headers=headers_result.unwrap(),
            query_params=query_params,
            timeout=timeout_result.unwrap(),
        )
        return self.request(http_request)

    def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        request_kwargs: FlextApiTypes.RequestKwargs | None = None,
    ) -> r[FlextApiModels.HttpResponse]:
        """HTTP GET - delegates to generic method."""
        return self._http_method(
            method=FlextApiConstants.Method.GET,
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
    ) -> r[FlextApiModels.HttpResponse]:
        """HTTP POST - delegates to generic method."""
        return self._http_method(
            method=FlextApiConstants.Method.POST,
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
    ) -> r[FlextApiModels.HttpResponse]:
        """HTTP PUT - delegates to generic method."""
        return self._http_method(
            method=FlextApiConstants.Method.PUT,
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
    ) -> r[FlextApiModels.HttpResponse]:
        """HTTP DELETE - delegates to generic method."""
        return self._http_method(
            method=FlextApiConstants.Method.DELETE,
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
    ) -> r[FlextApiModels.HttpResponse]:
        """HTTP PATCH - delegates to generic method."""
        return self._http_method(
            method=FlextApiConstants.Method.PATCH,
            url=url,
            data=data,
            headers=headers,
            request_kwargs=request_kwargs,
        )


__all__ = ["FlextApi"]

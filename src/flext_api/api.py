"""FLEXT API - Unified HTTP Facade.

Single entry point for all HTTP operations. Delegates to FlextApiClient for
actual HTTP work, to FlextApiModels for data validation. 100% GENERIC.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar, Self, cast

from flext_core import FlextRuntime, FlextService, r, t

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
        # Type narrowing: convert kwargs to expected type
        kwargs_typed: dict[str, t.GeneralValueType] = {
            k: cast("t.GeneralValueType", FlextRuntime.normalize_to_general_value(v))
            for k, v in kwargs.items()
        }
        super().__init__(**kwargs_typed)
        api_config = getattr(self, "_flext_api_config", None)
        if api_config is not None:
            # Override _config from base class with FlextApiConfig
            object.__setattr__(self, "_config", api_config)
            delattr(self, "_flext_api_config")
        elif config is not None:
            # Override _config from base class with FlextApiConfig
            object.__setattr__(self, "_config", config)
        else:
            # Override _config from base class with FlextApiConfig
            object.__setattr__(self, "_config", FlextApiConfig())
        # Type narrowing: _config is now FlextApiConfig
        config_typed: FlextApiConfig = cast("FlextApiConfig", self._config)
        self._client = FlextApiClient(config=config_typed)

    def execute(
        self,
        **_kwargs: FlextApiTypes.JsonValue | str | int | bool,
    ) -> r[FlextApiConfig]:
        """Execute FlextService interface."""
        # Type narrowing: _config is FlextApiConfig
        config_typed: FlextApiConfig = cast("FlextApiConfig", self._config)
        return r[FlextApiConfig].ok(config_typed)

    def request(
        self,
        request: FlextApiModels.HttpRequest,
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
        # Type narrowing: convert RequestKwargs to dict[str, object] | None
        request_kwargs_dict: dict[str, object] | None = (
            dict(request_kwargs.items()) if request_kwargs is not None else None
        )
        # Extract body using monadic pattern
        body_result = FlextApiUtilities.RequestUtils.extract_body_from_kwargs(
            data,
            request_kwargs_dict,
        )
        if body_result.is_failure:
            return r[FlextApiModels.HttpResponse].fail(
                body_result.error or "Body extraction failed",
            )

        # Merge headers using monadic pattern
        headers_result = FlextApiUtilities.RequestUtils.merge_headers(
            headers,
            request_kwargs_dict,
        )
        if headers_result.is_failure:
            return r[FlextApiModels.HttpResponse].fail(
                headers_result.error or "Header extraction failed",
            )

        # Validate timeout using monadic pattern
        timeout_result = FlextApiUtilities.RequestUtils.validate_and_extract_timeout(
            timeout,
            request_kwargs_dict,
        )
        if timeout_result.is_failure:
            return r[FlextApiModels.HttpResponse].fail(
                timeout_result.error or "Timeout extraction failed",
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
                        f"Invalid params type: {type(params_value)}",
                    )

        # Use body value directly (HttpRequest accepts empty dict or actual body)
        body_value = body_result.unwrap()
        # Type narrowing: ensure RequestBody compatibility
        if isinstance(body_value, (str, bytes)):
            body_final: FlextApiTypes.RequestBody = body_value
        elif isinstance(body_value, dict):
            body_final = body_value  # type: ignore[assignment]
        else:
            body_final = str(body_value)

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

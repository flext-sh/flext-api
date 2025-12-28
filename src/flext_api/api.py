"""FLEXT API - Unified HTTP Facade.

Single entry point for all HTTP operations. Delegates to FlextApiClient for
actual HTTP work, to FlextApiModels for data validation. 100% GENERIC.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar, Self

from flext_core import FlextLogger, r, s
from flext_core.runtime import FlextRuntime

from flext_api.client import FlextApiClient
from flext_api.constants import FlextApiConstants
from flext_api.models import FlextApiModels
from flext_api.settings import FlextApiSettings
from flext_api.typings import t
from flext_api.utilities import FlextApiUtilities


class FlextApi(s[FlextApiSettings]):
    """Unified HTTP API facade - pure delegation pattern.

    Single responsibility: Delegate HTTP operations to FlextApiClient.
    All configuration through FlextApiSettings model.
    All data validation through FlextApiModels.
    100% GENERIC - no domain coupling.
    """

    # Unified namespace - direct access to FLEXT components
    Models: ClassVar = FlextApiModels
    Config: ClassVar = FlextApiSettings

    def __new__(cls, config: FlextApiSettings | None = None) -> Self:
        """Intercept positional config argument and convert to kwargs.

        Args:
            config: Optional FlextApiSettings (passed to __init__ via attribute).

        """
        instance = super().__new__(cls)
        if config is not None:
            # Store config for use in __init__
            object.__setattr__(instance, "_init_config", config)
        return instance

    def __init__(
        self,
        config: FlextApiSettings | None = None,
        **kwargs: t.JsonValue | str | int | bool,
    ) -> None:
        """Initialize with optional config.

        Args:
        config: FlextApiSettings model or None for defaults.
        **kwargs: Additional Pydantic model fields (ignored for this service).

        """
        # Determine which config to use
        init_config = getattr(self, "_init_config", None)
        if init_config is not None:
            api_config = init_config
        elif config is not None:
            api_config = config
        else:
            api_config = FlextApiSettings()

        # Type narrowing: convert kwargs to expected type
        kwargs_typed: dict[str, t.GeneralValueType] = {
            k: FlextRuntime.normalize_to_general_value(v) for k, v in kwargs.items()
        }
        super().__init__(**kwargs_typed)

        # Set the _config to the API-specific settings
        object.__setattr__(self, "_config", api_config)

        # Initialize HTTP client with API config
        self._client = FlextApiClient(config=api_config)

    def execute(
        self,
        **kwargs: t.JsonValue | str | int | bool,
    ) -> r[FlextApiSettings]:
        """Execute FlextService interface."""
        if kwargs:
            FlextLogger(__name__).info(f"Execute called with kwargs: {kwargs}")
        config = (
            self._config
            if isinstance(self._config, FlextApiSettings)
            else FlextApiSettings()
        )
        return r[FlextApiSettings].ok(config)

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

    def _extract_query_params(
        self,
        request_kwargs: t.Api.RequestKwargs | None,
    ) -> r[t.Api.WebParams]:
        """Extract and validate query parameters from request_kwargs.

        Args:
            request_kwargs: Optional request kwargs containing params.

        Returns:
            r[WebParams]: Query params dict or error.

        """
        query_params: t.Api.WebParams = {}
        if request_kwargs is None or "params" not in request_kwargs:
            return r[t.Api.WebParams].ok(query_params)

        params_value = request_kwargs["params"]
        if params_value is None:
            return r[t.Api.WebParams].ok(query_params)

        if not isinstance(params_value, dict):
            return r[t.Api.WebParams].fail(
                f"Invalid params type: {type(params_value)}",
            )

        # Type reconstruction: build params dict with proper narrowing
        params_result: dict[str, str | list[str]] = {}
        for k, v in params_value.items():
            if isinstance(v, str):
                params_result[k] = v
            elif isinstance(v, list):
                # Convert list elements to strings if needed
                str_list: list[str] = [str(item) for item in v]
                params_result[k] = str_list
            else:
                params_result[k] = str(v)
        return r[t.Api.WebParams].ok(params_result)

    def _finalize_body(
        self,
        body_value: object,
    ) -> t.Api.RequestBody:
        """Finalize body value to RequestBody type.

        Args:
            body_value: Raw body value from extraction.

        Returns:
            RequestBody: Finalized body value.

        """
        if isinstance(body_value, (str, bytes)):
            return body_value
        if isinstance(body_value, dict):
            # dict is compatible with JsonObject which is part of RequestBody
            return body_value
        return str(body_value)

    def _http_method(
        self,
        method: str,
        url: str,
        data: t.Api.RequestBody | None = None,
        headers: dict[str, str] | None = None,
        request_kwargs: t.Api.RequestKwargs | None = None,
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
        # Type narrowing: convert RequestKwargs to dict[str, t.GeneralValueType] | None
        request_kwargs_dict: dict[str, t.GeneralValueType] | None = (
            dict(request_kwargs.items()) if request_kwargs is not None else None
        )
        # Extract body using monadic pattern
        body_result = FlextApiUtilities.Api.RequestUtils.extract_body_from_kwargs(
            data,
            request_kwargs_dict,
        )
        if body_result.is_failure:
            return r[FlextApiModels.HttpResponse].fail(
                body_result.error or "Body extraction failed",
            )

        # Merge headers using monadic pattern
        headers_result = FlextApiUtilities.Api.RequestUtils.merge_headers(
            headers,
            request_kwargs_dict,
        )
        if headers_result.is_failure:
            return r[FlextApiModels.HttpResponse].fail(
                headers_result.error or "Header extraction failed",
            )

        # Validate timeout using monadic pattern
        timeout_result = (
            FlextApiUtilities.Api.RequestUtils.validate_and_extract_timeout(
                timeout,
                request_kwargs_dict,
            )
        )
        if timeout_result.is_failure:
            return r[FlextApiModels.HttpResponse].fail(
                timeout_result.error or "Timeout extraction failed",
            )

        # Extract query params
        query_params_result = self._extract_query_params(request_kwargs)
        if query_params_result.is_failure:
            return r[FlextApiModels.HttpResponse].fail(
                query_params_result.error or "Query params extraction failed",
            )

        # Finalize body value
        body_value = body_result.value
        body_final = self._finalize_body(body_value)

        # Create request model
        http_request = FlextApiModels.HttpRequest(
            method=method,
            url=url,
            body=body_final,
            headers=headers_result.value,
            query_params=query_params_result.value,
            timeout=timeout_result.value,
        )
        return self.request(http_request)

    def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        request_kwargs: t.Api.RequestKwargs | None = None,
    ) -> r[FlextApiModels.HttpResponse]:
        """HTTP GET - delegates to generic method."""
        return self._http_method(
            method=FlextApiConstants.Api.Method.GET,
            url=url,
            headers=headers,
            request_kwargs=request_kwargs,
        )

    def post(
        self,
        url: str,
        data: t.Api.RequestBody | None = None,
        headers: dict[str, str] | None = None,
        request_kwargs: t.Api.RequestKwargs | None = None,
    ) -> r[FlextApiModels.HttpResponse]:
        """HTTP POST - delegates to generic method."""
        return self._http_method(
            method=FlextApiConstants.Api.Method.POST,
            url=url,
            data=data,
            headers=headers,
            request_kwargs=request_kwargs,
        )

    def put(
        self,
        url: str,
        data: t.Api.RequestBody | None = None,
        headers: dict[str, str] | None = None,
        request_kwargs: t.Api.RequestKwargs | None = None,
    ) -> r[FlextApiModels.HttpResponse]:
        """HTTP PUT - delegates to generic method."""
        return self._http_method(
            method=FlextApiConstants.Api.Method.PUT,
            url=url,
            data=data,
            headers=headers,
            request_kwargs=request_kwargs,
        )

    def delete(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        request_kwargs: t.Api.RequestKwargs | None = None,
    ) -> r[FlextApiModels.HttpResponse]:
        """HTTP DELETE - delegates to generic method."""
        return self._http_method(
            method=FlextApiConstants.Api.Method.DELETE,
            url=url,
            headers=headers,
            request_kwargs=request_kwargs,
        )

    def patch(
        self,
        url: str,
        data: t.Api.RequestBody | None = None,
        headers: dict[str, str] | None = None,
        request_kwargs: t.Api.RequestKwargs | None = None,
    ) -> r[FlextApiModels.HttpResponse]:
        """HTTP PATCH - delegates to generic method."""
        return self._http_method(
            method=FlextApiConstants.Api.Method.PATCH,
            url=url,
            data=data,
            headers=headers,
            request_kwargs=request_kwargs,
        )


__all__ = ["FlextApi"]

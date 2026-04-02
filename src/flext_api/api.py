"""FLEXT API - Unified HTTP Facade.

Single entry point for all HTTP operations. Delegates to FlextApiClient for
actual HTTP work, to FlextApiModels for data validation. 100% GENERIC.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping
from typing import ClassVar, Self, override

from pydantic import ConfigDict

from flext_api import FlextApiClient, FlextApiSettings, c, m, t, u
from flext_core import FlextLogger, r, s


class FlextApi(s[FlextApiSettings]):
    """Unified HTTP API facade - pure delegation pattern.

    Single responsibility: Delegate HTTP operations to FlextApiClient.
    All configuration through FlextApiSettings model.
    All data validation through FlextApiModels.
    100% GENERIC - no domain coupling.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(use_enum_values=True)
    "Unified HTTP API facade - pure delegation pattern.\n\n    Single responsibility: Delegate HTTP operations to FlextApiClient.\n    All configuration through FlextApiSettings model.\n    All data validation through FlextApiModels.\n    100% GENERIC - no domain coupling.\n    "
    Models: ClassVar = m

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
        """Initialize with optional config.

        Args:
        config: FlextApiSettings model or None for defaults.
        **kwargs: Additional Pydantic model fields (ignored for this service).

        """
        init_config = getattr(self, "_init_config", None)
        if init_config is not None:
            api_config = init_config
        elif config is not None:
            api_config = config
        else:
            api_config = FlextApiSettings.model_validate({})
        _ = kwargs
        super().__init__()
        object.__setattr__(self, "_config", api_config)
        self._client = FlextApiClient(config=api_config)

    def delete(
        self,
        url: str,
        headers: t.StrMapping | None = None,
        request_kwargs: t.Api.RequestKwargs | None = None,
    ) -> r[m.Api.HttpResponse]:
        """HTTP DELETE - delegates to generic method."""
        return self._http_method(
            method=c.Api.Method.DELETE,
            url=url,
            headers=headers,
            request_kwargs=request_kwargs,
        )

    @override
    def execute(self, **kwargs: t.Scalar) -> r[FlextApiSettings]:
        """Execute FlextService interface."""
        if kwargs:
            FlextLogger(__name__).info(f"Execute called with kwargs: {kwargs}")
        config = self._get_config()
        return r[FlextApiSettings].ok(config)

    def get(
        self,
        url: str,
        headers: t.StrMapping | None = None,
        request_kwargs: t.Api.RequestKwargs | None = None,
    ) -> r[m.Api.HttpResponse]:
        """HTTP GET - delegates to generic method."""
        return self._http_method(
            method=c.Api.Method.GET,
            url=url,
            headers=headers,
            request_kwargs=request_kwargs,
        )

    def patch(
        self,
        url: str,
        data: t.Api.RequestBody | None = None,
        headers: t.StrMapping | None = None,
        request_kwargs: t.Api.RequestKwargs | None = None,
    ) -> r[m.Api.HttpResponse]:
        """HTTP PATCH - delegates to generic method."""
        return self._http_method(
            method=c.Api.Method.PATCH,
            url=url,
            data=data,
            headers=headers,
            request_kwargs=request_kwargs,
        )

    def post(
        self,
        url: str,
        data: t.Api.RequestBody | None = None,
        headers: t.StrMapping | None = None,
        request_kwargs: t.Api.RequestKwargs | None = None,
    ) -> r[m.Api.HttpResponse]:
        """HTTP POST - delegates to generic method."""
        return self._http_method(
            method=c.Api.Method.POST,
            url=url,
            data=data,
            headers=headers,
            request_kwargs=request_kwargs,
        )

    def put(
        self,
        url: str,
        data: t.Api.RequestBody | None = None,
        headers: t.StrMapping | None = None,
        request_kwargs: t.Api.RequestKwargs | None = None,
    ) -> r[m.Api.HttpResponse]:
        """HTTP PUT - delegates to generic method."""
        return self._http_method(
            method=c.Api.Method.PUT,
            url=url,
            data=data,
            headers=headers,
            request_kwargs=request_kwargs,
        )

    def request(self, request: m.Api.HttpRequest) -> r[m.Api.HttpResponse]:
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
        if not isinstance(params_value, Mapping):
            return r[t.Api.WebParams].fail(f"Invalid params type: {type(params_value)}")
        params_mapping: Mapping[str, t.ApiJsonValue] = params_value
        params_result: t.MutableStrMapping = {}
        for k, v in params_mapping.items():
            if isinstance(v, str):
                params_result[k] = v
            elif isinstance(v, (int, float, bool)):
                params_result[k] = f"{v}"
            else:
                params_result[k] = ""
        return r[t.Api.WebParams].ok(params_result)

    def _get_config(self) -> FlextApiSettings:
        config = self._config
        if isinstance(config, FlextApiSettings):
            return config
        return FlextApiSettings.model_validate({})

    def _http_method(
        self,
        method: str,
        url: str,
        data: t.Api.RequestBody | None = None,
        headers: t.StrMapping | None = None,
        request_kwargs: t.Api.RequestKwargs | None = None,
        timeout: float | None = None,
    ) -> r[m.Api.HttpResponse]:
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
        request_kwargs_dict: Mapping[str, t.ApiJsonValue] | None = request_kwargs
        body_result = u.Api.RequestUtils.extract_body_from_kwargs(
            data,
            request_kwargs_dict,
        )
        if body_result.is_failure:
            return r[m.Api.HttpResponse].fail(
                body_result.error or "Body extraction failed"
            )
        headers_result = u.Api.RequestUtils.merge_headers(
            headers,
            request_kwargs_dict,
        )
        if headers_result.is_failure:
            return r[m.Api.HttpResponse].fail(
                headers_result.error or "Header extraction failed",
            )
        timeout_result = u.Api.RequestUtils.validate_and_extract_timeout(
            timeout,
            request_kwargs_dict,
        )
        if timeout_result.is_failure:
            return r[m.Api.HttpResponse].fail(
                timeout_result.error or "Timeout extraction failed",
            )
        query_params_result = self._extract_query_params(request_kwargs)
        if query_params_result.is_failure:
            return r[m.Api.HttpResponse].fail(
                query_params_result.error or "Query params extraction failed",
            )
        body_final = body_result.value
        http_request = m.Api.HttpRequest(
            method=method,
            url=url,
            body=body_final,
            headers=dict(headers_result.value),
            query_params=query_params_result.value,
            timeout=timeout_result.value,
        )
        return self.request(http_request)


__all__ = ["FlextApi"]

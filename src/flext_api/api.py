"""FLEXT API - Unified HTTP Facade.

Single entry point for all HTTP operations. Delegates to FlextApiClient for
actual HTTP work, to FlextApiModels for data validation. 100% GENERIC.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar, override

from pydantic import ConfigDict, PrivateAttr

from flext_api import FlextApiClient, FlextApiSettings, c, m, t, u
from flext_core import r, s


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
    _client: FlextApiClient | None = PrivateAttr(default=None)

    def __init__(
        self,
        *,
        config: FlextApiSettings | None = None,
    ) -> None:
        """Public zero-ceremony bootstrap for the API facade."""
        super().__init__(config=config)

    @classmethod
    @override
    def _get_service_config_type(cls) -> type[FlextApiSettings]:
        """Bind the API facade to FlextApiSettings by default."""
        return FlextApiSettings

    @property
    @override
    def settings(self) -> FlextApiSettings:
        """Return typed API settings for facade operations."""
        config = self.config
        if isinstance(config, FlextApiSettings):
            return config
        msg = "FlextApi runtime config must be FlextApiSettings"
        raise TypeError(msg)

    @property
    def client(self) -> FlextApiClient:
        """Return the lazily created HTTP client bound to this facade config."""
        client = self._client
        if client is None:
            client = FlextApiClient(config=self.settings)
            self._client = client
        return client

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
        """Execute s interface."""
        if kwargs:
            self.logger.info(f"Execute called with kwargs: {kwargs}")
        return r[FlextApiSettings].ok(self.settings)

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
        return self.client.request(request)

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
        return (
            u.Api.RequestUtils
            .build_request_payload(
                method=method,
                url=url,
                data=data,
                headers=headers,
                request_kwargs=request_kwargs,
                timeout=timeout,
            )
            .flat_map(lambda payload: u.load(m.Api.HttpRequest, payload))
            .flat_map(self.request)
        )


api = FlextApi

__all__ = ["FlextApi", "api"]

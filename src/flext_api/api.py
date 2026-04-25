"""FLEXT API - Unified HTTP Facade.

Single entry point for all HTTP operations. Delegates to FlextApiClient for
actual HTTP work, to FlextApiModels for data validation. 100% GENERIC.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar, override

from flext_core import FlextSettings, r, s

from flext_api import (
    FlextApiClient,
    FlextApiSettings,
    c,
    m,
    p,
    t,
    u,
)


class FlextApi(s[bool]):
    """Unified HTTP API facade - pure delegation pattern.

    Single responsibility: Delegate HTTP operations to FlextApiClient.
    All configuration through FlextApiSettings model.
    All data validation through FlextApiModels.
    100% GENERIC - no domain coupling.
    """

    model_config: ClassVar[m.ConfigDict] = m.ConfigDict(use_enum_values=True)
    _client: FlextApiClient | None = u.PrivateAttr(default_factory=lambda: None)

    def __init__(
        self,
        *,
        settings: FlextApiSettings | None = None,
    ) -> None:
        """Public bootstrap surface using the canonical ``settings=`` call form."""
        super().__init__()
        if settings is not None:
            self._settings = settings

    @property
    @override
    def settings(self) -> FlextApiSettings:
        """Return typed API settings for facade operations."""
        settings = super().settings
        if isinstance(settings, FlextApiSettings):
            return settings
        return FlextSettings.fetch_global().fetch_namespace("api", FlextApiSettings)

    @property
    def client(self) -> FlextApiClient:
        """Return the lazily created HTTP client bound to this facade settings."""
        client = self._client
        if client is None:
            client = FlextApiClient(settings=self.settings)
            self._client = client
        return client

    def delete(
        self,
        url: str,
        headers: t.StrMapping | None = None,
        request_kwargs: t.Api.RequestKwargs | None = None,
    ) -> p.Result[m.Api.HttpResponse]:
        """HTTP DELETE - delegates to generic method."""
        return self._http_method(
            method=c.Api.Method.DELETE,
            url=url,
            headers=headers,
            request_kwargs=request_kwargs,
        )

    def execute(
        self,
        **kwargs: t.Scalar,
    ) -> p.Result[bool]:
        """Execute s interface."""
        if kwargs:
            self.logger.info(f"Execute called with kwargs: {kwargs}")
        return r[bool].ok(True)

    def get(
        self,
        url: str,
        headers: t.StrMapping | None = None,
        request_kwargs: t.Api.RequestKwargs | None = None,
    ) -> p.Result[m.Api.HttpResponse]:
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
    ) -> p.Result[m.Api.HttpResponse]:
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
    ) -> p.Result[m.Api.HttpResponse]:
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
    ) -> p.Result[m.Api.HttpResponse]:
        """HTTP PUT - delegates to generic method."""
        return self._http_method(
            method=c.Api.Method.PUT,
            url=url,
            data=data,
            headers=headers,
            request_kwargs=request_kwargs,
        )

    def request(
        self,
        request: m.Api.HttpRequest,
    ) -> p.Result[m.Api.HttpResponse]:
        """Execute HTTP request - pure delegation to client.

        Args:
        request: HttpRequest model.

        Returns:
        r[HttpResponse]: Response or error.

        """
        return self.client.request(request)

    def _http_method(
        self,
        method: c.Api.Method | str,
        url: str,
        data: t.Api.RequestBody | None = None,
        headers: t.StrMapping | None = None,
        request_kwargs: t.Api.RequestKwargs | None = None,
        timeout: float | None = None,
    ) -> p.Result[m.Api.HttpResponse]:
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
            .flat_map(lambda payload: u.parse_model(payload.root, m.Api.HttpRequest))
            .flat_map(self.request)
        )


api = FlextApi()


__all__: list[str] = ["FlextApi", "api"]

"""FLEXT API - Unified HTTP Facade.

Single entry point for all HTTP operations. Delegates to FlextApiClient for
actual HTTP work, to FlextApiModels for data validation. 100% GENERIC.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar, override

from flext_api import c, m, p, r, s, t, u
from flext_api.services import FlextApiClient


class FlextApi(s[bool]):
    """Unified HTTP API facade - pure delegation pattern.

    Single responsibility: Delegate HTTP operations to FlextApiClient.
    All configuration through FlextApiSettings model.
    All data validation through FlextApiModels.
    100% GENERIC - no domain coupling.
    """

    model_config: ClassVar[m.ConfigDict] = m.ConfigDict(use_enum_values=True)
    _client: FlextApiClient | None = m.PrivateAttr(default_factory=lambda: None)

    @property
    def client(self) -> FlextApiClient:
        """The lazily created HTTP client bound to this facade settings."""
        client = self._client
        if client is None:
            client = FlextApiClient(runtime_settings=self.settings)
            self._client = client
        return client

    def delete(
        self,
        url: str,
        headers: t.StrMapping | None = None,
        request_kwargs: t.Api.RequestKwargs | None = None,
    ) -> p.Result[m.Api.HttpResponse]:
        """Perform an HTTP DELETE request through the generic client path.

        Args:
            url: Request URL.
            headers: Optional additional headers.
            request_kwargs: Optional transport kwargs merged into the request.

        Returns:
            Response payload or error result.

        """
        return self._http_method(
            method=c.Api.Method.DELETE,
            url=url,
            headers=headers,
            request_kwargs=request_kwargs,
        )

    @override
    def execute(self, **kwargs: t.Scalar) -> p.Result[bool]:
        """Execute the service lifecycle parity hook.

        Args:
            **kwargs: Optional execution context; logged when present.

        Returns:
            Successful ``True`` result.

        """
        if kwargs:
            self.logger.info("Execute called with kwargs: %s", kwargs)
        return r[bool].ok(value=True)

    def get(
        self,
        url: str,
        headers: t.StrMapping | None = None,
        request_kwargs: t.Api.RequestKwargs | None = None,
    ) -> p.Result[m.Api.HttpResponse]:
        """Perform an HTTP GET request through the generic client path.

        Args:
            url: Request URL.
            headers: Optional additional headers.
            request_kwargs: Optional transport kwargs merged into the request.

        Returns:
            Response payload or error result.

        """
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
        """Perform an HTTP PATCH request through the generic client path.

        Args:
            url: Request URL.
            data: Optional request body.
            headers: Optional additional headers.
            request_kwargs: Optional transport kwargs merged into the request.

        Returns:
            Response payload or error result.

        """
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
        """Perform an HTTP POST request through the generic client path.

        Args:
            url: Request URL.
            data: Optional request body.
            headers: Optional additional headers.
            request_kwargs: Optional transport kwargs merged into the request.

        Returns:
            Response payload or error result.

        """
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
        """Perform an HTTP PUT request through the generic client path.

        Args:
            url: Request URL.
            data: Optional request body.
            headers: Optional additional headers.
            request_kwargs: Optional transport kwargs merged into the request.

        Returns:
            Response payload or error result.

        """
        return self._http_method(
            method=c.Api.Method.PUT,
            url=url,
            data=data,
            headers=headers,
            request_kwargs=request_kwargs,
        )

    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        """Execute an HTTP request, delegating purely to the client.

        Args:
            request: Prepared HTTP request model.

        Returns:
            Response payload or error result.

        """
        return self.client.request(request)

    def _http_method(
        self,
        method: c.Api.Method | str,
        url: str,
        data: t.Api.RequestBody | None = None,
        headers: t.StrMapping | None = None,
        request_kwargs: t.Api.RequestKwargs | None = None,
    ) -> p.Result[m.Api.HttpResponse]:
        """Execute a generic HTTP method using monadic patterns, without fallbacks.

        Args:
            method: HTTP method (GET, POST, etc.).
            url: Request URL.
            data: Optional request body.
            headers: Optional additional headers.
            request_kwargs: Optional transport kwargs merged into the request.

        Returns:
            Response payload or error result.

        """
        chain: p.Result[m.Api.HttpResponse] = (
            u.Api.RequestUtils
            .build_request_payload(
                method=method,
                url=url,
                data=data,
                headers=headers,
                request_kwargs=request_kwargs,
            )
            .flat_map(lambda payload: u.parse_model(payload.root, m.Api.HttpRequest))
            .flat_map(self.request)
        )
        return chain


api: FlextApi = FlextApi.fetch_global()
"""Global FlextApi facade instance used as the canonical runtime entrypoint."""


__all__: t.MutableSequenceOf[str] = ["FlextApi", "api"]

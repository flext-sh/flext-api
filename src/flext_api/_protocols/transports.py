"""FLEXT API Transports - Transport layer implementations.

This module provides transport implementations for different communication protocols
including HTTP, WebSocket, SSE, GraphQL, and gRPC. All transports follow FLEXT patterns
with proper error handling and Result types.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING, override

import httpx

from flext_api.constants import c
from flext_api.models import m
from flext_api.typings import t
from flext_core import r

from ._transports_config import FlextApiTransportsConfigMixin
from ._transports_request import FlextApiTransportsRequestMixin
from .base import FlextApiProtocolsBase as pb

if TYPE_CHECKING:
    from flext_web import p


class FlextApiProtocolsTransports:
    """FLEXT API transport implementations."""

    # Why: no member here carries @abstractmethod (TransportPlugin's Protocol
    # bodies are structural, not abstract), so an explicit ABC base added
    # nothing but tripped pyrefly's direct-abstract-base-instantiation check
    # on the concrete `FlextWebTransport()` construction in tests.
    class FlextWebTransport(
        FlextApiTransportsConfigMixin,
        FlextApiTransportsRequestMixin,
        pb.TransportPlugin,
    ):
        """HTTP transport implementation using httpx."""

        def __init__(self) -> None:
            """Initialize HTTP transport."""
            self._client: httpx.Client | None = None

        @override
        def connect(self, url: str, **options: t.JsonValue) -> p.Result[str]:
            """Connect to HTTP endpoint."""
            if not url:
                return r[str].fail("URL is required for HTTP connection")
            timeout = self._client_timeout(options)
            follow_redirects = self._client_follow_redirects(options)
            max_redirects = self._client_max_redirects(options)
            try:
                self._client = httpx.Client(
                    timeout=timeout,
                    follow_redirects=follow_redirects,
                    max_redirects=max_redirects,
                )
            except c.Api.EXC_HTTPX as e:
                return r[str].fail_op("HTTP connect", e)
            return r[str].ok(url)

        @override
        def disconnect(self, connection: str) -> p.Result[bool]:
            """Disconnect HTTP connection."""
            try:
                _ = connection
                if self._client is not None:
                    self._client.close()
                self._client = None
                return r[bool].ok(value=True)
            except c.Api.EXC_HTTPX as e:
                return r[bool].fail_op("HTTP disconnect", e)

        @override
        def send(
            self, connection: str, data: t.JsonMapping | t.Api.RequestBody
        ) -> p.Result[t.Api.HttpResponseDict | str]:
            """Send HTTP request."""
            params_result = self._extract_request_params(
                data, connection_url=connection
            )
            if params_result.failure:
                return r[t.Api.HttpResponseDict | str].from_failure(params_result)
            response_result = self._request_model(params_result.value)
            if response_result.failure:
                return r[t.Api.HttpResponseDict | str].from_failure(response_result)
            return r[t.Api.HttpResponseDict | str].ok(
                self._response_mapping(response_result.value)
            )

        def request_model(
            self, request: m.Api.HttpRequest
        ) -> p.Result[m.Api.HttpResponse]:
            """Public wrapper around request-model execution for protocol consumers."""
            return self._request_model(request)


__all__: list[str] = ["FlextApiProtocolsTransports"]

"""FLEXT API transports service namespace: concrete HTTP transport behavior.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import override

import httpx

from flext_api.constants import c
from flext_api.protocols import p
from flext_api.typings import t
from flext_core import r

from .._services._transports_config import FlextApiTransportsConfigMixin
from .._services._transports_request import FlextApiTransportsRequestMixin


class FlextApiServicesTransports:
    """Concrete transport implementations owned by the services layer."""

    # Why: no member here carries @abstractmethod (TransportPlugin's Protocol
    # bodies are structural, not abstract), so an explicit ABC base added
    # nothing but tripped pyrefly's direct-abstract-base-instantiation check
    # on the concrete `FlextWebTransport()` construction in tests.
    class FlextWebTransport(
        FlextApiTransportsConfigMixin,
        FlextApiTransportsRequestMixin,
        p.FlextApiProtocolsTransport.TransportPlugin,
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
            """Disconnect from HTTP endpoint."""
            if self._client is None:
                return r[bool].fail("Not connected")
            self._client.close()
            self._client = None
            return r[bool].ok(True)

        @override
        def send(
            self, connection: str, data: t.Api.RequestBody
        ) -> p.Result[t.Api.HttpResponseDict | str]:
            """Send data over HTTP."""
            if self._client is None:
                return r[t.Api.HttpResponseDict | str].fail("Not connected")
            try:
                response = self._client.post(connection, json=data)
                response.raise_for_status()
                return r[t.Api.HttpResponseDict | str].ok(
                    {"status_code": response.status_code, "body": response.text}
                )
            except c.Api.EXC_HTTPX as e:
                return r[t.Api.HttpResponseDict | str].fail_op("HTTP send", e)

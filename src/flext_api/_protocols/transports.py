"""FLEXT API Transports - Transport layer implementations.

This module provides transport implementations for different communication protocols
including HTTP, WebSocket, SSE, GraphQL, and gRPC. All transports follow FLEXT patterns
with proper error handling and Result types.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import override

import httpx
from flext_core import r

from flext_api import c, m, p, t


class FlextApiTransports:
    """FLEXT API transport implementations."""

    class FlextWebTransport(p.Api.Transport.TransportPlugin):
        """HTTP transport implementation using httpx."""

        def __init__(self) -> None:
            """Initialize HTTP transport."""
            self._client: httpx.Client | None = None

        @property
        def client(self) -> httpx.Client | None:
            """Expose the active HTTP client instance."""
            return self._client

        @override
        def connect(self, url: str, **options: t.ApiJsonValue) -> r[str]:
            """Connect to HTTP endpoint."""
            try:
                if not url:
                    return r[str].fail("URL is required for HTTP connection")
                _ = options
                self._client = httpx.Client()
                return r[str].ok(url)
            except (
                ValueError,
                TypeError,
                KeyError,
                httpx.HTTPError,
                ConnectionError,
            ) as e:
                return r[str].fail(f"HTTP connect failed: {e}")

        @override
        def disconnect(self, connection: str) -> r[bool]:
            """Disconnect HTTP connection."""
            try:
                _ = connection
                if self._client is not None:
                    self._client.close()
                self._client = None
                return r[bool].ok(value=True)
            except (
                ValueError,
                TypeError,
                KeyError,
                httpx.HTTPError,
                ConnectionError,
            ) as e:
                return r[bool].fail(f"HTTP disconnect failed: {e}")

        @override
        def send(
            self,
            connection: str,
            data: t.Api.RequestConfig | t.Api.RequestBody,
        ) -> r[t.Api.HttpResponseDict | str]:
            """Send HTTP request."""
            try:
                _ = connection
                client = self._client
                if client is None:
                    return r[t.Api.HttpResponseDict | str].fail(
                        "HTTP client is not connected",
                    )
                params_result = self._extract_request_params(
                    data,
                    connection_url=connection,
                )
                if params_result.is_failure:
                    return r[t.Api.HttpResponseDict | str].fail(
                        params_result.error or "Parameter extraction failed",
                    )
                request_model = params_result.value
                match request_model.body:
                    case dict() as body_json:
                        response = client.request(
                            method=str(request_model.method),
                            url=request_model.url,
                            headers=request_model.headers,
                            json=body_json,
                        )
                    case str() as body_text:
                        response = client.request(
                            method=str(request_model.method),
                            url=request_model.url,
                            headers=request_model.headers,
                            content=body_text,
                        )
                    case bytes() as body_bytes:
                        response = client.request(
                            method=str(request_model.method),
                            url=request_model.url,
                            headers=request_model.headers,
                            content=body_bytes,
                        )
                    case _:
                        return r[t.Api.HttpResponseDict | str].fail(
                            "Unsupported HTTP request body type",
                        )
                return r[t.Api.HttpResponseDict | str].ok({
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "content": response.content,
                    "text": response.text,
                    "url": str(response.url),
                })
            except (
                ValueError,
                TypeError,
                KeyError,
                httpx.HTTPError,
                ConnectionError,
            ) as e:
                return r[t.Api.HttpResponseDict | str].fail(f"HTTP send failed: {e}")

        def _extract_request_params(
            self,
            data: t.Api.RequestConfig | t.Api.RequestBody,
            *,
            connection_url: str,
        ) -> r[m.Api.HttpRequest]:
            """Extract and validate request parameters from data."""
            try:
                match data:
                    case dict() as payload:
                        request_model = m.Api.HttpRequest.model_validate(payload)
                    case str() as body_text:
                        request_model = m.Api.HttpRequest(
                            method=c.Api.Method.GET,
                            url=connection_url,
                            body=body_text,
                            headers={},
                            query_params={},
                            timeout=float(c.Api.DEFAULT_TIMEOUT),
                        )
                    case bytes() as body_bytes:
                        request_model = m.Api.HttpRequest(
                            method=c.Api.Method.GET,
                            url=connection_url,
                            body=body_bytes,
                            headers={},
                            query_params={},
                            timeout=float(c.Api.DEFAULT_TIMEOUT),
                        )
                    case _:
                        return r[m.Api.HttpRequest].fail(
                            "Unsupported HTTP request payload type",
                        )
                return r[m.Api.HttpRequest].ok(request_model)
            except (
                ValueError,
                TypeError,
                KeyError,
                httpx.HTTPError,
                ConnectionError,
            ) as e:
                return r[m.Api.HttpRequest].fail(f"Invalid HTTP request payload: {e}")


__all__ = ["FlextApiTransports"]

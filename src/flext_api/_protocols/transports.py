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

from flext_api import c, m, p, r, t


class FlextApiTransports:
    """FLEXT API transport implementations."""

    class FlextWebTransport(p.Api.Transport.TransportPlugin):
        """HTTP transport implementation using httpx."""

        def __init__(self) -> None:
            """Initialize HTTP transport."""
            self._client: httpx.Client | None = None

        @override
        def connect(self, url: str, **options: t.ApiJsonValue) -> p.Result[str]:
            """Connect to HTTP endpoint."""
            try:
                if not url:
                    return r[str].fail("URL is required for HTTP connection")
                raw_timeout = options.get("timeout")
                timeout = (
                    float(raw_timeout)
                    if isinstance(raw_timeout, (int, float))
                    else float(c.Api.DEFAULT_TIMEOUT)
                )
                raw_follow_redirects = options.get("follow_redirects")
                follow_redirects = (
                    raw_follow_redirects
                    if isinstance(raw_follow_redirects, bool)
                    else True
                )
                raw_max_redirects = options.get("max_redirects")
                max_redirects = (
                    raw_max_redirects if isinstance(raw_max_redirects, int) else 20
                )
                self._client = httpx.Client(
                    timeout=timeout,
                    follow_redirects=follow_redirects,
                    max_redirects=max_redirects,
                )
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
        def disconnect(self, connection: str) -> p.Result[bool]:
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
            data: t.ContainerValueMapping | t.Api.RequestBody,
        ) -> p.Result[t.Api.HttpResponseDict | str]:
            """Send HTTP request."""
            params_result = self._extract_request_params(
                data,
                connection_url=connection,
            )
            if params_result.failure:
                return r[t.Api.HttpResponseDict | str].fail(
                    params_result.error or "Parameter extraction failed",
                )
            response_result = self._request_model(params_result.value)
            if response_result.failure:
                return r[t.Api.HttpResponseDict | str].fail(
                    response_result.error or "HTTP send failed",
                )
            return r[t.Api.HttpResponseDict | str].ok(
                self._response_mapping(response_result.value),
            )

        def _extract_request_params(
            self,
            data: t.ContainerValueMapping | t.Api.RequestBody,
            *,
            connection_url: str,
        ) -> p.Result[m.Api.HttpRequest]:
            """Extract and validate request parameters from data."""
            try:
                match data:
                    case dict() as payload:
                        request_model = m.Api.HttpRequest.model_validate(
                            {"url": connection_url, **payload},
                        )
                    case str() | bytes():
                        request_model = m.Api.HttpRequest.model_validate({
                            "url": connection_url,
                            "body": data,
                        })
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

        def _request_model(
            self,
            request: m.Api.HttpRequest,
        ) -> p.Result[m.Api.HttpResponse]:
            """Execute one validated HTTP request model through the active transport."""
            try:
                client = self._client
                if client is None:
                    return r[m.Api.HttpResponse].fail("HTTP client is not connected")
                match request.body:
                    case dict() as body_json:
                        response = client.request(
                            method=request.method,
                            url=request.url,
                            headers=request.headers,
                            params=request.query_params,
                            json=body_json,
                            timeout=request.timeout,
                        )
                    case str() as body_text:
                        response = client.request(
                            method=request.method,
                            url=request.url,
                            headers=request.headers,
                            params=request.query_params,
                            content=body_text,
                            timeout=request.timeout,
                        )
                    case bytes() as body_bytes:
                        response = client.request(
                            method=request.method,
                            url=request.url,
                            headers=request.headers,
                            params=request.query_params,
                            content=body_bytes,
                            timeout=request.timeout,
                        )
                    case _:
                        return r[m.Api.HttpResponse].fail(
                            "Unsupported HTTP request body type",
                        )
                return r[m.Api.HttpResponse].ok(self._response_model(response))
            except (
                ValueError,
                TypeError,
                KeyError,
                httpx.HTTPError,
                ConnectionError,
            ) as e:
                return r[m.Api.HttpResponse].fail(f"HTTP request failed: {e}")

        def request_model(
            self,
            request: m.Api.HttpRequest,
        ) -> p.Result[m.Api.HttpResponse]:
            """Public wrapper around request-model execution for protocol consumers."""
            return self._request_model(request)

        @staticmethod
        def _response_model(response: httpx.Response) -> m.Api.HttpResponse:
            """Convert the concrete httpx response into the central API response model."""
            return m.Api.create_response(
                status_code=response.status_code,
                body=response.content,
                headers=dict(response.headers),
                request_id="",
            )

        @staticmethod
        def _response_mapping(response: m.Api.HttpResponse) -> t.Api.HttpResponseDict:
            """Convert the central response model to the public mapping contract."""
            return {
                "status_code": response.status_code,
                "headers": response.headers,
                "body": response.body,
                "request_id": response.request_id,
            }


__all__: list[str] = ["FlextApiTransports"]

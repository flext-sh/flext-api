"""FLEXT API Transports - Transport layer implementations.

This module provides transport implementations for different communication protocols
including HTTP, WebSocket, SSE, GraphQL, and gRPC. All transports follow FLEXT patterns
with proper error handling and Result types.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from abc import ABC
from typing import override

import httpx

from flext_api import c, m, r, t
from flext_api._protocols.base import FlextApiProtocolsBase as pb
from flext_web import p


class FlextApiProtocolsTransports:
    """FLEXT API transport implementations."""

    class FlextWebTransport(pb.TransportPlugin, ABC):
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

        @staticmethod
        def _client_timeout(options: t.MappingKV[str, t.JsonValue]) -> float:
            """Resolve the httpx timeout option from validated scalar inputs."""
            raw_timeout = options.get("timeout")
            return (
                float(raw_timeout)
                if isinstance(raw_timeout, t.NUMERIC_TYPES)
                else c.Api.DEFAULT_TIMEOUT
            )

        @staticmethod
        def _client_follow_redirects(options: t.MappingKV[str, t.JsonValue]) -> bool:
            """Resolve the httpx follow-redirects option."""
            raw_follow_redirects = options.get("follow_redirects")
            return (
                raw_follow_redirects if isinstance(raw_follow_redirects, bool) else True
            )

        @staticmethod
        def _client_max_redirects(options: t.MappingKV[str, t.JsonValue]) -> int:
            """Resolve the httpx maximum redirects option."""
            raw_max_redirects = options.get("max_redirects")
            return raw_max_redirects if isinstance(raw_max_redirects, int) else 20

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
            self,
            connection: str,
            data: t.JsonMapping | t.Api.RequestBody,
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
            data: t.JsonMapping | t.Api.RequestBody,
            *,
            connection_url: str,
        ) -> p.Result[m.Api.HttpRequest]:
            """Extract and validate request parameters from data."""
            payload_result = self._request_payload(data, connection_url=connection_url)
            if payload_result.failure:
                return r[m.Api.HttpRequest].fail(
                    payload_result.error or "Unsupported HTTP request payload type",
                )
            try:
                request_model = m.Api.HttpRequest.model_validate(payload_result.value)
            except c.Api.EXC_HTTPX as e:
                return r[m.Api.HttpRequest].fail(f"Invalid HTTP request payload: {e}")
            return r[m.Api.HttpRequest].ok(request_model)

        @staticmethod
        def _request_payload(
            data: t.JsonMapping | t.Api.RequestBody,
            *,
            connection_url: str,
        ) -> p.Result[t.MappingKV[str, t.Api.RequestBody | t.JsonValue]]:
            """Build the Pydantic request payload from supported transport inputs."""
            match data:
                case dict() as payload:
                    request_payload: t.MappingKV[
                        str, t.Api.RequestBody | t.JsonValue
                    ] = {
                        "url": connection_url,
                        **payload,
                    }
                case str() | bytes():
                    request_payload = {
                        "url": connection_url,
                        "body": data,
                    }
                case _:
                    return r[t.MappingKV[str, t.Api.RequestBody | t.JsonValue]].fail(
                        "Unsupported HTTP request payload type",
                    )
            return r[t.MappingKV[str, t.Api.RequestBody | t.JsonValue]].ok(
                request_payload,
            )

        def _request_model(
            self,
            request: m.Api.HttpRequest,
        ) -> p.Result[m.Api.HttpResponse]:
            """Execute one validated HTTP request model through the active transport."""
            client = self._client
            if client is None:
                return r[m.Api.HttpResponse].fail("HTTP client is not connected")
            response_result = self._httpx_response(client, request)
            if response_result.failure:
                return r[m.Api.HttpResponse].fail(
                    response_result.error or "HTTP request failed",
                )
            return r[m.Api.HttpResponse].ok(
                self._response_model(response_result.value),
            )

        def _httpx_response(
            self,
            client: httpx.Client,
            request: m.Api.HttpRequest,
        ) -> p.Result[httpx.Response]:
            """Dispatch one request body shape to httpx."""
            match request.body:
                case dict() as body_json:
                    return self._request_json_body(client, request, body_json)
                case str() as body_text:
                    return self._request_content_body(client, request, body_text)
                case bytes() as body_bytes:
                    return self._request_content_body(client, request, body_bytes)
                case _:
                    return r[httpx.Response].fail(
                        "Unsupported HTTP request body type",
                    )

        @staticmethod
        def _request_json_body(
            client: httpx.Client,
            request: m.Api.HttpRequest,
            body_json: t.JsonMapping,
        ) -> p.Result[httpx.Response]:
            """Execute an HTTP request with JSON body semantics."""
            try:
                response = client.request(
                    method=request.method,
                    url=request.url,
                    headers=request.headers,
                    params=request.query_params,
                    json=body_json,
                    timeout=request.timeout,
                )
            except c.Api.EXC_HTTPX as e:
                return r[httpx.Response].fail_op("HTTP request", e)
            return r[httpx.Response].ok(response)

        @staticmethod
        def _request_content_body(
            client: httpx.Client,
            request: m.Api.HttpRequest,
            body_content: str | bytes,
        ) -> p.Result[httpx.Response]:
            """Execute an HTTP request with raw content body semantics."""
            try:
                response = client.request(
                    method=request.method,
                    url=request.url,
                    headers=request.headers,
                    params=request.query_params,
                    content=body_content,
                    timeout=request.timeout,
                )
            except c.Api.EXC_HTTPX as e:
                return r[httpx.Response].fail_op("HTTP request", e)
            return r[httpx.Response].ok(response)

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


__all__: list[str] = ["FlextApiProtocolsTransports"]

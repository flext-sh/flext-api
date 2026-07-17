"""HTTP transport request-pipeline mixin.

Behavior-preserving MRO shard for :class:`FlextWebTransport`. Owns request
parameter extraction, payload construction, and httpx dispatch.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import httpx

from typing import TYPE_CHECKING

from flext_api.constants import FlextApiConstants as c
from flext_api.models import FlextApiModels as m
from flext_api.typings import FlextApiTypes as t
from flext_core import r

if TYPE_CHECKING:
    from flext_api import p


class FlextApiTransportsRequestMixin:
    """Request extraction, payload building, and httpx dispatch."""

    _client: httpx.Client | None

    def _extract_request_params(
        self, data: t.JsonMapping | t.Api.RequestBody, *, connection_url: str
    ) -> p.Result[p.Api.HttpRequest]:
        """Extract and validate request parameters from data."""
        payload_result = self._request_payload(data, connection_url=connection_url)
        if payload_result.failure:
            return r[m.Api.HttpRequest].fail(
                payload_result.error or "Unsupported HTTP request payload type"
            )
        try:
            request_model = m.Api.HttpRequest.model_validate(payload_result.value)
        except c.Api.EXC_HTTPX as e:
            return r[m.Api.HttpRequest].fail(f"Invalid HTTP request payload: {e}")
        return r[m.Api.HttpRequest].ok(request_model)

    @staticmethod
    def _request_payload(
        data: t.JsonMapping | t.Api.RequestBody, *, connection_url: str
    ) -> p.Result[t.MappingKV[str, t.Api.RequestBody | t.JsonValue]]:
        """Build the Pydantic request payload from supported transport inputs."""
        match data:
            case dict() as payload:
                request_payload: t.MappingKV[str, t.Api.RequestBody | t.JsonValue] = {
                    "url": connection_url,
                    **payload,
                }
            case str() | bytes():
                request_payload = {"url": connection_url, "body": data}
            case _:
                return r[t.MappingKV[str, t.Api.RequestBody | t.JsonValue]].fail(
                    "Unsupported HTTP request payload type"
                )
        return r[t.MappingKV[str, t.Api.RequestBody | t.JsonValue]].ok(request_payload)

    def _request_model(
        self, request: p.Api.HttpRequest
    ) -> p.Result[p.Api.HttpResponse]:
        """Execute one validated HTTP request model through the active transport."""
        client = self._client
        if client is None:
            return r[m.Api.HttpResponse].fail("HTTP client is not connected")
        response_result = self._httpx_response(client, request)
        if response_result.failure:
            return r[m.Api.HttpResponse].fail(
                response_result.error or "HTTP request failed"
            )
        return r[m.Api.HttpResponse].ok(self._response_model(response_result.value))

    def _httpx_response(
        self, client: httpx.Client, request: p.Api.HttpRequest
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
                return r[httpx.Response].fail("Unsupported HTTP request body type")

    @staticmethod
    def _request_json_body(
        client: httpx.Client, request: p.Api.HttpRequest, body_json: t.JsonMapping
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
        client: httpx.Client, request: p.Api.HttpRequest, body_content: str | bytes
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

    @staticmethod
    def _response_model(response: httpx.Response) -> p.Api.HttpResponse:
        """Convert the concrete httpx response into the central API response model."""
        return m.Api.create_response(
            status_code=response.status_code,
            body=response.content,
            headers=dict(response.headers),
            request_id="",
        )


__all__: list[str] = ["FlextApiTransportsRequestMixin"]

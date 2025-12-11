"""FLEXT API Transports - Transport layer implementations.

This module provides transport implementations for different communication protocols
including HTTP, WebSocket, SSE, GraphQL, and gRPC. All transports follow FLEXT patterns
with proper error handling and Result types.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Protocol

import httpx
from flext_core import r

from flext_api.constants import c


class TransportPlugin(Protocol):
    """Protocol for transport plugins."""

    def connect(self, url: str, **options: object) -> r[object]:
        """Connect to endpoint."""
        ...

    def disconnect(self, connection: object) -> r[bool]:
        """Disconnect from endpoint."""
        ...

    def send(self, connection: object, data: object) -> r[object]:
        """Send data through connection."""
        ...


class FlextApiTransports:
    """FLEXT API transport implementations."""

    class FlextWebTransport(TransportPlugin):
        """HTTP transport implementation using httpx."""

        def __init__(self) -> None:
            """Initialize HTTP transport."""
            self._client: httpx.Client | None = None

        def connect(self, url: str, **options: object) -> r[object]:
            """Connect to HTTP endpoint."""
            try:
                # Validate URL parameter
                if not url:
                    return r[object].fail("URL is required for HTTP connection")

                # Create a basic httpx client - options can be used by subclasses
                # The url parameter is validated but not directly used in client creation
                # as httpx.Client doesn't take a base URL in connect()
                # Options parameter is reserved for future extensibility
                _ = options  # Reserved for future use
                self._client = httpx.Client()
                return r[object].ok(self._client)
            except Exception as e:
                return r[object].fail(f"HTTP connect failed: {e}")

        def disconnect(self, connection: object) -> r[bool]:
            """Disconnect HTTP connection."""
            try:
                if isinstance(connection, httpx.Client):
                    connection.close()
                self._client = None
                return r[bool].ok(True)
            except Exception as e:
                return r[bool].fail(f"HTTP disconnect failed: {e}")

        def _extract_request_params(
            self,
            data: dict[str, object],
        ) -> r[tuple[str, str, dict[str, str], object, object, object]]:
            """Extract and validate request parameters from data."""
            method_str: str = c.Api.Method.GET
            if "method" in data:
                method_value = data["method"]
                if isinstance(method_value, str):
                    method_str = method_value

            if "url" not in data:
                return r[tuple[str, str, dict[str, str], object, object, object]].fail(
                    "URL is required for HTTP request",
                )

            url_value = data["url"]
            if not isinstance(url_value, str) or not url_value:
                return r[tuple[str, str, dict[str, str], object, object, object]].fail(
                    "URL must be a non-empty string",
                )

            url: str = url_value

            headers: dict[str, str] = {}
            if "headers" in data:
                headers_value = data["headers"]
                if isinstance(headers_value, dict):
                    headers = headers_value

            params = None
            if "params" in data:
                params = data["params"]

            json_data = None
            if "json" in data:
                json_data = data["json"]

            content = None
            if "content" in data:
                content = data["content"]

            return r[tuple[str, str, dict[str, str], object, object, object]].ok((
                method_str,
                url,
                headers,
                params,
                json_data,
                content,
            ))

        def send(self, connection: object, data: object) -> r[object]:
            """Send HTTP request."""
            try:
                if not isinstance(connection, httpx.Client):
                    return r[object].fail("Connection must be an httpx.Client")

                if not isinstance(data, dict):
                    return r[object].fail("HTTP send data must be a dict")

                params_result = self._extract_request_params(data)
                if params_result.is_failure:
                    return r[object].fail(
                        params_result.error or "Parameter extraction failed",
                    )

                method_str, url, headers, params, json_data, content = (
                    params_result.value
                )

                # Make the request with explicit parameter passing
                # httpx.request requires specific types, so we pass parameters directly
                if params is not None and isinstance(params, dict):
                    if json_data is not None:
                        response = connection.request(
                            method=method_str,
                            url=url,
                            headers=headers,
                            params=params,
                            json=json_data,
                        )
                    elif content is not None and isinstance(content, (str, bytes)):
                        response = connection.request(
                            method=method_str,
                            url=url,
                            headers=headers,
                            params=params,
                            content=content,
                        )
                    else:
                        response = connection.request(
                            method=method_str,
                            url=url,
                            headers=headers,
                            params=params,
                        )
                elif json_data is not None:
                    response = connection.request(
                        method=method_str,
                        url=url,
                        headers=headers,
                        json=json_data,
                    )
                elif content is not None and isinstance(content, (str, bytes)):
                    response = connection.request(
                        method=method_str,
                        url=url,
                        headers=headers,
                        content=content,
                    )
                else:
                    response = connection.request(
                        method=method_str,
                        url=url,
                        headers=headers,
                    )

                # Return response data
                return r[object].ok({
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "content": response.content,
                    "text": response.text,
                    "url": str(response.url),
                })
            except Exception as e:
                return r[object].fail(f"HTTP send failed: {e}")

    class WebSocketTransport(TransportPlugin):
        """WebSocket transport implementation."""

        def connect(self, url: str, **_options: object) -> r[object]:
            """Connect to WebSocket endpoint."""
            # Parameter validation for future implementation
            if not url:
                return r[object].fail("WebSocket URL is required")
            # options parameter is reserved for future WebSocket connection options (e.g., headers, protocols)
            _ = _options  # Reserved for future use
            return r[object].fail("WebSocket transport not implemented (Phase 3)")

        def disconnect(self, connection: object) -> r[bool]:
            """Disconnect WebSocket."""
            # Parameter validation for future implementation
            if connection is None:
                return r[bool].fail("Connection object is required")
            return r[bool].fail("WebSocket transport not implemented (Phase 3)")

        def send(self, connection: object, data: object) -> r[object]:
            """Send WebSocket message."""
            # Parameter validation for future implementation
            if connection is None:
                return r[object].fail("Connection object is required")
            if data is None:
                return r[object].fail("Data is required")
            return r[object].fail("WebSocket transport not implemented (Phase 3)")

    class SseTransport(TransportPlugin):
        """Server-Sent Events transport implementation."""

        def connect(self, url: str, **_options: object) -> r[object]:
            """Connect to SSE endpoint."""
            # Parameter validation for future implementation
            if not url:
                return r[object].fail("SSE URL is required")
            # options parameter is reserved for future SSE connection options (e.g., headers, reconnect settings)
            _ = _options  # Reserved for future use
            return r[object].fail("SSE transport not implemented (Phase 3)")

        def disconnect(self, connection: object) -> r[bool]:
            """Disconnect SSE."""
            # Parameter validation for future implementation
            if connection is None:
                return r[bool].fail("Connection object is required")
            return r[bool].fail("SSE transport not implemented (Phase 3)")

        def send(self, connection: object, data: object) -> r[object]:
            """Send SSE data."""
            # Parameter validation for future implementation
            if connection is None:
                return r[object].fail("Connection object is required")
            if data is None:
                return r[object].fail("Data is required")
            return r[object].fail("SSE transport not implemented (Phase 3)")

    class GraphQLTransport(TransportPlugin):
        """GraphQL transport implementation."""

        def connect(self, url: str, **_options: object) -> r[object]:
            """Connect to GraphQL endpoint."""
            # Parameter validation for future implementation
            if not url:
                return r[object].fail("GraphQL URL is required")
            # options parameter is reserved for future GraphQL connection options (e.g., headers, schema)
            _ = _options  # Reserved for future use
            return r[object].fail("GraphQL transport not implemented (Phase 3)")

        def disconnect(self, connection: object) -> r[bool]:
            """Disconnect GraphQL."""
            # Parameter validation for future implementation
            if connection is None:
                return r[bool].fail("Connection object is required")
            return r[bool].fail("GraphQL transport not implemented (Phase 3)")

        def send(self, connection: object, data: object) -> r[object]:
            """Send GraphQL query."""
            # Parameter validation for future implementation
            if connection is None:
                return r[object].fail("Connection object is required")
            if data is None:
                return r[object].fail("Query data is required")
            return r[object].fail("GraphQL transport not implemented (Phase 3)")

    class GrpcTransport(TransportPlugin):
        """gRPC transport implementation."""

        def connect(self, url: str, **_options: object) -> r[object]:
            """Connect to gRPC service."""
            # Parameter validation for future implementation
            if not url:
                return r[object].fail("gRPC URL is required")
            # options parameter is used for future gRPC connection options
            return r[object].fail("gRPC transport not implemented (Phase 3)")

        def disconnect(self, connection: object) -> r[bool]:
            """Disconnect gRPC."""
            # Parameter validation for future implementation
            if connection is None:
                return r[bool].fail("Connection object is required")
            return r[bool].fail("gRPC transport not implemented (Phase 3)")

        def send(self, connection: object, data: object) -> r[object]:
            """Send gRPC request."""
            # Parameter validation for future implementation
            if connection is None:
                return r[object].fail("Connection object is required")
            if data is None:
                return r[object].fail("Request data is required")
            return r[object].fail("gRPC transport not implemented (Phase 3)")


__all__ = [
    "FlextApiTransports",
    "TransportPlugin",
]

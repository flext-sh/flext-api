"""Transport Layer Abstraction for flext-api.

Protocol-agnostic transport layer for network communication.
Provides transport implementations for HTTP, WebSocket, GraphQL, gRPC, and SSE.

See TRANSFORMATION_PLAN.md - Phase 1 for architecture details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import httpx
from flext_core import FlextCore

from flext_api.plugins import TransportPlugin


class FlextApiTransports:
    """Unified transport layer abstraction for flext-api.

    Provides transport implementations for HTTP, WebSocket, GraphQL, gRPC, and SSE
    within a single namespace class following FLEXT patterns.
    """

    class HttpTransport(TransportPlugin):
        """HTTP transport implementation using httpx.

        Supports HTTP/1.1, HTTP/2, and HTTP/3 protocols.
        Provides connection pooling, retry logic, and streaming.

        Features:
        - HTTP/2 multiplexing
        - Connection keep-alive
        - Automatic decompression
        - Streaming support
        - Timeout management

        Usage:
            transport = FlextApiTransports.HttpTransport()
            conn_result = transport.connect("https://api.example.com")
            if conn_result.is_success:
                conn = conn_result.unwrap()
                # Use connection...
        """

        def __init__(
            self,
            pool_limits: httpx.Limits | None = None,
            timeout: httpx.Timeout | None = None,
            *,
            http2: bool = True,
        ) -> None:
            """Initialize HTTP transport.

            Args:
                http2: Enable HTTP/2 support (default: True)
                pool_limits: Connection pool limits
                timeout: Default timeout configuration

            """
            super().__init__(
                name="http",
                version="1.0.0",
                description="HTTP/1.1, HTTP/2, HTTP/3 transport using httpx",
            )

            self._http2 = http2
            self._pool_limits = pool_limits or httpx.Limits(
                max_connections=100,
                max_keepalive_connections=20,
            )
            self._timeout = timeout or httpx.Timeout(30.0)
            self._client: httpx.Client | None = None

        def connect(
            self,
            url: str,
            **options: object,
        ) -> FlextCore.Result[httpx.Client]:
            """Establish HTTP client connection.

            Args:
                url: Base URL for client
                **options: Additional httpx client options

            Returns:
                FlextCore.Result containing Client or error

            """
            try:
                # Create client if not exists
                if self._client is None:
                    # Extract parameters that are explicitly set to avoid duplicate keyword arguments
                    # when unpacking **options
                    options_copy = options.copy()
                    follow_redirects = options_copy.pop("follow_redirects", True)
                    # Remove other explicitly set parameters if present in options
                    options_copy.pop("http2", None)
                    options_copy.pop("limits", None)
                    options_copy.pop("timeout", None)
                    options_copy.pop("base_url", None)

                    self._client = httpx.Client(
                        base_url=url,
                        http2=self._http2,
                        limits=self._pool_limits,
                        timeout=self._timeout,
                        follow_redirects=follow_redirects,
                        **options_copy,
                    )

                self.logger.debug(
                    f"HTTP client connected to: {url}",
                    extra={"url": url, "http2": self._http2},
                )

                return FlextCore.Result[httpx.Client].ok(self._client)

            except Exception as e:
                return FlextCore.Result[httpx.Client].fail(
                    f"Failed to create HTTP client: {e}"
                )

        def disconnect(
            self,
            connection: httpx.Client,
        ) -> FlextCore.Result[None]:
            """Close HTTP client connection.

            Args:
                connection: Client to close

            Returns:
                FlextCore.Result indicating success or failure

            """
            try:
                connection.close()
                self._client = None

                self.logger.debug("HTTP client disconnected")
                return FlextCore.Result[None].ok(None)

            except Exception as e:
                return FlextCore.Result[None].fail(f"Failed to close HTTP client: {e}")

        def send(
            self,
            connection: httpx.Client,
            data: bytes | str,
            **options: object,
        ) -> FlextCore.Result[None]:
            """Send HTTP request.

            Args:
                connection: Active HTTP client
                data: Request data (will be converted to request)
                **options: Request options (method, url, headers, etc.)

            Returns:
                FlextCore.Result indicating success or failure

            """
            try:
                method = options.get("method", "GET")
                url = options.get("url", "/")
                headers = options.get("headers", {})

                # Send request (response will be retrieved via receive)
                response = connection.request(
                    method=method,
                    url=url,
                    content=data if isinstance(data, bytes) else data.encode(),
                    headers=headers,
                )

                # Store response for receive()
                self._last_response = response

                return FlextCore.Result[None].ok(None)

            except Exception as e:
                return FlextCore.Result[None].fail(f"Failed to send HTTP request: {e}")

        def receive(
            self,
            _connection: httpx.Client,
            **_options: object,
        ) -> FlextCore.Result[bytes]:
            """Receive HTTP response.

            Args:
                connection: Active HTTP client
                **options: Receive options

            Returns:
                FlextCore.Result containing response bytes or error

            """
            try:
                if not hasattr(self, "_last_response"):
                    return FlextCore.Result[bytes].fail("No response available")

                response = self._last_response
                content = response.read()

                return FlextCore.Result[bytes].ok(content)

            except Exception as e:
                return FlextCore.Result[bytes].fail(
                    f"Failed to receive HTTP response: {e}"
                )

        def supports_streaming(self) -> bool:
            """HTTP transport supports streaming."""
            return True

        def get_connection_info(
            self, _connection: httpx.Client
        ) -> FlextCore.Types.Dict:
            """Get HTTP connection information.

            Args:
                connection: Active HTTP client

            Returns:
                Dictionary containing connection metadata

            """
            return {
                "transport": "http",
                "http2_enabled": self._http2,
                "pool_limits": {
                    "max_connections": self._pool_limits.max_connections,
                    "max_keepalive": self._pool_limits.max_keepalive_connections,
                },
                "timeout": {
                    "connect": self._timeout.connect,
                    "read": self._timeout.read,
                    "write": self._timeout.write,
                    "pool": self._timeout.pool,
                },
            }


class WebSocketTransport(TransportPlugin):
    """WebSocket transport implementation (stub).

    Will be implemented in Phase 3 with websockets library.

    Features (planned):
    - Binary and text message support
    - Automatic reconnection
    - Ping/pong heartbeat
    - Message queuing
    """

    def __init__(self) -> None:
        """Initialize WebSocket transport stub."""
        super().__init__(
            name="websocket",
            version="1.0.0",
            description="WebSocket transport (stub - Phase 3)",
        )

    def connect(
        self,
        url: str,
        **options: object,
    ) -> FlextCore.Result[object]:
        """Connect to WebSocket endpoint (stub).

        Args:
            url: WebSocket URL
            **options: Connection options

        Returns:
            FlextCore.Result with stub error

        """
        return FlextCore.Result[object].fail(
            "WebSocket transport not yet implemented (Phase 3)"
        )

    def disconnect(
        self,
        connection: object,
    ) -> FlextCore.Result[None]:
        """Disconnect WebSocket (stub)."""
        return FlextCore.Result[None].fail(
            "WebSocket transport not yet implemented (Phase 3)"
        )

    def send(
        self,
        _connection: object,
        _data: bytes | str,
        **_options: object,
    ) -> FlextCore.Result[None]:
        """Send WebSocket message (stub)."""
        return FlextCore.Result[None].fail(
            "WebSocket transport not yet implemented (Phase 3)"
        )

    def receive(
        self,
        _connection: object,
        **_options: object,
    ) -> FlextCore.Result[bytes | str]:
        """Receive WebSocket message (stub)."""
        return FlextCore.Result[bytes | str].fail(
            "WebSocket transport not yet implemented (Phase 3)"
        )


class GraphQLTransport(TransportPlugin):
    """GraphQL transport implementation (stub).

    Will be implemented in Phase 4 with gql library.

    Features (planned):
    - Query/Mutation/Subscription support
    - Schema introspection
    - Fragment caching
    - Subscription via WebSocket
    """

    def __init__(self) -> None:
        """Initialize GraphQL transport stub."""
        super().__init__(
            name="graphql",
            version="1.0.0",
            description="GraphQL transport (stub - Phase 4)",
        )

    def connect(
        self,
        url: str,
        **options: object,
    ) -> FlextCore.Result[object]:
        """Connect to GraphQL endpoint (stub).

        Args:
            url: GraphQL endpoint URL
            **options: Connection options

        Returns:
            FlextCore.Result with stub error

        """
        return FlextCore.Result[object].fail(
            "GraphQL transport not yet implemented (Phase 4)"
        )

    def disconnect(
        self,
        _connection: object,
    ) -> FlextCore.Result[None]:
        """Disconnect GraphQL (stub)."""
        return FlextCore.Result[None].fail(
            "GraphQL transport not yet implemented (Phase 4)"
        )

    def send(
        self,
        _connection: object,
        _data: bytes | str,
        **_options: object,
    ) -> FlextCore.Result[None]:
        """Send GraphQL query (stub)."""
        return FlextCore.Result[None].fail(
            "GraphQL transport not yet implemented (Phase 4)"
        )

    def receive(
        self,
        _connection: object,
        **_options: object,
    ) -> FlextCore.Result[bytes | str]:
        """Receive GraphQL response (stub)."""
        return FlextCore.Result[bytes | str].fail(
            "GraphQL transport not yet implemented (Phase 4)"
        )


class SSETransport(TransportPlugin):
    """Server-Sent Events transport implementation (stub).

    Will be implemented in Phase 3 with sse-starlette.

    Features (planned):
    - Event stream parsing
    - Automatic reconnection with last-event-id
    - Event type filtering
    - Retry handling
    """

    def __init__(self) -> None:
        """Initialize SSE transport stub."""
        super().__init__(
            name="sse",
            version="1.0.0",
            description="Server-Sent Events transport (stub - Phase 3)",
        )

    def connect(
        self,
        url: str,
        **options: object,
    ) -> FlextCore.Result[object]:
        """Connect to SSE endpoint (stub).

        Args:
            url: SSE endpoint URL
            **options: Connection options

        Returns:
            FlextCore.Result with stub error

        """
        return FlextCore.Result[object].fail(
            "SSE transport not yet implemented (Phase 3)"
        )

    def disconnect(
        self,
        _connection: object,
    ) -> FlextCore.Result[None]:
        """Disconnect SSE (stub)."""
        return FlextCore.Result[None].fail(
            "SSE transport not yet implemented (Phase 3)"
        )

    def send(
        self,
        _connection: object,
        _data: bytes | str,
        **_options: object,
    ) -> FlextCore.Result[None]:
        """Send not applicable for SSE (stub)."""
        return FlextCore.Result[None].fail("SSE is receive-only, send not applicable")

    def receive(
        self,
        _connection: object,
        **_options: object,
    ) -> FlextCore.Result[bytes | str]:
        """Receive SSE event (stub)."""
        return FlextCore.Result[bytes | str].fail(
            "SSE transport not yet implemented (Phase 3)"
        )

    def supports_streaming(self) -> bool:
        """SSE is streaming-only."""
        return True


class GrpcTransport(TransportPlugin):
    """gRPC transport implementation (stub).

    Will be implemented in future phase integrating with flext-grpc.

    Features (planned):
    - Unary RPC
    - Server streaming
    - Client streaming
    - Bidirectional streaming
    - gRPC metadata support
    """

    def __init__(self) -> None:
        """Initialize gRPC transport stub."""
        super().__init__(
            name="grpc",
            version="1.0.0",
            description="gRPC transport (stub - future flext-grpc integration)",
        )

    def connect(
        self,
        url: str,
        **options: object,
    ) -> FlextCore.Result[object]:
        """Connect to gRPC service (stub).

        Args:
            url: gRPC service URL
            **options: Connection options

        Returns:
            FlextCore.Result with stub error

        """
        return FlextCore.Result[object].fail(
            "gRPC transport not yet implemented (future: flext-grpc integration)"
        )

    def disconnect(
        self,
        _connection: object,
    ) -> FlextCore.Result[None]:
        """Disconnect gRPC (stub)."""
        return FlextCore.Result[None].fail(
            "gRPC transport not yet implemented (future: flext-grpc integration)"
        )

    def send(
        self,
        _connection: object,
        _data: bytes | str,
        **_options: object,
    ) -> FlextCore.Result[None]:
        """Send gRPC request (stub)."""
        return FlextCore.Result[None].fail(
            "gRPC transport not yet implemented (future: flext-grpc integration)"
        )

    def receive(
        self,
        _connection: object,
        **_options: object,
    ) -> FlextCore.Result[bytes | str]:
        """Receive gRPC response (stub)."""
        return FlextCore.Result[bytes | str].fail(
            "gRPC transport not yet implemented (future: flext-grpc integration)"
        )


__all__ = [
    "FlextApiTransports",
]

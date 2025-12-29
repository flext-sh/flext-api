"""Unit tests for transport implementations.

Tests FlextApiTransports with proper mocking and no fallbacks.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from unittest.mock import MagicMock, patch  # TEST-INFRA
# All error checks below are safe with null checks, patch

import pytest
from flext_core import FlextTypes as t

from flext_api.transports import FlextApiTransports


class TestFlextWebTransport:
    """Unit tests for HTTP transport implementation."""

    @pytest.fixture
    def transport(self) -> FlextApiTransports.FlextWebTransport:
        """Create transport instance."""
        return FlextApiTransports.FlextWebTransport()

    def test_init_creates_transport(self, transport: FlextApiTransports.FlextWebTransport) -> None:
        """Test transport initialization."""
        assert transport._client is None

    @patch("httpx.Client")
    def test_connect_success(self, mock_client_class: MagicMock, transport: FlextApiTransports.FlextWebTransport) -> None:
        """Test successful connection to HTTP endpoint."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        result = transport.connect("https://api.example.com")

        assert result.is_success
        assert result.value is mock_client
        assert transport._client is mock_client
        mock_client_class.assert_called_once()

    @patch("httpx.Client")
    def test_connect_with_options(self, mock_client_class: MagicMock, transport: FlextApiTransports.FlextWebTransport) -> None:
        """Test connection with custom options."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        result = transport.connect("https://api.example.com", timeout=30.0, verify=False)

        assert result.is_success
        # Current implementation doesn't use options, just creates basic client
        mock_client_class.assert_called_once_with()

    @patch("httpx.Client")
    def test_connect_failure(self, mock_client_class: MagicMock, transport: FlextApiTransports.FlextWebTransport) -> None:
        """Test connection failure."""
        mock_client_class.side_effect = Exception("Connection failed")

        result = transport.connect("https://api.example.com")

        assert result.is_failure
        assert result.error is not None
        assert result.error is not None and "Connection failed" in result.error

    def test_disconnect_when_connected(self, transport: FlextApiTransports.FlextWebTransport) -> None:
        """Test disconnect when client is connected."""
        import httpx  # CONDITIONAL  # CONDITIONAL
        mock_client = MagicMock(spec=httpx.Client)
        transport._client = mock_client

        result = transport.disconnect(mock_client)

        assert result.is_success
        assert result.value is True
        mock_client.close.assert_called_once()
        assert transport._client is None

    def test_disconnect_when_not_connected(self, transport: FlextApiTransports.FlextWebTransport) -> None:
        """Test disconnect when no client is connected."""
        # Create a mock that behaves like httpx.Client
        import httpx  # CONDITIONAL  # CONDITIONAL
        mock_client = MagicMock(spec=httpx.Client)
        result = transport.disconnect(mock_client)

        assert result.is_success
        assert result.value is True
        mock_client.close.assert_called_once()

    def test_disconnect_wrong_connection(self, transport: FlextApiTransports.FlextWebTransport) -> None:
        """Test disconnect with wrong connection object."""
        import httpx  # CONDITIONAL  # CONDITIONAL
        mock_client = MagicMock(spec=httpx.Client)
        transport._client = mock_client

        other_client = MagicMock(spec=httpx.Client)
        result = transport.disconnect(other_client)

        assert result.is_success
        assert result.value is True
        other_client.close.assert_called_once()

    def test_send_with_connection(self, transport: FlextApiTransports.FlextWebTransport) -> None:
        """Test sending data through connection."""
        import httpx  # CONDITIONAL  # CONDITIONAL
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_client.request.return_value = mock_response
        transport._client = mock_client

        test_data = {"method": "GET", "url": "/test"}
        result = transport.send(mock_client, test_data)

        assert result.is_success
        # The result should be a dict with response data
        assert isinstance(result.value, dict)
        assert "status_code" in result.value
        assert "headers" in result.value
        assert "content" in result.value

    def test_send_wrong_connection(self, transport: FlextApiTransports.FlextWebTransport) -> None:
        """Test sending with wrong connection object."""
        mock_client = MagicMock()
        transport._client = mock_client

        other_client = MagicMock()
        result = transport.send(other_client, {"method": "GET", "url": "/test"})

        assert result.is_failure
        assert result.error is not None
        assert "Connection must be an httpx.Client" in result.error

    def test_send_no_connection(self, transport: FlextApiTransports.FlextWebTransport) -> None:
        """Test sending without established connection."""
        result = transport.send(None, {"method": "GET", "url": "/test"})

        assert result.is_failure
        assert result.error is not None
        assert "Connection must be an httpx.Client" in result.error

    def test_extract_request_params_with_method_and_url(self, transport: FlextApiTransports.FlextWebTransport) -> None:
        """Test parameter extraction with method and URL."""
        data: dict[str, t.GeneralValueType] = {"method": "POST", "url": "/api/test"}

        result = transport._extract_request_params(data)

        assert result.is_success
        method, url, headers, params, json_data, content = result.value
        assert method == "POST"
        assert url == "/api/test"
        assert headers == {}
        assert params is None
        assert json_data is None
        assert content is None

    def test_extract_request_params_minimal(self, transport: FlextApiTransports.FlextWebTransport) -> None:
        """Test parameter extraction with minimal data."""
        data: dict[str, t.GeneralValueType] = {}

        result = transport._extract_request_params(data)

        assert result.is_failure
        assert result.error is not None
        assert "URL is required" in result.error


class TestWebSocketTransport:
    """Unit tests for WebSocket transport (Phase 3 - not implemented)."""

    def test_connect_returns_not_implemented(self) -> None:
        """Test WebSocket connect returns not implemented error."""
        transport = FlextApiTransports.WebSocketTransport()
        result = transport.connect("ws://example.com")
        assert result.is_failure
        assert result.error is not None
        assert "WebSocket transport not implemented" in result.error

    def test_disconnect_returns_not_implemented(self) -> None:
        """Test WebSocket disconnect returns not implemented error."""
        transport = FlextApiTransports.WebSocketTransport()
        result = transport.disconnect("dummy_connection")
        assert result.is_failure
        assert result.error is not None
        assert "WebSocket transport not implemented" in result.error

    def test_send_returns_not_implemented(self) -> None:
        """Test WebSocket send returns not implemented error."""
        transport = FlextApiTransports.WebSocketTransport()
        result = transport.send("dummy_connection", {})
        assert result.is_failure
        assert result.error is not None
        assert "WebSocket transport not implemented" in result.error


class TestSseTransport:
    """Unit tests for SSE transport (Phase 3 - not implemented)."""

    def test_connect_returns_not_implemented(self) -> None:
        """Test SSE connect returns not implemented error."""
        transport = FlextApiTransports.SseTransport()
        result = transport.connect("http://example.com/sse")
        assert result.is_failure
        assert result.error is not None and "SSE transport not implemented" in result.error

    def test_disconnect_returns_not_implemented(self) -> None:
        """Test SSE disconnect returns not implemented error."""
        transport = FlextApiTransports.SseTransport()
        result = transport.disconnect("dummy_connection")
        assert result.is_failure
        assert result.error is not None and "SSE transport not implemented" in result.error

    def test_send_returns_not_implemented(self) -> None:
        """Test SSE send returns not implemented error."""
        transport = FlextApiTransports.SseTransport()
        result = transport.send("dummy_connection", {})
        assert result.is_failure
        assert result.error is not None and "SSE transport not implemented" in result.error


class TestGraphQLTransport:
    """Unit tests for GraphQL transport (Phase 3 - not implemented)."""

    def test_connect_returns_not_implemented(self) -> None:
        """Test GraphQL connect returns not implemented error."""
        transport = FlextApiTransports.GraphQLTransport()
        result = transport.connect("http://example.com/graphql")
        assert result.is_failure
        assert result.error is not None and "GraphQL transport not implemented" in result.error

    def test_disconnect_returns_not_implemented(self) -> None:
        """Test GraphQL disconnect returns not implemented error."""
        transport = FlextApiTransports.GraphQLTransport()
        result = transport.disconnect("dummy_connection")
        assert result.is_failure
        assert result.error is not None and "GraphQL transport not implemented" in result.error

    def test_send_returns_not_implemented(self) -> None:
        """Test GraphQL send returns not implemented error."""
        transport = FlextApiTransports.GraphQLTransport()
        result = transport.send("dummy_connection", {})
        assert result.is_failure
        assert result.error is not None and "GraphQL transport not implemented" in result.error


class TestGrpcTransport:
    """Unit tests for gRPC transport (Phase 3 - not implemented)."""

    def test_connect_returns_not_implemented(self) -> None:
        """Test gRPC connect returns not implemented error."""
        transport = FlextApiTransports.GrpcTransport()
        result = transport.connect("grpc://example.com")
        assert result.is_failure
        assert result.error is not None and "gRPC transport not implemented" in result.error

    def test_disconnect_returns_not_implemented(self) -> None:
        """Test gRPC disconnect returns not implemented error."""
        transport = FlextApiTransports.GrpcTransport()
        result = transport.disconnect("dummy_connection")
        assert result.is_failure
        assert result.error is not None and "gRPC transport not implemented" in result.error

    def test_send_returns_not_implemented(self) -> None:
        """Test gRPC send returns not implemented error."""
        transport = FlextApiTransports.GrpcTransport()
        result = transport.send("dummy_connection", {})
        assert result.is_failure
        assert result.error is not None and "gRPC transport not implemented" in result.error

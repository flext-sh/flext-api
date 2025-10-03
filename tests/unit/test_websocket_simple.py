"""Simple unit tests for WebSocket protocol plugin.

Focused tests for WebSocket protocol implementation validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from flext_api.models import FlextApiModels
from flext_api.protocol_impls.websocket import WebSocketProtocolPlugin


class TestWebSocketProtocolPluginSimple:
    """Simple test suite for WebSocketProtocolPlugin."""

    def test_plugin_initialization(self) -> None:
        """Test WebSocket plugin initialization."""
        plugin = WebSocketProtocolPlugin(
            ping_interval=20.0,
            ping_timeout=20.0,
            auto_reconnect=True,
        )

        assert plugin is not None
        assert plugin.name == "websocket"
        assert plugin._ping_interval == 20.0
        assert plugin._auto_reconnect is True

    def test_plugin_supports_protocol(self) -> None:
        """Test protocol support checking."""
        plugin = WebSocketProtocolPlugin()

        assert plugin.supports_protocol("websocket") is True
        assert plugin.supports_protocol("ws") is True
        assert plugin.supports_protocol("wss") is True
        assert plugin.supports_protocol("http") is False

    def test_plugin_get_supported_protocols(self) -> None:
        """Test getting list of supported protocols."""
        plugin = WebSocketProtocolPlugin()

        protocols = plugin.get_supported_protocols()

        assert "websocket" in protocols
        assert "ws" in protocols
        assert "wss" in protocols

    def test_plugin_initialization_lifecycle(self) -> None:
        """Test plugin initialization and shutdown lifecycle."""
        plugin = WebSocketProtocolPlugin()

        # Test initialization
        init_result = plugin.initialize()
        assert init_result.is_success
        assert plugin.is_initialized

        # Test double initialization fails
        init_result_2 = plugin.initialize()
        assert init_result_2.is_failure

        # Test shutdown
        shutdown_result = plugin.shutdown()
        assert shutdown_result.is_success
        assert not plugin.is_initialized

        # Test double shutdown fails
        shutdown_result_2 = plugin.shutdown()
        assert shutdown_result_2.is_failure

    def test_plugin_metadata(self) -> None:
        """Test plugin metadata retrieval."""
        plugin = WebSocketProtocolPlugin()

        metadata = plugin.get_metadata()

        assert metadata["name"] == "websocket"
        assert "version" in metadata
        assert "description" in metadata
        assert "initialized" in metadata

    def test_plugin_connection_state(self) -> None:
        """Test WebSocket connection state tracking."""
        plugin = WebSocketProtocolPlugin()

        # Initially not connected
        assert not plugin.is_connected
        assert plugin._connected is False

    def test_plugin_event_handlers(self) -> None:
        """Test event handler registration."""
        plugin = WebSocketProtocolPlugin()

        def on_message(message: str) -> None:
            pass

        def on_connect() -> None:
            pass

        def on_disconnect() -> None:
            pass

        def on_error(error: Exception) -> None:
            pass

        plugin.on_message(on_message)
        plugin.on_connect(on_connect)
        plugin.on_disconnect(on_disconnect)
        plugin.on_error(on_error)

        assert len(plugin._on_message_handlers) == 1
        assert len(plugin._on_connect_handlers) == 1
        assert len(plugin._on_disconnect_handlers) == 1
        assert len(plugin._on_error_handlers) == 1


class TestWebSocketModelsSimple:
    """Simple test suite for WebSocket models."""

    def test_websocket_message_creation(self) -> None:
        """Test WebSocketMessage creation."""
        message = FlextApiModels.WebSocketMessage(
            message="Hello WebSocket",
            message_type="text",
            timestamp=datetime.now(UTC).isoformat(),
        )

        assert message.message == "Hello WebSocket"
        assert message.message_type == "text"

    def test_websocket_message_binary(self) -> None:
        """Test WebSocketMessage with binary data."""
        message = FlextApiModels.WebSocketMessage(
            message=b"Binary data",
            message_type="binary",
            timestamp=datetime.now(UTC).isoformat(),
        )

        assert message.message == b"Binary data"
        assert message.message_type == "binary"

    def test_websocket_message_invalid_type(self) -> None:
        """Test WebSocketMessage with invalid type."""
        with pytest.raises(ValueError):
            FlextApiModels.WebSocketMessage(
                message="test",
                message_type="invalid",
                timestamp=datetime.now(UTC).isoformat(),
            )

    def test_websocket_connection_creation(self) -> None:
        """Test WebSocketConnection creation."""
        connection = FlextApiModels.WebSocketConnection(
            url="wss://api.example.com/ws",
            state="connected",
        )

        assert connection.url == "wss://api.example.com/ws"
        assert connection.state == "connected"
        assert connection.is_connected is True
        assert connection.is_secure is True

    def test_websocket_connection_insecure(self) -> None:
        """Test WebSocketConnection with ws:// (insecure)."""
        connection = FlextApiModels.WebSocketConnection(
            url="ws://api.example.com/ws",
            state="connected",
        )

        assert connection.is_secure is False

    def test_websocket_connection_invalid_url(self) -> None:
        """Test WebSocketConnection with invalid URL."""
        with pytest.raises(ValueError):
            FlextApiModels.WebSocketConnection(
                url="http://api.example.com/ws",
                state="connected",
            )

    def test_websocket_connection_invalid_state(self) -> None:
        """Test WebSocketConnection with invalid state."""
        with pytest.raises(ValueError):
            FlextApiModels.WebSocketConnection(
                url="wss://api.example.com/ws",
                state="invalid_state",
            )

    def test_websocket_connection_message_tracking(self) -> None:
        """Test WebSocketConnection message tracking."""
        connection = FlextApiModels.WebSocketConnection(
            url="wss://api.example.com/ws",
            state="connected",
            messages_sent=10,
            messages_received=15,
        )

        assert connection.messages_sent == 10
        assert connection.messages_received == 15

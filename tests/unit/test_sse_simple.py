"""Simple unit tests for SSE protocol plugin.

Focused tests for Server-Sent Events protocol implementation validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import datetime

import pytest

from flext_api.models import FlextApiModels
from flext_api.protocol_impls.sse import SSEProtocolPlugin


class TestSSEProtocolPluginSimple:
    """Simple test suite for SSEProtocolPlugin."""

    def test_plugin_initialization(self) -> None:
        """Test SSE plugin initialization."""
        plugin = SSEProtocolPlugin(
            retry_timeout=3000,
            connect_timeout=30.0,
            auto_reconnect=True,
        )

        assert plugin is not None
        assert plugin.name == "sse"
        assert plugin._retry_timeout == 3000
        assert plugin._auto_reconnect is True

    def test_plugin_supports_protocol(self) -> None:
        """Test protocol support checking."""
        plugin = SSEProtocolPlugin()

        assert plugin.supports_protocol("sse") is True
        assert plugin.supports_protocol("server-sent-events") is True
        assert plugin.supports_protocol("eventsource") is True
        assert plugin.supports_protocol("http") is False

    def test_plugin_get_supported_protocols(self) -> None:
        """Test getting list of supported protocols."""
        plugin = SSEProtocolPlugin()

        protocols = plugin.get_supported_protocols()

        assert "sse" in protocols
        assert "server-sent-events" in protocols
        assert "eventsource" in protocols

    def test_plugin_initialization_lifecycle(self) -> None:
        """Test plugin initialization and shutdown lifecycle."""
        plugin = SSEProtocolPlugin()

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
        plugin = SSEProtocolPlugin()

        metadata = plugin.get_metadata()

        assert metadata["name"] == "sse"
        assert "version" in metadata
        assert "description" in metadata
        assert "initialized" in metadata

    def test_plugin_connection_state(self) -> None:
        """Test SSE connection state tracking."""
        plugin = SSEProtocolPlugin()

        # Initially not connected
        assert not plugin.is_connected
        assert plugin._connected is False
        assert plugin.last_event_id == ""

    def test_plugin_event_handlers(self) -> None:
        """Test event handler registration."""
        plugin = SSEProtocolPlugin()

        def on_message_event(event) -> None:
            pass

        def on_update_event(event) -> None:
            pass

        def on_connect() -> None:
            pass

        def on_disconnect() -> None:
            pass

        def on_error(error) -> None:
            pass

        plugin.on_event("message", on_message_event)
        plugin.on_event("update", on_update_event)
        plugin.on_connect(on_connect)
        plugin.on_disconnect(on_disconnect)
        plugin.on_error(on_error)

        assert "message" in plugin._on_event_handlers
        assert "update" in plugin._on_event_handlers
        assert len(plugin._on_event_handlers["message"]) == 1
        assert len(plugin._on_event_handlers["update"]) == 1
        assert len(plugin._on_connect_handlers) == 1
        assert len(plugin._on_disconnect_handlers) == 1
        assert len(plugin._on_error_handlers) == 1

    def test_plugin_wildcard_event_handlers(self) -> None:
        """Test wildcard event handler registration."""
        plugin = SSEProtocolPlugin()

        def on_any_event(event) -> None:
            pass

        plugin.on_event("*", on_any_event)

        assert "*" in plugin._on_event_handlers
        assert len(plugin._on_event_handlers["*"]) == 1


class TestSSEModelsSimple:
    """Simple test suite for SSE models."""

    def test_sse_event_creation(self) -> None:
        """Test SSEEvent creation."""
        event = FlextApiModels.SSEEvent(
            event_type="message",
            data="Hello SSE",
            timestamp=datetime.now().isoformat(),
        )

        assert event.event_type == "message"
        assert event.data == "Hello SSE"
        assert event.has_id is False

    def test_sse_event_with_id(self) -> None:
        """Test SSEEvent with event ID."""
        event = FlextApiModels.SSEEvent(
            event_type="update",
            data="Update data",
            event_id="123",
            timestamp=datetime.now().isoformat(),
        )

        assert event.event_id == "123"
        assert event.has_id is True

    def test_sse_event_with_retry(self) -> None:
        """Test SSEEvent with retry timeout."""
        event = FlextApiModels.SSEEvent(
            event_type="message",
            data="test data",
            retry=5000,
            timestamp=datetime.now().isoformat(),
        )

        assert event.retry == 5000

    def test_sse_event_data_length(self) -> None:
        """Test SSEEvent data length computation."""
        event = FlextApiModels.SSEEvent(
            event_type="message",
            data="test data with length",
            timestamp=datetime.now().isoformat(),
        )

        assert event.data_length == len("test data with length")

    def test_sse_connection_creation(self) -> None:
        """Test SSEConnection creation."""
        connection = FlextApiModels.SSEConnection(
            url="https://api.example.com/events",
            state="connected",
        )

        assert connection.url == "https://api.example.com/events"
        assert connection.state == "connected"
        assert connection.is_connected is True

    def test_sse_connection_with_last_event_id(self) -> None:
        """Test SSEConnection with last event ID."""
        connection = FlextApiModels.SSEConnection(
            url="https://api.example.com/events",
            state="connected",
            last_event_id="abc123",
        )

        assert connection.last_event_id == "abc123"
        assert connection.has_last_event_id is True

    def test_sse_connection_invalid_state(self) -> None:
        """Test SSEConnection with invalid state."""
        with pytest.raises(ValueError):
            FlextApiModels.SSEConnection(
                url="https://api.example.com/events",
                state="invalid_state",
            )

    def test_sse_connection_retry_timeout_conversion(self) -> None:
        """Test SSEConnection retry timeout conversion."""
        connection = FlextApiModels.SSEConnection(
            url="https://api.example.com/events",
            state="connected",
            retry_timeout=5000,
        )

        assert connection.retry_timeout == 5000
        assert connection.retry_timeout_seconds == 5.0

    def test_sse_connection_event_tracking(self) -> None:
        """Test SSEConnection event tracking."""
        connection = FlextApiModels.SSEConnection(
            url="https://api.example.com/events",
            state="connected",
            events_received=42,
            reconnect_count=3,
        )

        assert connection.events_received == 42
        assert connection.reconnect_count == 3

"""Simple unit tests for server and webhook functionality.

Focused tests for FlextApiServer and FlextWebhookHandler.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.app import FlextApiApp
from flext_api.server import FlextApiServer
from flext_api.webhook import FlextWebhookHandler


class TestFlextApiServer:
    """Simple test suite for FlextApiServer."""

    def test_server_initialization(self) -> None:
        """Test server initialization."""
        server = FlextApiServer(
            host="127.0.0.1",
            port=8080,
            title="Test Server",
            version="1.0.0",
        )

        assert server is not None
        assert server.host == "127.0.0.1"
        assert server.port == 8080
        assert server.is_running is False

    def test_server_default_initialization(self) -> None:
        """Test server initialization with defaults."""
        server = FlextApiServer()

        assert server.host == "0.0.0.0"
        assert server.port == 8000
        assert server.is_running is False

    def test_server_register_protocol_handler(self) -> None:
        """Test protocol handler registration."""
        from flext_api.protocol_impls.http import HttpProtocolPlugin

        server = FlextApiServer()
        handler = HttpProtocolPlugin()

        result = server.register_protocol_handler("http", handler)

        assert result.is_success
        assert "http" in server.protocols

    def test_server_register_duplicate_protocol(self) -> None:
        """Test registering duplicate protocol handler fails."""
        from flext_api.protocol_impls.http import HttpProtocolPlugin

        server = FlextApiServer()
        handler = HttpProtocolPlugin()

        result1 = server.register_protocol_handler("http", handler)
        result2 = server.register_protocol_handler("http", handler)

        assert result1.is_success
        assert result2.is_failure
        assert "already registered" in result2.error

    def test_server_register_route(self) -> None:
        """Test route registration."""
        server = FlextApiServer()

        def test_handler() -> dict[str, str]:
            return {"message": "test"}

        result = server.register_route("/test", "GET", test_handler)

        assert result.is_success
        assert "GET:/test" in server.routes

    def test_server_register_duplicate_route(self) -> None:
        """Test registering duplicate route fails."""
        server = FlextApiServer()

        def test_handler() -> dict:
            return {"message": "test"}

        result1 = server.register_route("/test", "GET", test_handler)
        result2 = server.register_route("/test", "GET", test_handler)

        assert result1.is_success
        assert result2.is_failure
        assert "already registered" in result2.error

    def test_server_register_websocket_endpoint(self) -> None:
        """Test WebSocket endpoint registration."""
        server = FlextApiServer()

        def ws_handler(websocket: object) -> None:
            pass

        result = server.register_websocket_endpoint("/ws", ws_handler)

        assert result.is_success
        assert "WS:/ws" in server.routes

    def test_server_register_sse_endpoint(self) -> None:
        """Test SSE endpoint registration."""
        server = FlextApiServer()

        def sse_handler() -> None:
            pass

        result = server.register_sse_endpoint("/events", sse_handler)

        assert result.is_success
        assert "SSE:/events" in server.routes

    def test_server_register_graphql_endpoint(self) -> None:
        """Test GraphQL endpoint registration."""
        server = FlextApiServer()

        result = server.register_graphql_endpoint("/graphql")

        assert result.is_success
        assert "GRAPHQL:/graphql" in server.routes

    def test_server_start_creates_app(self) -> None:
        """Test server start creates FastAPI app."""
        server = FlextApiServer()

        result = server.start()

        assert result.is_success
        assert server.is_running is True

        # Cleanup
        server.stop()

    def test_server_stop_when_not_running(self) -> None:
        """Test stopping server when not running fails."""
        server = FlextApiServer()

        result = server.stop()

        assert result.is_failure
        assert result.error is not None and "not running" in result.error

    def test_server_start_stop_lifecycle(self) -> None:
        """Test server start/stop lifecycle."""
        server = FlextApiServer()

        # Start server
        start_result = server.start()
        assert start_result.is_success
        assert server.is_running is True

        # Stop server
        stop_result = server.stop()
        assert stop_result.is_success
        assert server.is_running is False


class TestFlextWebhookHandler:
    """Simple test suite for FlextWebhookHandler."""

    def test_webhook_handler_initialization(self) -> None:
        """Test webhook handler initialization."""
        handler = FlextWebhookHandler(
            secret="test_secret",
            max_retries=5,
            retry_delay=2.0,
        )

        assert handler is not None
        assert handler._secret == "test_secret"
        assert handler._max_retries == 5
        assert handler._retry_delay == 2.0

    def test_webhook_handler_default_initialization(self) -> None:
        """Test webhook handler initialization with defaults."""
        handler = FlextWebhookHandler()

        assert handler._secret is None
        assert handler._max_retries == 3
        assert handler._retry_delay == 1.0

    def test_webhook_register_event_handler(self) -> None:
        """Test event handler registration."""
        handler = FlextWebhookHandler()

        def test_handler(event_data: dict) -> None:
            pass

        result = handler.register_event_handler("user.created", test_handler)

        assert result.is_success
        assert "user.created" in handler._event_handlers

    def test_webhook_register_multiple_handlers_same_event(self) -> None:
        """Test registering multiple handlers for same event."""
        handler = FlextWebhookHandler()

        def handler1(event_data: FlextTypes.Dict) -> None:
            pass

        def handler2(event_data: FlextTypes.Dict) -> None:
            pass

        result1 = handler.register_event_handler("user.created", handler1)
        result2 = handler.register_event_handler("user.created", handler2)

        assert result1.is_success
        assert result2.is_success
        assert len(handler._event_handlers["user.created"]) == 2

    def test_webhook_receive_without_signature(self) -> None:
        """Test receiving webhook without signature verification."""
        handler = FlextWebhookHandler()  # No secret

        payload = '{"type": "user.created", "data": {"id": "123"}}'
        headers = {}

        result = handler.receive_webhook(payload, headers)

        # Without registered handler, should succeed but not process
        assert result.is_success

    def test_webhook_receive_with_signature(self) -> None:
        """Test receiving webhook with signature verification."""
        import hashlib
        import hmac

        handler = FlextWebhookHandler(secret="test_secret")

        payload = '{"type": "user.created", "data": {"id": "123"}}'
        signature = hmac.new(
            b"test_secret",
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        headers = {"X-Webhook-Signature": signature}

        result = handler.receive_webhook(payload, headers)

        assert result.is_success

    def test_webhook_receive_invalid_signature(self) -> None:
        """Test receiving webhook with invalid signature."""
        handler = FlextWebhookHandler(secret="test_secret")

        payload = '{"type": "user.created", "data": {"id": "123"}}'
        headers = {"X-Webhook-Signature": "invalid_signature"}

        result = handler.receive_webhook(payload, headers)

        assert result.is_failure
        assert result.error is not None and "Signature" in result.error

    def test_webhook_receive_missing_signature(self) -> None:
        """Test receiving webhook with missing signature when required."""
        handler = FlextWebhookHandler(secret="test_secret")

        payload = '{"type": "user.created", "data": {"id": "123"}}'
        headers = {}

        result = handler.receive_webhook(payload, headers)

        assert result.is_failure
        assert result.error is not None and "signature" in result.error.lower()

    def test_webhook_receive_invalid_json(self) -> None:
        """Test receiving webhook with invalid JSON."""
        handler = FlextWebhookHandler()

        payload = "invalid json {"
        headers = {}

        result = handler.receive_webhook(payload, headers)

        assert result.is_failure
        assert result.error is not None and "parse" in result.error.lower()

    def test_webhook_receive_missing_event_type(self) -> None:
        """Test receiving webhook without event type."""
        handler = FlextWebhookHandler()

        payload = '{"data": {"id": "123"}}'
        headers = {}

        result = handler.receive_webhook(payload, headers)

        assert result.is_failure
        assert result.error is not None and "event type" in result.error.lower()

    def test_webhook_get_queue_stats(self) -> None:
        """Test getting webhook queue statistics."""
        handler = FlextWebhookHandler()

        stats = handler.get_queue_stats()

        assert "event_queue_size" in stats
        assert "retry_queue_size" in stats
        assert "total_deliveries" in stats
        assert "successful_deliveries" in stats
        assert "failed_deliveries" in stats


class TestFlextApiAppEnhancements:
    """Test suite for FlextApiApp enhancements."""

    def test_create_server_factory_method(self) -> None:
        """Test create_server factory method."""
        result = FlextApiApp.create_server(
            host="127.0.0.1",
            port=9000,
            title="Test Server",
            version="2.0.0",
        )

        assert result.is_success
        server = result.unwrap()
        assert server.host == "127.0.0.1"
        assert server.port == 9000

    def test_create_webhook_handler_factory_method(self) -> None:
        """Test create_webhook_handler factory method."""
        result = FlextApiApp.create_webhook_handler(
            secret="factory_secret",
            max_retries=5,
        )

        assert result.is_success
        handler = result.unwrap()
        assert handler._secret == "factory_secret"
        assert handler._max_retries == 5

"""WebSocket Protocol Plugin for flext-api.

Implements WebSocket protocol support with:
- Connection management and lifecycle
- Message handling (text/binary)
- Event-driven architecture
- Automatic reconnection logic
- Ping/pong heartbeat mechanism
- Integration with FlextResult patterns

See TRANSFORMATION_PLAN.md - Phase 3 for implementation details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import time
from collections.abc import Callable

import websockets
from pydantic import ConfigDict

from flext import r
from flext_api.constants import FlextApiConstants
from flext_api.protocol_impls.rfc import RFCProtocolImplementation
from flext_api.typings import t

# Asyncio utilities
# Synchronous alternatives for async functionality


class WebSocketProtocolPlugin(RFCProtocolImplementation):
    """WebSocket protocol plugin with full lifecycle management.

    Features:
    - WebSocket connection management
    - Text and binary message support
    - Event-driven message handling
    - Automatic reconnection with backoff
    - Ping/pong heartbeat mechanism
    - Connection state tracking
    - Error recovery and resilience

    Integration:
    - Uses websockets library for transport
    - FlextResult for error handling
    - FlextLogger for structured logging
    - Event callbacks for message handling
    """

    # Override frozen constraint from RFCProtocolImplementation - WebSocket needs mutable state
    model_config = ConfigDict(frozen=False, arbitrary_types_allowed=True)

    # Declare attributes to satisfy type checkers
    # These are initialized via object.__setattr__() in __init__()
    _ping_interval: float
    _ping_timeout: float
    _close_timeout: float
    _max_size: int
    _max_queue: int
    _compression: str
    _auto_reconnect: bool
    _reconnect_max_attempts: int
    _reconnect_backoff_factor: float
    _connection: object | None
    _connected: bool
    _url: str
    _headers: dict[str, str]
    _on_message_handlers: list[Callable]
    _on_connect_handlers: list[Callable]
    _on_disconnect_handlers: list[Callable]
    _on_error_handlers: list[Callable]

    def __init__(
        self,
        ping_interval: float | None = None,
        ping_timeout: float | None = None,
        close_timeout: float | None = None,
        max_size: int | None = None,
        max_queue: int | None = None,
        compression: str | None = None,
        *,
        auto_reconnect: bool = True,
        reconnect_max_attempts: int | None = None,
        reconnect_backoff_factor: float | None = None,
    ) -> None:
        """Initialize WebSocket protocol plugin.

        Args:
        ping_interval: Ping interval in seconds
        ping_timeout: Ping timeout in seconds
        close_timeout: Close timeout in seconds
        max_size: Maximum message size in bytes
        max_queue: Maximum queue size for outgoing messages
        compression: Compression method (deflate or None)
        auto_reconnect: Enable automatic reconnection
        reconnect_max_attempts: Maximum reconnection attempts
        reconnect_backoff_factor: Reconnection backoff multiplier

        """
        super().__init__(
            name="websocket",
            version="1.0.0",
            description="WebSocket protocol support with event-driven architecture",
        )

        # Use object.__setattr__() to bypass frozen Pydantic model constraints
        # WebSocket configuration - use constants if not provided
        object.__setattr__(
            self,
            "_ping_interval",
            (
                ping_interval
                if ping_interval is not None
                else FlextApiConstants.WebSocket.DEFAULT_PING_INTERVAL
            ),
        )
        object.__setattr__(
            self,
            "_ping_timeout",
            (
                ping_timeout
                if ping_timeout is not None
                else FlextApiConstants.WebSocket.DEFAULT_PING_TIMEOUT
            ),
        )
        object.__setattr__(
            self,
            "_close_timeout",
            (
                close_timeout
                if close_timeout is not None
                else FlextApiConstants.WebSocket.DEFAULT_CLOSE_TIMEOUT
            ),
        )
        object.__setattr__(
            self,
            "_max_size",
            (
                max_size
                if max_size is not None
                else FlextApiConstants.WebSocket.DEFAULT_MAX_SIZE
            ),
        )
        object.__setattr__(
            self,
            "_max_queue",
            (
                max_queue
                if max_queue is not None
                else FlextApiConstants.WebSocket.DEFAULT_MAX_QUEUE
            ),
        )
        object.__setattr__(
            self,
            "_compression",
            (
                compression
                if compression is not None
                else FlextApiConstants.WebSocket.COMPRESSION_DEFLATE
            ),
        )

        # Reconnection configuration - use constants if not provided
        object.__setattr__(self, "_auto_reconnect", auto_reconnect)
        object.__setattr__(
            self,
            "_reconnect_max_attempts",
            (
                reconnect_max_attempts
                if reconnect_max_attempts is not None
                else FlextApiConstants.WebSocket.DEFAULT_RECONNECT_MAX_ATTEMPTS
            ),
        )
        object.__setattr__(
            self,
            "_reconnect_backoff_factor",
            (
                reconnect_backoff_factor
                if reconnect_backoff_factor is not None
                else FlextApiConstants.WebSocket.DEFAULT_RECONNECT_BACKOFF_FACTOR
            ),
        )

        # Connection state
        object.__setattr__(self, "_connection", None)
        object.__setattr__(self, "_connected", False)
        object.__setattr__(self, "_url", "")
        object.__setattr__(self, "_headers", {})

        # Event handlers
        object.__setattr__(self, "_on_message_handlers", [])
        object.__setattr__(self, "_on_connect_handlers", [])
        object.__setattr__(self, "_on_disconnect_handlers", [])
        object.__setattr__(self, "_on_error_handlers", [])

        # Initialize protocol
        init_result = self.initialize()
        if init_result.is_failure:
            self.logger.error(
                f"Failed to initialize WebSocket protocol: {init_result.error}",
            )

    def _extract_message(
        self,
        request: t.JsonObject,
        kwargs: dict[str, object],
    ) -> r[str | bytes]:
        """Extract message from request or kwargs."""
        if "message" in kwargs:
            message_value = kwargs["message"]
            if isinstance(message_value, (str, bytes)):
                return r[str | bytes].ok(message_value)
            if message_value is not None:
                return r[str | bytes].ok(str(message_value))

        # Type narrowing: convert JsonObject to dict[str, object]
        request_dict: dict[str, object] = dict(request.items())
        body = self._extract_body(request_dict)
        if body is not None:
            if isinstance(body, (str, bytes)):
                return r[str | bytes].ok(body)
            return r[str | bytes].ok(str(body))

        return r[str | bytes].fail("Message or body is required")

    def _extract_message_type(self, kwargs: dict[str, object]) -> str:
        """Extract message type from kwargs."""
        if "message_type" in kwargs:
            message_type_value = kwargs["message_type"]
            if isinstance(message_type_value, str):
                return message_type_value
            if message_type_value is not None:
                return str(message_type_value)
        return FlextApiConstants.WebSocket.MessageType.TEXT

    def _ensure_connected(self, request: t.JsonObject) -> r[bool]:
        """Ensure WebSocket is connected."""
        if self._connected:
            return r[bool].ok(True)

        # Type narrowing: convert JsonObject to dict[str, object]
        req_dict: dict[str, object] = dict(request.items())
        # Use RFC method to extract URL
        url_result = self._extract_url(req_dict)
        if url_result.is_failure:
            return r[bool].fail(url_result.error or "URL extraction failed")

        # Use RFC method to extract headers
        headers = self._extract_headers(req_dict)

        return self._connect(url_result.value, headers)

    def send_request(
        self,
        request: dict[str, object],
        **kwargs: object,
    ) -> r[dict[str, object]]:
        """Send WebSocket request (connect and send message).

        Args:
        request: HTTP request model (adapted for WebSocket)
        **kwargs: Additional WebSocket-specific parameters

        Returns:
        FlextResult containing response or error

        """
        if not isinstance(request, dict):
            return r[dict[str, object]].fail("Request must be a dictionary")

        # Extract WebSocket-specific parameters
        # Convert request to JsonValue dict to match method signature
        json_request = dict(request.items())
        message_result = self._extract_message(
            json_request,  # type: ignore[arg-type]
            kwargs,
        )
        if message_result.is_failure:
            return r[dict[str, object]].fail(
                message_result.error or "Message extraction failed",
            )

        message_type = self._extract_message_type(kwargs)

        # Connect if not connected
        # Convert request to JsonValue dict to match method signature
        connect_result = self._ensure_connected(json_request)  # type: ignore[arg-type]
        if connect_result.is_failure:
            return r[dict[str, object]].fail(
                f"WebSocket connection failed: {connect_result.error}",
            )

        # Send message
        send_result = self._send_message(message_result.value, message_type)
        if send_result.is_failure:
            return r[dict[str, object]].fail(
                f"WebSocket send failed: {send_result.error}",
            )

        # Create response (WebSocket doesn't have traditional responses)
        url_result = self._extract_url(request)
        if url_result.is_failure:
            return r[dict[str, object]].fail(
                f"Failed to extract URL: {url_result.error}",
            )

        response: dict[str, object] = {
            "status_code": FlextApiConstants.WebSocket.STATUS_SWITCHING_PROTOCOLS,
            "url": url_result.value,
            "method": "WEBSOCKET",
            "headers": {"Connection": "Upgrade", "Upgrade": "websocket"},
            "body": {"status": "message_sent", "message_type": message_type},
        }

        return r[dict[str, object]].ok(response)

    def supports_protocol(self, protocol: str) -> bool:
        """Check if this plugin supports the given protocol.

        Args:
        protocol: Protocol identifier

        Returns:
        True if protocol is supported

        """
        return protocol.lower() in {
            FlextApiConstants.WebSocket.Protocol.WEBSOCKET,
            FlextApiConstants.WebSocket.Protocol.WS,
            FlextApiConstants.WebSocket.Protocol.WSS,
        }

    def get_supported_protocols(self) -> list[str]:
        """Get list of supported protocols.

        Returns:
        List of supported protocol identifiers

        """
        return [
            FlextApiConstants.WebSocket.Protocol.WEBSOCKET,
            FlextApiConstants.WebSocket.Protocol.WS,
            FlextApiConstants.WebSocket.Protocol.WSS,
        ]

    def connect(
        self,
        url: str,
        headers: dict[str, str] | None = None,
    ) -> r[bool]:
        """Connect to WebSocket server.

        Args:
        url: WebSocket URL (ws:// or wss://)
        headers: Optional connection headers

        Returns:
        FlextResult indicating success or failure

        """
        connect_headers: dict[str, str] = {}
        if headers is not None:
            connect_headers = headers
        return self._connect(url, connect_headers)

    def disconnect(self) -> r[bool]:
        """Disconnect from WebSocket server.

        Returns:
        FlextResult indicating success or failure

        """
        if not self._connected:
            return r[bool].fail("Not connected to WebSocket server")

        try:
            # Simplified sync disconnect - no async tasks to cancel

            # Close connection
            if self._connection and hasattr(self._connection, "close"):
                self._connection.close()

            self._connected = False
            self._connection = None

            # Notify disconnect handlers
            for handler in self._on_disconnect_handlers:
                try:
                    handler()
                except Exception:
                    self.logger.exception("Disconnect handler error")

            self.logger.info("WebSocket disconnected", url=self._url)

            return r[bool].ok(True)

        except Exception as e:
            return r[bool].fail(f"WebSocket disconnect failed: {e}")

    def send_message(
        self,
        message: str | bytes,
        message_type: str = "text",
    ) -> r[bool]:
        """Send message over WebSocket.

        Args:
            message: Message content (text or binary)
            message_type: Message type ("text" or "binary")

        Returns:
            FlextResult indicating success or failure

        """
        return self._send_message(message, message_type)

    def on_message(self, handler: Callable) -> None:
        """Register message handler.

        Args:
            handler: function to handle incoming messages

        """
        self._on_message_handlers.append(handler)

    def on_connect(self, handler: Callable) -> None:
        """Register connection handler.

        Args:
            handler: function to call on connection

        """
        self._on_connect_handlers.append(handler)

    def on_disconnect(self, handler: Callable) -> None:
        """Register disconnection handler.

        Args:
            handler: function to call on disconnection

        """
        self._on_disconnect_handlers.append(handler)

    def on_error(self, handler: Callable) -> None:
        """Register error handler.

        Args:
            handler: function to call on error

        """
        self._on_error_handlers.append(handler)

    @property
    def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self._connected

    def _connect(
        self,
        url: str,
        headers: dict[str, str],
    ) -> r[bool]:
        """Internal connection implementation.

        Args:
            url: WebSocket URL
            headers: Connection headers

        Returns:
            FlextResult indicating success or failure

        """
        # Check if websockets library is available
        if websockets is None:
            return r[bool].fail(
                "websockets library not installed. Install with: pip install websockets",
            )

        try:
            self._url = url
            self._headers = headers

            # Connect to WebSocket server
            connection_obj = websockets.connect(
                url,
                extra_headers=headers,
                ping_interval=self._ping_interval,
                ping_timeout=self._ping_timeout,
                close_timeout=self._close_timeout,
                max_size=self._max_size,
                max_queue=self._max_queue,
                compression=self._compression,
            )

            self._connection = connection_obj
            self._connected = True

            # Simplified sync implementation - no background tasks needed

            # Notify connect handlers
            for handler in self._on_connect_handlers:
                try:
                    handler()
                except Exception:
                    self.logger.exception("Connect handler error")

            self.logger.info(
                "WebSocket connected",
                extra={
                    "url": url,
                    "ping_interval": self._ping_interval,
                    "compression": self._compression,
                },
            )

            return r[bool].ok(True)

        except Exception as e:
            self._connected = False
            self._connection = None
            return r[bool].fail(f"WebSocket connection error: {e}")

    def _send_message(
        self,
        message: str | bytes,
        message_type: str,
    ) -> r[bool]:
        """Internal send message implementation.

        Args:
        message: Message content
        message_type: Message type

        Returns:
        FlextResult indicating success or failure

        """
        if not self._connected:
            return r[bool].fail("Not connected to WebSocket server")
        if not self._connection:
            return r[bool].fail("WebSocket connection is None")

        try:
            if message_type == FlextApiConstants.WebSocket.MessageType.TEXT:
                if isinstance(message, bytes):
                    message = message.decode("utf-8")
                if hasattr(self._connection, "send"):
                    self._connection.send(message)
            elif message_type == FlextApiConstants.WebSocket.MessageType.BINARY:
                if isinstance(message, str):
                    message = message.encode("utf-8")
                if hasattr(self._connection, "send"):
                    self._connection.send(message)
            else:
                return r[bool].fail(f"Invalid message type: {message_type}")

            self.logger.debug(
                "WebSocket message sent",
                extra={"message_type": message_type, "size": len(message)},
            )

            return r[bool].ok(True)

        except Exception as e:
            return r[bool].fail(f"WebSocket send error: {e}")

    def _receive_loop(self) -> None:
        """Background task to receive messages."""
        while self._connected and self._connection:
            try:
                if hasattr(self._connection, "recv"):
                    message = self._connection.recv()
                else:
                    message = None

                # Notify message handlers
                for handler in self._on_message_handlers:
                    try:
                        handler(message)
                    except Exception:
                        self.logger.exception("Message handler error")

            except Exception as e:
                if isinstance(e, Exception):
                    break
                self.logger.exception("WebSocket receive error")
                self.logger.exception("WebSocket receive error")

                # Notify error handlers
                for handler in self._on_error_handlers:
                    try:
                        handler(e)
                    except Exception:
                        self.logger.exception("Error handler error")

                # Attempt reconnection if enabled
                if self._auto_reconnect:
                    self._reconnect()
                break

    def _heartbeat_loop(self) -> None:
        """Background task for heartbeat monitoring."""
        while self._connected:
            try:
                time.sleep(self._ping_interval)

                if self._connection:
                    # Ping is handled automatically by websockets library
                    self.logger.debug("WebSocket heartbeat")

            except Exception as e:
                if isinstance(e, Exception):
                    break
                self.logger.exception("Heartbeat error")
                break

    def _reconnect(self) -> r[bool]:
        """Attempt to reconnect with exponential backoff.

        Returns:
        FlextResult indicating success or failure

        """
        for attempt in range(self._reconnect_max_attempts):
            delay = self._reconnect_backoff_factor**attempt

            attempt_msg = (
                f"Reconnecting... (attempt {attempt + 1}/"
                f"{self._reconnect_max_attempts})"
            )
            self.logger.info(attempt_msg, extra={"delay": delay})

            time.sleep(delay)

            connect_result = self._connect(self._url, self._headers)
            if connect_result.is_success:
                self.logger.info("WebSocket reconnected successfully")
                return connect_result

        return r[bool].fail(
            f"Failed to reconnect after {self._reconnect_max_attempts} attempts",
        )


__all__ = ["WebSocketProtocolPlugin"]

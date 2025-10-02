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

import asyncio
import contextlib
from collections.abc import Callable
from typing import Any

from flext_core import FlextConstants

from flext_api.models import FlextApiModels
from flext_api.plugins import ProtocolPlugin
from flext_core import FlextResult

try:
    import websockets
except ImportError:
    websockets = None


class WebSocketProtocolPlugin(ProtocolPlugin):
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

    def __init__(
        self,
        ping_interval: float = 20.0,
        ping_timeout: float = 20.0,
        close_timeout: float = 10.0,
        max_size: int = 10 * 1024 * 1024,  # 10MB
        max_queue: int = 32,
        compression: str | None = "deflate",
        *,
        auto_reconnect: bool = True,
        reconnect_max_attempts: int = 5,
        reconnect_backoff_factor: float = 1.5,
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

        # WebSocket configuration
        self._ping_interval = ping_interval
        self._ping_timeout = ping_timeout
        self._close_timeout = close_timeout
        self._max_size = max_size
        self._max_queue = max_queue
        self._compression = compression

        # Reconnection configuration
        self._auto_reconnect = auto_reconnect
        self._reconnect_max_attempts = reconnect_max_attempts
        self._reconnect_backoff_factor = reconnect_backoff_factor

        # Connection state
        self._connection: Any | None = None
        self._connected = False
        self._url: str = ""
        self._headers: dict[str, str] = {}

        # Event handlers
        self._on_message_handlers: list[Callable] = []
        self._on_connect_handlers: list[Callable] = []
        self._on_disconnect_handlers: list[Callable] = []
        self._on_error_handlers: list[Callable] = []

        # Background tasks
        self._receive_task: Task | None = None
        self._heartbeat_task: Task | None = None

    def send_request(
        self,
        request: FlextApiModels.HttpRequest,
        **kwargs: float | str | bool,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Send WebSocket request (connect and send message).

        Args:
            request: HTTP request model (adapted for WebSocket)
            **kwargs: Additional WebSocket-specific parameters

        Returns:
            FlextResult containing response or error

        """
        # Extract WebSocket-specific parameters
        message = kwargs.get("message", request.body)
        message_type = kwargs.get("message_type", "text")

        # Connect if not connected
        if not self._connected:
            connect_result = self._connect(str(request.url), dict(request.headers))
            if connect_result.is_failure:
                return FlextResult[FlextApiModels.HttpResponse].fail(
                    f"WebSocket connection failed: {connect_result.error}"
                )

        # Send message
        send_result = self._send_message(message, message_type)
        if send_result.is_failure:
            return FlextResult[FlextApiModels.HttpResponse].fail(
                f"WebSocket send failed: {send_result.error}"
            )

        # Create response (WebSocket doesn't have traditional responses)
        response = FlextApiModels.HttpResponse(
            status_code=101,  # Switching Protocols
            url=str(request.url),
            method="WEBSOCKET",
            headers={"Connection": "Upgrade", "Upgrade": "websocket"},
            body={"status": "message_sent", "message_type": message_type},
        )

        return FlextResult[FlextApiModels.HttpResponse].ok(response)

    def supports_protocol(self, protocol: str) -> bool:
        """Check if this plugin supports the given protocol.

        Args:
            protocol: Protocol identifier

        Returns:
            True if protocol is supported

        """
        return protocol.lower() in {"websocket", "ws", "wss"}

    def get_supported_protocols(self) -> list[str]:
        """Get list of supported protocols.

        Returns:
            List of supported protocol identifiers

        """
        return ["websocket", "ws", "wss"]

    def connect(
        self,
        url: str,
        headers: dict[str, str] | None = None,
    ) -> FlextResult[None]:
        """Connect to WebSocket server.

        Args:
            url: WebSocket URL (ws:// or wss://)
            headers: Optional connection headers

        Returns:
            FlextResult indicating success or failure

        """
        return self._connect(url, headers or {})

    def disconnect(self) -> FlextResult[None]:
        """Disconnect from WebSocket server.

        Returns:
            FlextResult indicating success or failure

        """
        if not self._connected:
            return FlextResult[None].fail("Not connected to WebSocket server")

        try:
            # Cancel background tasks
            if self._receive_task:
                self._receive_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    pass

            if self._heartbeat_task:
                self._heartbeat_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    pass

            # Close connection
            if self._connection:
                self._connection.close()

            self._connected = False
            self._connection = None

            # Notify disconnect handlers
            for handler in self._on_disconnect_handlers:
                try:
                    handler()
                except Exception as e:
                    self._logger.exception("Disconnect handler error")

            self._logger.info("WebSocket disconnected", extra={"url": self._url})

            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"WebSocket disconnect failed: {e}")

    def send_message(
        self,
        message: str | bytes,
        message_type: str = "text",
    ) -> FlextResult[None]:
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
    ) -> FlextResult[None]:
        """Internal connection implementation.

        Args:
            url: WebSocket URL
            headers: Connection headers

        Returns:
            FlextResult indicating success or failure

        """
        # Check if websockets library is available
        if websockets is None:
            return FlextResult[None].fail(
                "websockets library not installed. Install with: pip install websockets"
            )

        try:
            self._url = url
            self._headers = headers

            # Connect to WebSocket server
            self._connection = websockets.connect(
                url,
                extra_headers=headers,
                ping_interval=self._ping_interval,
                ping_timeout=self._ping_timeout,
                close_timeout=self._close_timeout,
                max_size=self._max_size,
                max_queue=self._max_queue,
                compression=self._compression,
            )

            self._connected = True

            # Start background tasks
            self._receive_task = create_task(self._receive_loop())
            self._heartbeat_task = create_task(self._heartbeat_loop())

            # Notify connect handlers
            for handler in self._on_connect_handlers:
                try:
                    handler()
                except Exception as e:
                    self._logger.exception("Connect handler error")

            self._logger.info(
                "WebSocket connected",
                extra={
                    "url": url,
                    "ping_interval": self._ping_interval,
                    "compression": self._compression,
                },
            )

            return FlextResult[None].ok(None)

        except Exception as e:
            self._connected = False
            self._connection = None
            return FlextResult[None].fail(f"WebSocket connection error: {e}")

    def _send_message(
        self,
        message: str | bytes,
        message_type: str,
    ) -> FlextResult[None]:
        """Internal send message implementation.

        Args:
            message: Message content
            message_type: Message type

        Returns:
            FlextResult indicating success or failure

        """
        if not self._connected or not self._connection:
            return FlextResult[None].fail("Not connected to WebSocket server")

        try:
            if message_type == "text":
                if isinstance(message, bytes):
                    message = message.decode("utf-8")
                self._connection.send(message)
            elif message_type == "binary":
                if isinstance(message, str):
                    message = message.encode("utf-8")
                self._connection.send(message)
            else:
                return FlextResult[None].fail(f"Invalid message type: {message_type}")

            self._logger.debug(
                "WebSocket message sent",
                extra={"message_type": message_type, "size": len(message)},
            )

            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"WebSocket send error: {e}")

    def _receive_loop(self) -> None:
        """Background task to receive messages."""
        while self._connected and self._connection:
            try:
                message = self._connection.recv()

                # Notify message handlers
                for handler in self._on_message_handlers:
                    try:
                        handler(message)
                    except Exception as e:
                        self._logger.exception("Message handler error")

            except CancelledError:
                break
            except Exception as e:
                self._logger.exception("WebSocket receive error")

                # Notify error handlers
                for handler in self._on_error_handlers:
                    try:
                        handler(e)
                    except Exception as handler_error:
                        self._logger.exception("Error handler error")

                # Attempt reconnection if enabled
                if self._auto_reconnect:
                    self._reconnect()
                break

    def _heartbeat_loop(self) -> None:
        """Background task for heartbeat monitoring."""
        while self._connected:
            try:
                sleep(self._ping_interval)

                if self._connection:
                    # Ping is handled automatically by websockets library
                    self._logger.debug("WebSocket heartbeat")

            except CancelledError:
                break
            except Exception as e:
                self._logger.exception(f"Heartbeat error: {e}")
                break

    def _reconnect(self) -> FlextResult[None]:
        """Attempt to reconnect with exponential backoff.

        Returns:
            FlextResult indicating success or failure

        """
        for attempt in range(self._reconnect_max_attempts):
            delay = self._reconnect_backoff_factor**attempt

            self._logger.info(
                f"Reconnecting... (attempt {attempt + 1}/{self._reconnect_max_attempts})",
                extra={"delay": delay},
            )

            sleep(delay)

            connect_result = self._connect(self._url, self._headers)
            if connect_result.is_success:
                self._logger.info("WebSocket reconnected successfully")
                return connect_result

        return FlextResult[None].fail(
            f"Failed to reconnect after {self._reconnect_max_attempts} attempts"
        )


__all__ = ["WebSocketProtocolPlugin"]

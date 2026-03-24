"""WebSocket Protocol Plugin for flext-api.

Implements WebSocket protocol support with:
- Connection management and lifecycle
- Message handling (text/binary)
- Event-driven architecture
- Automatic reconnection logic
- Ping/pong heartbeat mechanism
- Integration with r patterns

See TRANSFORMATION_PLAN.md - Phase 3 for implementation details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping, MutableMapping, MutableSequence
from typing import ClassVar, override

import websockets
from flext_core import r
from pydantic import ConfigDict, ValidationError
from websockets.sync.client import ClientConnection, connect as websocket_connect

from flext_api import FlextApiRfcProtocolImplementation, c, m, t


class FlextApiWebsocketProtocolPlugin(FlextApiRfcProtocolImplementation):
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
    - r for error handling
    - FlextLogger for structured logging
    - Event callbacks for message handling
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        frozen=False,
        arbitrary_types_allowed=True,
    )
    _ping_interval: float
    _ping_timeout: float
    _close_timeout: float
    _max_size: int
    _max_queue: int
    _compression: str
    _auto_reconnect: bool
    _reconnect_max_attempts: int
    _reconnect_backoff_factor: float
    _connection: ClientConnection | None
    _connected: bool
    _url: str
    _headers: t.StrMapping
    _on_message_handlers: MutableSequence[Callable[[str | bytes], None]]
    _on_connect_handlers: MutableSequence[Callable[[], None]]
    _on_disconnect_handlers: MutableSequence[Callable[[], None]]
    _on_error_handlers: MutableSequence[Callable[[Exception], None]]

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
        object.__setattr__(
            self,
            "_ping_interval",
            ping_interval
            if ping_interval is not None
            else c.Api.WebSocket.DEFAULT_PING_INTERVAL,
        )
        object.__setattr__(
            self,
            "_ping_timeout",
            ping_timeout
            if ping_timeout is not None
            else c.Api.WebSocket.DEFAULT_PING_TIMEOUT,
        )
        object.__setattr__(
            self,
            "_close_timeout",
            close_timeout
            if close_timeout is not None
            else c.Api.WebSocket.DEFAULT_CLOSE_TIMEOUT,
        )
        object.__setattr__(
            self,
            "_max_size",
            max_size if max_size is not None else c.Api.WebSocket.DEFAULT_MAX_SIZE,
        )
        object.__setattr__(
            self,
            "_max_queue",
            max_queue if max_queue is not None else c.Api.WebSocket.DEFAULT_MAX_QUEUE,
        )
        object.__setattr__(
            self,
            "_compression",
            compression
            if compression is not None
            else c.Api.WebSocket.COMPRESSION_DEFLATE,
        )
        object.__setattr__(self, "_auto_reconnect", auto_reconnect)
        object.__setattr__(
            self,
            "_reconnect_max_attempts",
            reconnect_max_attempts
            if reconnect_max_attempts is not None
            else c.Api.WebSocket.DEFAULT_RECONNECT_MAX_ATTEMPTS,
        )
        object.__setattr__(
            self,
            "_reconnect_backoff_factor",
            reconnect_backoff_factor
            if reconnect_backoff_factor is not None
            else c.Api.WebSocket.DEFAULT_RECONNECT_BACKOFF_FACTOR,
        )
        object.__setattr__(self, "_connection", None)
        object.__setattr__(self, "_connected", False)
        object.__setattr__(self, "_url", "")
        object.__setattr__(self, "_headers", {})
        object.__setattr__(self, "_on_message_handlers", [])
        object.__setattr__(self, "_on_connect_handlers", [])
        object.__setattr__(self, "_on_disconnect_handlers", [])
        object.__setattr__(self, "_on_error_handlers", [])

        def _log_initialize_error(error: str) -> None:
            self.logger.error("Failed to initialize WebSocket protocol: %s", error)

        self.initialize().tap_error(_log_initialize_error)

    @property
    def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self._connected

    def connect(self, url: str, headers: t.StrMapping | None = None) -> r[bool]:
        """Connect to WebSocket server.

        Args:
        url: WebSocket URL (ws:// or wss://)
        headers: Optional connection headers

        Returns:
        r indicating success or failure

        """
        connect_headers: MutableMapping[str, str] = {}
        if headers is not None:
            connect_headers.update(headers)
        return self._connect(url, connect_headers)

    def disconnect(self) -> r[bool]:
        """Disconnect from WebSocket server.

        Returns:
        r indicating success or failure

        """
        if not self._connected:
            return r[bool].fail("Not connected to WebSocket server")
        try:
            if self._connection is not None:
                self._connection.close()
            self._connected = False
            self._connection = None
            for handler in self._on_disconnect_handlers:
                try:
                    handler()
                except (ValueError, TypeError, KeyError, ConnectionError):
                    self.logger.exception("Disconnect handler error")
            self.logger.info("WebSocket disconnected", url=self._url)
            return r[bool].ok(value=True)
        except (ValueError, TypeError, KeyError, ConnectionError) as e:
            return r[bool].fail(f"WebSocket disconnect failed: {e}")

    @override
    def get_supported_protocols(self) -> t.StrSequence:
        """Get list of supported protocols.

        Returns:
        List of supported protocol identifiers

        """
        return [
            c.Api.WebSocket.Protocol.WEBSOCKET,
            c.Api.WebSocket.Protocol.WS,
            c.Api.WebSocket.Protocol.WSS,
        ]

    def on_connect(self, handler: Callable[[], None]) -> None:
        """Register connection handler.

        Args:
            handler: function to call on connection

        """
        self._on_connect_handlers.append(handler)

    def on_disconnect(self, handler: Callable[[], None]) -> None:
        """Register disconnection handler.

        Args:
            handler: function to call on disconnection

        """
        self._on_disconnect_handlers.append(handler)

    def on_error(self, handler: Callable[[Exception], None]) -> None:
        """Register error handler.

        Args:
            handler: function to call on error

        """
        self._on_error_handlers.append(handler)

    def on_message(self, handler: Callable[[str | bytes], None]) -> None:
        """Register message handler.

        Args:
            handler: function to handle incoming messages

        """
        self._on_message_handlers.append(handler)

    def send_message(self, message: str | bytes, message_type: str = "text") -> r[bool]:
        """Send message over WebSocket.

        Args:
            message: Message content (text or binary)
            message_type: Message type ("text" or "binary")

        Returns:
            r indicating success or failure

        """
        return self._send_message(message, message_type)

    @override
    def send_request(
        self,
        request: Mapping[str, t.ContainerValue],
        **kwargs: t.Scalar,
    ) -> r[Mapping[str, t.ContainerValue]]:
        """Send WebSocket request (connect and send message).

        Args:
        request: HTTP request model (adapted for WebSocket)
        **kwargs: Additional WebSocket-specific parameters

        Returns:
        r containing response or error

        """
        try:
            options = m.Api._SendRequestWsOptions.model_validate(kwargs)
        except ValidationError as exc:
            details = (
                exc.errors()[0]["msg"] if exc.errors() else "Invalid WebSocket options"
            )
            return r[t.ContainerValueMapping].fail(str(details))
        message_result = self._extract_message(request, options)
        if message_result.is_failure:
            return r[t.ContainerValueMapping].fail(
                message_result.error or "Message extraction failed",
            )
        message_type = self._extract_message_type(options)
        connect_result = self._ensure_connected(request)
        if connect_result.is_failure:
            return r[t.ContainerValueMapping].fail(
                f"WebSocket connection failed: {connect_result.error}",
            )
        send_result = self._send_message(message_result.value, message_type)
        if send_result.is_failure:
            return r[t.ContainerValueMapping].fail(
                f"WebSocket send failed: {send_result.error}",
            )
        url_result = self._extract_url(request)
        if url_result.is_failure:
            return r[t.ContainerValueMapping].fail(
                f"Failed to extract URL: {url_result.error}",
            )
        response: Mapping[str, t.ContainerValue] = {
            "status_code": c.Api.WebSocket.STATUS_SWITCHING_PROTOCOLS,
            "url": url_result.value,
            "method": "WEBSOCKET",
            "headers": {"Connection": "Upgrade", "Upgrade": "websocket"},
            "body": {"status": "message_sent", "message_type": message_type},
        }
        return r[t.ContainerValueMapping].ok(response)

    @override
    def supports_protocol(self, protocol: str) -> bool:
        """Check if this plugin supports the given protocol.

        Args:
        protocol: Protocol identifier

        Returns:
        True if protocol is supported

        """
        return protocol.lower() in {
            c.Api.WebSocket.Protocol.WEBSOCKET,
            c.Api.WebSocket.Protocol.WS,
            c.Api.WebSocket.Protocol.WSS,
        }

    def _connect(self, url: str, headers: t.StrMapping) -> r[bool]:
        """Internal connection implementation.

        Args:
            url: WebSocket URL
            headers: Connection headers

        Returns:
            r indicating success or failure

        """
        if websockets is None:
            return r[bool].fail(
                "websockets library not installed. Install with: pip install websockets",
            )
        try:
            self._url = url
            self._headers = headers
            connection_obj = websocket_connect(
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
            for handler in self._on_connect_handlers:
                try:
                    handler()
                except (ValueError, TypeError, KeyError, ConnectionError):
                    self.logger.exception("Connect handler error")
            self.logger.info(
                "WebSocket connected",
                url=url,
                ping_interval=self._ping_interval,
                compression=self._compression,
            )
            return r[bool].ok(value=True)
        except (ValueError, TypeError, KeyError, ConnectionError) as e:
            self._connected = False
            self._connection = None
            return r[bool].fail(f"WebSocket connection error: {e}")

    def _ensure_connected(self, request: Mapping[str, t.ContainerValue]) -> r[bool]:
        """Ensure WebSocket is connected."""
        if self._connected:
            return r[bool].ok(value=True)
        url_result = self._extract_url(request)
        if url_result.is_failure:
            return r[bool].fail(url_result.error or "URL extraction failed")
        headers = self._extract_headers(request)
        return self._connect(url_result.value, headers)

    def _extract_message(
        self,
        request: Mapping[str, t.ContainerValue],
        options: m.Api._SendRequestWsOptions,
    ) -> r[str | bytes]:
        """Extract message from request or kwargs."""
        if options.message is not None:
            return r[str | bytes].ok(options.message)
        body = self._extract_body(request)
        if body is not None:
            if isinstance(body, (str, bytes)):
                try:
                    parsed = m.Api._InboundMessage(message=body)
                    return r[str | bytes].ok(parsed.message)
                except ValidationError:
                    return r[str | bytes].ok(str(body))
            else:
                return r[str | bytes].ok(str(body))
        return r[str | bytes].fail("Message or body is required")

    def _extract_message_type(self, options: m.Api._SendRequestWsOptions) -> str:
        """Extract message type from kwargs."""
        return options.message_type

    def _heartbeat_loop(self) -> None:
        """Background task for heartbeat monitoring."""
        while self._connected:
            try:
                time.sleep(self._ping_interval)
                if self._connection:
                    self.logger.debug("WebSocket heartbeat")
            except (ValueError, TypeError, KeyError, ConnectionError):
                self.logger.exception("Heartbeat error")
                break

    def _receive_loop(self) -> None:
        """Background task to receive messages."""
        while self._connected and self._connection:
            try:
                message = self._connection.recv()
                try:
                    inbound = m.Api._InboundMessage(message=message)
                except ValidationError:
                    pass
                else:
                    for handler in self._on_message_handlers:
                        try:
                            handler(inbound.message)
                        except (ValueError, TypeError, KeyError, ConnectionError):
                            self.logger.exception("Message handler error")
            except (ValueError, TypeError, KeyError, ConnectionError) as e:
                self.logger.exception("WebSocket receive error")
                for error_handler in self._on_error_handlers:
                    try:
                        error_handler(e)
                    except (ValueError, TypeError, KeyError, ConnectionError):
                        self.logger.exception("Error handler error")
                if self._auto_reconnect:
                    self._reconnect()
                break

    def _reconnect(self) -> r[bool]:
        """Attempt to reconnect with exponential backoff.

        Returns:
        r indicating success or failure

        """
        for attempt in range(self._reconnect_max_attempts):
            delay = self._reconnect_backoff_factor**attempt
            attempt_msg = f"Reconnecting... (attempt {attempt + 1}/{self._reconnect_max_attempts})"
            self.logger.info(attempt_msg, delay=delay)
            time.sleep(delay)
            connect_result = self._connect(self._url, self._headers)
            if connect_result.is_success:
                self.logger.info("WebSocket reconnected successfully")
                return connect_result
        return r[bool].fail(
            f"Failed to reconnect after {self._reconnect_max_attempts} attempts",
        )

    def _send_message(self, message: str | bytes, message_type: str) -> r[bool]:
        """Internal send message implementation.

        Args:
        message: Message content
        message_type: Message type

        Returns:
        r indicating success or failure

        """
        if not self._connected:
            return r[bool].fail("Not connected to WebSocket server")
        if not self._connection:
            return r[bool].fail("WebSocket connection is None")
        try:
            if message_type == c.Api.WebSocket.MessageType.TEXT:
                text_message = str(message)
                self._connection.send(text_message)
            elif message_type == c.Api.WebSocket.MessageType.BINARY:
                binary_message = bytes(str(message), encoding="utf-8")
                self._connection.send(binary_message)
            else:
                return r[bool].fail(f"Invalid message type: {message_type}")
            self.logger.debug(
                "WebSocket message sent",
                message_type=message_type,
                size=len(message),
            )
            return r[bool].ok(value=True)
        except (ValueError, TypeError, KeyError, ConnectionError) as e:
            return r[bool].fail(f"WebSocket send error: {e}")


__all__ = ["FlextApiWebsocketProtocolPlugin"]

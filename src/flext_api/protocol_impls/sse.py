"""Server-Sent Events (SSE) Protocol Plugin for flext-api.

SSE protocol support currently not implemented - stub for future development.
All methods return NotImplementedError to indicate stub status.

See TRANSFORMATION_PLAN.md - Phase 3 for implementation details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable

from flext_api.models import FlextApiModels
from flext_api.plugins import ProtocolPlugin
from flext_core import FlextResult


class SSEProtocolPlugin(ProtocolPlugin):
    """Server-Sent Events protocol plugin (stub implementation).

    Features (planned for future implementation):
    - SSE event stream handling
    - Event parsing (id, event, data, retry)
    - Automatic reconnection with Last-Event-ID
    - Event type filtering
    - Retry handling with configurable delays
    - Connection state tracking
    - Error recovery and resilience

    Note:
        This is a stub implementation. All methods return errors indicating
        the feature is not yet implemented.

    """

    def __init__(
        self,
        retry_timeout: int = 3000,
        connect_timeout: float = 30.0,  # noqa: ARG002 - reserved for future SSE implementation
        read_timeout: float = 300.0,  # noqa: ARG002 - reserved for future SSE implementation
        *,
        auto_reconnect: bool = True,
        reconnect_max_attempts: int = 10,  # noqa: ARG002 - reserved for future SSE implementation
        reconnect_backoff_factor: float = 1.5,  # noqa: ARG002 - reserved for future SSE implementation
    ) -> None:
        """Initialize SSE protocol plugin stub.

        Args:
            retry_timeout: Default retry timeout in milliseconds (unused in stub)
            connect_timeout: Connection timeout in seconds (unused in stub)
            read_timeout: Read timeout in seconds (unused in stub)
            auto_reconnect: Enable automatic reconnection (unused in stub)
            reconnect_max_attempts: Maximum reconnection attempts (unused in stub)
            reconnect_backoff_factor: Reconnection backoff multiplier (unused in stub)

        """
        super().__init__(
            name="sse",
            version="1.0.0",
            description="Server-Sent Events protocol support (stub - not yet implemented)",
        )

        # Initialize stub attributes for testing
        self.is_connected = False
        self._connected = False
        self.last_event_id = ""
        self._on_event_handlers = {}
        self._on_connect_handlers = []
        self._on_disconnect_handlers = []
        self._on_error_handlers = []
        self._retry_timeout = retry_timeout
        self._auto_reconnect = auto_reconnect

    def send_request(
        self,
        request: FlextApiModels.HttpRequest,  # noqa: ARG002 - reserved for future SSE implementation
        **kwargs: float | str | bool,  # noqa: ARG002 - reserved for future SSE implementation
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Send SSE request (stub - not implemented).

        Args:
            request: HTTP request model (unused in stub)
            **kwargs: Additional SSE-specific parameters (unused in stub)

        Returns:
            FlextResult with error indicating not implemented

        """
        return FlextResult[FlextApiModels.HttpResponse].fail(
            "SSE protocol not yet implemented (Phase 3)"
        )

    def supports_protocol(self, protocol: str) -> bool:
        """Check if this plugin supports the given protocol.

        Args:
            protocol: Protocol identifier

        Returns:
            True if protocol is SSE variant

        """
        return protocol.lower() in {"sse", "server-sent-events", "eventsource"}

    def get_supported_protocols(self) -> list[str]:
        """Get list of supported protocols.

        Returns:
            List of supported protocol identifiers

        """
        return ["sse", "server-sent-events", "eventsource"]

    def on_event(self, event_type: str, handler: Callable[..., None]) -> None:
        """Register event handler (stub - not implemented)."""
        if event_type not in self._on_event_handlers:
            self._on_event_handlers[event_type] = []
        self._on_event_handlers[event_type].append(handler)

    def on_connect(self, handler: Callable[..., None]) -> None:
        """Register connect handler (stub - not implemented)."""
        self._on_connect_handlers.append(handler)

    def on_disconnect(self, handler: Callable[..., None]) -> None:
        """Register disconnect handler (stub - not implemented)."""
        self._on_disconnect_handlers.append(handler)

    def on_error(self, handler: Callable[..., None]) -> None:
        """Register error handler (stub - not implemented)."""
        self._on_error_handlers.append(handler)


__all__ = ["SSEProtocolPlugin"]

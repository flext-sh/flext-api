"""Server-Sent Events (SSE) Protocol Plugin for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time
from collections.abc import (
    Callable,
    MutableMapping,
    MutableSequence,
    Sequence,
)
from typing import override

import httpx
from httpx_sse import connect_sse

from flext_api import FlextApiRfcProtocolImplementation, c, m, p, r, t


class FlextApiSseProtocolPlugin(FlextApiRfcProtocolImplementation):
    """Server-Sent Events protocol plugin implementation."""

    connected: bool
    last_event_id: str
    _connected: bool
    _on_event_handlers: MutableMapping[str, MutableSequence[Callable[..., None]]]
    _on_connect_handlers: MutableSequence[Callable[[], None]]
    _on_disconnect_handlers: MutableSequence[Callable[[], None]]
    _on_error_handlers: MutableSequence[Callable[[Exception], None]]
    _retry_timeout: int
    _auto_reconnect: bool
    _connect_timeout: float
    _read_timeout: float
    _reconnect_max_attempts: int
    _reconnect_backoff_factor: float

    def __init__(
        self,
        retry_timeout: int | None = None,
        connect_timeout: float | None = None,
        read_timeout: float | None = None,
        *,
        auto_reconnect: bool = True,
        reconnect_max_attempts: int | None = None,
        reconnect_backoff_factor: float | None = None,
    ) -> None:
        """Initialize the SSE protocol plugin."""
        super().__init__(
            name="sse",
            version="1.0.0",
            description="Server-Sent Events protocol support with event stream handling",
        )
        object.__setattr__(self, "connected", False)
        object.__setattr__(self, "_connected", False)
        object.__setattr__(self, "last_event_id", "")
        object.__setattr__(self, "_on_event_handlers", {})
        object.__setattr__(self, "_on_connect_handlers", [])
        object.__setattr__(self, "_on_disconnect_handlers", [])
        object.__setattr__(self, "_on_error_handlers", [])
        object.__setattr__(
            self,
            "_retry_timeout",
            retry_timeout
            if retry_timeout is not None
            else c.Api.SSE.DEFAULT_RETRY_TIMEOUT,
        )
        object.__setattr__(self, "_auto_reconnect", auto_reconnect)
        object.__setattr__(
            self,
            "_connect_timeout",
            connect_timeout
            if connect_timeout is not None
            else c.Api.SSE.DEFAULT_CONNECT_TIMEOUT,
        )
        object.__setattr__(
            self,
            "_read_timeout",
            read_timeout
            if read_timeout is not None
            else c.Api.SSE.DEFAULT_READ_TIMEOUT,
        )
        object.__setattr__(
            self,
            "_reconnect_max_attempts",
            reconnect_max_attempts
            if reconnect_max_attempts is not None
            else c.Api.SSE.DEFAULT_RECONNECT_MAX_ATTEMPTS,
        )
        object.__setattr__(
            self,
            "_reconnect_backoff_factor",
            reconnect_backoff_factor
            if reconnect_backoff_factor is not None
            else c.Api.SSE.DEFAULT_RECONNECT_BACKOFF_FACTOR,
        )

        def _log_initialize_error(error: str) -> None:
            self.logger.error("Failed to initialize SSE protocol: %s", error)

        self.initialize().tap_error(_log_initialize_error)

    @override
    def supported_protocols(self) -> t.StrSequence:
        """Get list of supported protocols."""
        return [
            c.Api.SSE.Protocol.SSE,
            c.Api.SSE.Protocol.SERVER_SENT_EVENTS,
            c.Api.SSE.Protocol.EVENTSOURCE,
        ]

    def on_connect(self, handler: Callable[[], None]) -> None:
        """Register a handler to be called when connecting."""
        self._on_connect_handlers.append(handler)

    def on_disconnect(self, handler: Callable[[], None]) -> None:
        """Register a handler to be called when disconnected."""
        self._on_disconnect_handlers.append(handler)

    def on_error(self, handler: Callable[[Exception], None]) -> None:
        """Register a handler to be called on errors."""
        self._on_error_handlers.append(handler)

    def on_event(self, event_type: str, handler: Callable[..., None]) -> None:
        """Register a handler for a specific SSE event type."""
        self._on_event_handlers.setdefault(event_type, []).append(handler)

    @override
    def send_request(
        self,
        request: t.ContainerValueMapping,
        **kwargs: t.Scalar,
    ) -> p.Result[t.ContainerValueMapping]:
        """Send an SSE request and process the stream."""
        validation_result = self._validate_request(request)
        if validation_result.failure:
            return r[t.ContainerValueMapping].fail(
                validation_result.error or "Request validation failed",
            )
        try:
            options = m.Api.SendRequestSseOptions.model_validate(kwargs)
        except c.ValidationError as exc:
            details = exc.errors()[0]["msg"] if exc.errors() else "Invalid SSE options"
            return r[t.ContainerValueMapping].fail(details)
        url_result = self._extract_url(request)
        if url_result.failure:
            return r[t.ContainerValueMapping].fail(
                url_result.error or "URL extraction failed",
            )
        headers = dict(self._extract_headers(request))
        method = options.method.upper()
        max_events = options.max_events
        auto_reconnect = (
            options.auto_reconnect
            if options.auto_reconnect is not None
            else self._auto_reconnect
        )
        max_attempts = (
            options.reconnect_max_attempts
            if options.reconnect_max_attempts is not None
            else self._reconnect_max_attempts
        )
        backoff_factor = (
            options.reconnect_backoff_factor
            if options.reconnect_backoff_factor is not None
            else self._reconnect_backoff_factor
        )
        base_retry_timeout = (
            options.retry_timeout
            if options.retry_timeout is not None
            else self._retry_timeout
        )
        events: MutableSequence[t.ContainerValueMapping] = []
        retry_timeout_ms = base_retry_timeout
        attempts = 0
        while len(events) < max_events:
            connect_headers = dict(headers)
            if self.last_event_id:
                connect_headers["last-event-id"] = self.last_event_id
            try:
                stream_events, next_retry = self._consume_stream_once(
                    url=url_result.value,
                    method=method,
                    headers=connect_headers,
                    remaining=max_events - len(events),
                )
                events.extend(stream_events)
                if isinstance(next_retry, int) and next_retry >= 0:
                    retry_timeout_ms = next_retry
                if len(events) >= max_events:
                    break
                if not auto_reconnect or attempts >= max_attempts:
                    break
                attempts += 1
                self._sleep_before_reconnect(retry_timeout_ms, attempts, backoff_factor)
            except (
                ValueError,
                TypeError,
                KeyError,
                httpx.HTTPError,
                ConnectionError,
            ) as exc:
                self._notify_error_handlers(exc)
                if not auto_reconnect or attempts >= max_attempts:
                    return r[t.ContainerValueMapping].fail(
                        f"SSE stream failed: {exc}",
                    )
                attempts += 1
                self._sleep_before_reconnect(retry_timeout_ms, attempts, backoff_factor)
        response: t.ContainerValueMapping = {
            "status_code": 200,
            "url": url_result.value,
            "method": "SSE",
            "headers": headers,
            "body": {
                "events": events,
                "event_count": len(events),
                "last_event_id": self.last_event_id,
                "retry_timeout": retry_timeout_ms,
                "reconnect_attempts": attempts,
            },
        }
        return r[t.ContainerValueMapping].ok(response)

    @override
    def supports_protocol(self, protocol: str) -> bool:
        """Check if protocol is supported by this plugin."""
        protocol_lower = protocol.lower()
        return protocol_lower in {
            c.Api.SSE.Protocol.SSE,
            c.Api.SSE.Protocol.SERVER_SENT_EVENTS,
            c.Api.SSE.Protocol.EVENTSOURCE,
        }

    def _consume_stream_once(
        self,
        *,
        url: str,
        method: str,
        headers: t.StrMapping,
        remaining: int,
    ) -> t.Pair[Sequence[t.ContainerValueMapping], int | None]:
        timeout = httpx.Timeout(connect=self._connect_timeout, read=self._read_timeout)
        events: MutableSequence[t.ContainerValueMapping] = []
        retry_timeout: int | None = None
        self._update_connected_state(connected=True)
        self._notify_connect_handlers()
        try:
            with (
                httpx.Client(timeout=timeout) as client,
                connect_sse(client, method, url, headers=headers) as event_source,
            ):
                for event in event_source.iter_sse():
                    retry_raw = getattr(event, "retry", None)
                    parsed = self._parse_sse_event(
                        event_id=getattr(event, "id", ""),
                        event_type=getattr(event, "event", ""),
                        data=getattr(event, "data", ""),
                        retry=retry_raw if retry_raw is not None else "",
                    )
                    retry_timeout = self._extract_retry_timeout(parsed)
                    self._record_event_id(parsed)
                    self._notify_event_handlers(parsed)
                    events.append(parsed)
                    if len(events) >= remaining:
                        break
        finally:
            self._update_connected_state(connected=False)
            self._notify_disconnect_handlers()
        return (events, retry_timeout)

    def _extract_retry_timeout(
        self,
        event: t.ContainerValueMapping,
    ) -> int | None:
        retry_value = event.get("retry")
        if isinstance(retry_value, int) and retry_value >= 0:
            return retry_value
        return None

    def _notify_connect_handlers(self) -> None:
        for handler in self._on_connect_handlers:
            try:
                handler()
            except (ValueError, TypeError, KeyError, httpx.HTTPError, ConnectionError):
                self.logger.exception("SSE connect handler error")

    def _notify_disconnect_handlers(self) -> None:
        for handler in self._on_disconnect_handlers:
            try:
                handler()
            except (ValueError, TypeError, KeyError, httpx.HTTPError, ConnectionError):
                self.logger.exception("SSE disconnect handler error")

    def _notify_error_handlers(self, exc: Exception) -> None:
        for handler in self._on_error_handlers:
            try:
                handler(exc)
            except (ValueError, TypeError, KeyError, httpx.HTTPError, ConnectionError):
                self.logger.exception("SSE error handler error")

    def _notify_event_handlers(self, event: t.ContainerValueMapping) -> None:
        event_type_raw = event.get("event")
        event_type = event_type_raw if isinstance(event_type_raw, str) else "message"
        handlers = [*self._on_event_handlers.get(event_type, [])]
        handlers.extend(self._on_event_handlers.get("*", []))
        for handler in handlers:
            try:
                handler(event)
            except (ValueError, TypeError, KeyError, httpx.HTTPError, ConnectionError):
                self.logger.exception("SSE event handler error")

    def _parse_sse_event(
        self,
        *,
        event_id: t.Container,
        event_type: t.Container,
        data: t.Container,
        retry: t.Container,
    ) -> t.ContainerValueMapping:
        parsed_id = (
            "" if not event_id else t.Api.STRING_ADAPTER.validate_python(event_id)
        )
        parsed_type = (
            "message"
            if not event_type
            else t.Api.STRING_ADAPTER.validate_python(event_type)
        )
        parsed_data = "" if not data else t.Api.STRING_ADAPTER.validate_python(data)
        parsed_retry: int | None = None
        if retry not in {None, ""}:
            try:
                parsed_retry = t.Api.INTEGER_ADAPTER.validate_python(retry)
            except c.ValidationError:
                parsed_retry = None
        event_payload: t.MutableContainerValueMapping = {
            "id": parsed_id,
            "event": parsed_type,
            "data": parsed_data,
        }
        if parsed_retry is not None and parsed_retry >= 0:
            event_payload["retry"] = parsed_retry
        return event_payload

    def _record_event_id(self, event: t.ContainerValueMapping) -> None:
        event_id = event.get("id")
        if isinstance(event_id, str) and event_id:
            self.last_event_id = event_id

    def _update_connected_state(self, *, connected: bool) -> None:
        self._connected = connected
        self.connected = connected

    def _sleep_before_reconnect(
        self,
        retry_timeout_ms: int,
        attempt: int,
        backoff_factor: float,
    ) -> None:
        delay_seconds = (
            max(retry_timeout_ms, 0) / 1000.0 * backoff_factor ** (attempt - 1)
        )
        if delay_seconds > 0:
            time.sleep(delay_seconds)


__all__: list[str] = ["FlextApiSseProtocolPlugin"]

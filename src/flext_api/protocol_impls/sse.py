"""Server-Sent Events (SSE) Protocol Plugin for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time
from collections.abc import (
    Callable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)
from typing import override

import httpx
from flext_core import r
from httpx_sse import connect_sse
from pydantic import ValidationError

from flext_api import RFCProtocolImplementation, c, m, t


class SSEProtocolPlugin(RFCProtocolImplementation):
    """Server-Sent Events protocol plugin implementation."""

    is_connected: bool
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
        object.__setattr__(self, "is_connected", False)
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
    def get_supported_protocols(self) -> t.StrSequence:
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
        if event_type not in self._on_event_handlers:
            self._on_event_handlers[event_type] = []
        self._on_event_handlers[event_type].append(handler)

    @override
    def send_request(
        self,
        request: Mapping[str, t.ContainerValue],
        **kwargs: t.Scalar,
    ) -> r[Mapping[str, t.ContainerValue]]:
        """Send an SSE request and process the stream."""
        validation_result = self._validate_request(request)
        if validation_result.is_failure:
            return r[t.ContainerValueMapping].fail(
                validation_result.error or "Request validation failed",
            )
        try:
            options = m.Api._SendRequestSseOptions.model_validate(kwargs)
        except ValidationError as exc:
            details = exc.errors()[0]["msg"] if exc.errors() else "Invalid SSE options"
            return r[t.ContainerValueMapping].fail(str(details))
        url_result = self._extract_url(request)
        if url_result.is_failure:
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
        events: MutableSequence[Mapping[str, t.ContainerValue]] = []
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
        response: Mapping[str, t.ContainerValue] = {
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
    ) -> tuple[Sequence[Mapping[str, t.ContainerValue]], int | None]:
        timeout = httpx.Timeout(connect=self._connect_timeout, read=self._read_timeout)
        events: MutableSequence[Mapping[str, t.ContainerValue]] = []
        retry_timeout: int | None = None
        self._set_connected_state(connected=True)
        self._notify_connect_handlers()
        try:
            with (
                httpx.Client(timeout=timeout) as client,
                connect_sse(client, method, url, headers=headers) as event_source,
            ):
                for event in event_source.iter_sse():
                    parsed = self._parse_sse_event(
                        event_id=getattr(event, "id", ""),
                        event_type=getattr(event, "event", ""),
                        data=getattr(event, "data", ""),
                        retry=getattr(event, "retry", None),
                    )
                    retry_timeout = self._extract_retry_timeout(parsed)
                    self._record_event_id(parsed)
                    self._notify_event_handlers(parsed)
                    events.append(parsed)
                    if len(events) >= remaining:
                        break
        finally:
            self._set_connected_state(connected=False)
            self._notify_disconnect_handlers()
        return (events, retry_timeout)

    def _extract_retry_timeout(
        self,
        event: Mapping[str, t.ContainerValue],
    ) -> int | None:
        retry_value = event.get("retry")
        if isinstance(retry_value, int) and retry_value >= 0:
            return retry_value
        return None

    def _iter_fallback_events(
        self,
        lines: Iterator[str],
    ) -> Iterator[Mapping[str, t.ContainerValue]]:
        event_id = ""
        event_type = ""
        data_lines: MutableSequence[str] = []
        retry: int | None = None

        def flush_event() -> Mapping[str, t.ContainerValue] | None:
            if (
                not event_id
                and (not event_type)
                and (not data_lines)
                and (retry is None)
            ):
                return None
            return self._parse_sse_event(
                event_id=event_id,
                event_type=event_type,
                data="\n".join(data_lines),
                retry=retry,
            )

        for raw_line in lines:
            line = raw_line.rstrip("\r")
            if not line:
                payload = flush_event()
                if payload is not None:
                    yield payload
                event_id = ""
                event_type = ""
                data_lines = []
                retry = None
                continue
            if line.startswith(":"):
                continue
            field, separator, value = line.partition(":")
            if separator and value.startswith(" "):
                value = value[1:]
            if field == "data":
                data_lines.append(value)
            elif field == "event":
                event_type = value
            elif field == "id":
                if "\x00" not in value:
                    event_id = value
            elif field == "retry":
                try:
                    retry = int(value)
                except ValueError:
                    continue
        payload = flush_event()
        if payload is not None:
            yield payload

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

    def _notify_event_handlers(self, event: Mapping[str, t.ContainerValue]) -> None:
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
        event_id: t.ContainerValue,
        event_type: t.ContainerValue,
        data: t.ContainerValue,
        retry: t.ContainerValue,
    ) -> Mapping[str, t.ContainerValue]:
        parsed_id = str(event_id) if event_id is not None else ""
        parsed_type = str(event_type) if event_type else "message"
        parsed_data = "" if data is None else str(data)
        parsed_retry: int | None = None
        if retry is not None and isinstance(retry, (int, float, str)):
            try:
                parsed_retry = int(retry)
            except (TypeError, ValueError):
                parsed_retry = None
        event_payload: MutableMapping[str, t.ContainerValue] = {
            "id": parsed_id,
            "event": parsed_type,
            "data": parsed_data,
        }
        if parsed_retry is not None and parsed_retry >= 0:
            event_payload["retry"] = parsed_retry
        return event_payload

    def _record_event_id(self, event: Mapping[str, t.ContainerValue]) -> None:
        event_id = event.get("id")
        if isinstance(event_id, str) and event_id:
            self.last_event_id = event_id

    def _set_connected_state(self, *, connected: bool) -> None:
        self._connected = connected
        self.is_connected = connected

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


__all__ = ["SSEProtocolPlugin"]

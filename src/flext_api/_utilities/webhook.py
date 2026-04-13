"""Webhook handler backed by centralized Pydantic models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import hashlib
import hmac
import time
import uuid
from collections.abc import Mapping
from typing import override

from flext_api import m, p, r, t, u
from flext_core import s


class FlextWebhookHandler(s[bool]):
    """Webhook handler with centralized settings, event, delivery, and state models."""

    _settings: m.Api.Webhook.Settings
    _state: m.Api.Webhook.State

    def __init__(
        self,
        settings: m.Api.Webhook.Settings | Mapping[str, t.ValueOrModel] | None = None,
        **overrides: t.ValueOrModel,
    ) -> None:
        """Create one webhook handler from the canonical webhook settings model."""
        super().__init__()
        self._settings = self._resolve_webhook_settings(settings, overrides)
        self._state = m.Api.Webhook.State()

    @property
    def webhook_settings(self) -> m.Api.Webhook.Settings:
        """Return canonical webhook settings."""
        return self._settings

    @override
    def execute(self) -> p.Result[bool]:
        """Execute webhook lifecycle parity with other FLEXT services."""
        return r[bool].ok(True)

    def resolve_delivery_status(self, event_id: str) -> p.Result[t.JsonObject]:
        """Return one delivery status payload."""
        key_result = self._string_value(event_id)
        if key_result.failure:
            return r[t.JsonObject].fail(key_result.error or "Invalid event id")
        delivery = self._state.deliveries.get(key_result.value)
        if delivery is None:
            return r[t.JsonObject].fail(f"Event not found: {key_result.value}")
        return r[t.JsonObject].ok(self._delivery_payload(delivery))

    def queue_stats(self) -> t.JsonObject:
        """Return observable queue statistics."""
        return {
            "event_queue_size": self._state.event_queue_size,
            "retry_queue_size": self._state.retry_queue_size,
            "total_deliveries": self._state.total_deliveries,
            "successful_deliveries": self._state.successful_deliveries,
            "failed_deliveries": self._state.failed_deliveries,
        }

    def process_retry_queue(self) -> p.Result[t.JsonObject]:
        """Process all queued retries and report counts."""
        processed = 0
        failed = 0
        while self._state.retry_queue:
            event = self._state.retry_queue.pop(0)
            success, _should_retry = self._process_single_retry(event)
            if success:
                processed += 1
            else:
                failed += 1
        return r[t.JsonObject].ok({"processed": processed, "failed": failed})

    def receive_webhook(
        self,
        payload: bytes | str,
        headers: t.StrMapping,
    ) -> p.Result[t.JsonObject]:
        """Receive and process one webhook request."""
        if self._settings.secret is not None:
            signature_result = self._verify_signature(payload, headers)
            if signature_result.failure:
                return r[t.JsonObject].fail(
                    f"Signature verification failed: {signature_result.error}",
                )
        event_data_result = self._parse_payload(payload)
        if event_data_result.failure:
            return event_data_result
        event_result = self._build_event(event_data_result.value)
        if event_result.failure:
            return r[t.JsonObject].fail(
                event_result.error or "Webhook event validation failed",
            )
        event = event_result.value
        self._append_limited(
            self._state.event_queue,
            event,
            self._settings.queue_limit,
        )
        process_result = self._process_event(event)
        if process_result.success:
            return self._handle_processing_success(event)
        return self._handle_processing_failure(event, process_result)

    def register_event_handler(
        self,
        event_type: str,
        handler: t.Api.WebhookHandler,
    ) -> p.Result[bool]:
        """Register one handler for one event type."""
        event_type_result = self._string_value(event_type)
        if event_type_result.failure:
            return r[bool].fail(event_type_result.error or "Invalid event type")
        handlers = {key: list(value) for key, value in self._state.handlers.items()}
        handlers.setdefault(event_type_result.value, []).append(handler)
        self._state.handlers = handlers
        u.fetch_logger(__name__).info(
            "Event handler registered",
            event_type=event_type_result.value,
        )
        return r[bool].ok(True)

    @staticmethod
    def _append_limited[TItem](
        queue: list[TItem],
        item: TItem,
        limit: int,
    ) -> None:
        """Append one item to a bounded in-memory queue."""
        if len(queue) >= limit:
            queue.pop(0)
        queue.append(item)

    @staticmethod
    def _delivery_payload(
        delivery: m.Api.Webhook.Delivery,
    ) -> t.MutableContainerValueMapping:
        """Project one delivery model into the public payload."""
        payload: t.MutableContainerValueMapping = {
            "event_type": delivery.event_type,
            "timestamp": delivery.timestamp,
            "status": delivery.status,
        }
        if delivery.attempts is not None:
            payload["attempts"] = delivery.attempts
        if delivery.error is not None:
            payload["error"] = delivery.error
        return payload

    def _record_delivery(
        self,
        event_id: str,
        delivery: m.Api.Webhook.Delivery,
    ) -> None:
        """Persist one delivery update through the centralized state model."""
        deliveries = dict(self._state.deliveries)
        deliveries[event_id] = delivery
        self._state.deliveries = deliveries

    def _build_event(
        self,
        event_data: t.ContainerValueMapping,
    ) -> p.Result[m.Api.Webhook.Event]:
        """Build one canonical webhook event model."""
        event_type_result = self._resolve_event_type(event_data)
        if event_type_result.failure:
            return r[m.Api.Webhook.Event].fail(
                event_type_result.error or "Missing event type in payload",
            )
        return u.load(
            m.Api.Webhook.Event,
            {
                "id": self._resolve_event_id(event_data),
                "type": event_type_result.value,
                "data": event_data,
                "timestamp": time.time(),
                "attempts": 0,
            },
        )

    def _build_delivery(
        self,
        event: m.Api.Webhook.Event,
        *,
        status: str,
        error: str | None = None,
        attempts: int | None = None,
    ) -> m.Api.Webhook.Delivery:
        """Build one canonical delivery model."""
        delivery_result = u.load(
            m.Api.Webhook.Delivery,
            {
                "event_type": event.type,
                "timestamp": time.time(),
                "status": status,
                "attempts": attempts,
                "error": error,
            },
        )
        if delivery_result.failure:
            msg = delivery_result.error or "Webhook delivery validation failed"
            raise ValueError(msg)
        return delivery_result.value

    @staticmethod
    def _string_value(value: t.ValueOrModel | None) -> p.Result[str]:
        """Validate and normalize one string input."""
        value_result = u.validate_value(t.Api.STRING_ADAPTER, value)
        if value_result.failure:
            return r[str].fail(value_result.error or "Invalid string value")
        normalized = value_result.value.strip()
        if not normalized:
            return r[str].fail("Value must be a non-empty string")
        return r[str].ok(normalized)

    def _handle_processing_failure(
        self,
        event: m.Api.Webhook.Event,
        process_result: p.Result[bool],
    ) -> p.Result[t.JsonObject]:
        """Handle one failed event processing attempt."""
        if event.attempts < self._settings.max_retries:
            self._append_limited(
                self._state.retry_queue,
                event,
                self._settings.retry_queue_limit,
            )
            u.fetch_logger(__name__).warning(
                "Webhook processing failed, added to retry queue",
                event_id=event.id,
                event_type=event.type,
                error=process_result.error or "Webhook processing failed",
            )
            return r[t.JsonObject].ok({
                "event_id": event.id,
                "status": "queued_for_retry",
            })
        self._record_delivery(
            event.id,
            self._build_delivery(
                event,
                status="failed",
                error=process_result.error or "Webhook processing failed",
                attempts=event.attempts,
            ),
        )
        u.fetch_logger(__name__).error(
            "Webhook processing failed after max retries",
            event_id=event.id,
            event_type=event.type,
            error=process_result.error or "Webhook processing failed",
        )
        return r[t.JsonObject].fail(
            f"Processing failed: {process_result.error or 'Webhook processing failed'}",
        )

    def _handle_processing_success(
        self,
        event: m.Api.Webhook.Event,
    ) -> p.Result[t.JsonObject]:
        """Handle one successful event processing attempt."""
        self._record_delivery(
            event.id,
            self._build_delivery(
                event,
                status="delivered",
            ),
        )
        u.fetch_logger(__name__).info(
            "Webhook processed successfully",
            event_id=event.id,
            event_type=event.type,
        )
        return r[t.JsonObject].ok({"event_id": event.id, "status": "processed"})

    def _handle_successful_retry(self, event: m.Api.Webhook.Event) -> None:
        """Persist one successful retry delivery."""
        self._record_delivery(
            event.id,
            self._build_delivery(
                event,
                status="delivered_after_retry",
                attempts=event.attempts,
            ),
        )

    def _parse_payload(self, payload: bytes | str) -> p.Result[t.JsonObject]:
        """Parse and normalize one webhook payload."""
        payload_text = (
            payload.decode("utf-8") if isinstance(payload, bytes) else payload
        )
        event_data_result = u.validate_value(
            t.Api.CONTAINER_VALUE_ADAPTER,
            payload_text,
            from_json=True,
        )
        if event_data_result.failure:
            return r[t.JsonObject].fail(
                f"Failed to parse payload: {event_data_result.error}",
            )
        mapping_result = u.validate_value(
            t.Api.DICT_BODY_ADAPTER,
            event_data_result.value,
        )
        if mapping_result.failure:
            return r[t.JsonObject].fail("Payload must be a JSON object")
        return r[t.JsonObject].ok(dict(mapping_result.value))

    def _process_event(self, event: m.Api.Webhook.Event) -> p.Result[bool]:
        """Dispatch one event to registered handlers."""
        handlers = self._state.handlers.get(event.type, [])
        if not handlers:
            u.fetch_logger(__name__).warning(
                "No handlers registered for event type",
                event_type=event.type,
            )
            return r[bool].ok(True)
        for handler in handlers:
            try:
                outcome = handler(event.data)
            except (TypeError, ValueError, KeyError, AttributeError) as exc:
                return r[bool].fail(f"Handler execution failed: {exc}")
            if isinstance(outcome, p.Result) and outcome.failure:
                return r[bool].fail(outcome.error or "handler failed")
        return r[bool].ok(True)

    def _process_single_retry(
        self,
        event: m.Api.Webhook.Event,
    ) -> tuple[bool, bool]:
        """Process one queued retry event and report success/requeue status."""
        retry_event = event.model_copy(update={"attempts": event.attempts + 1})
        delay = self._settings.retry_delay * (
            self._settings.retry_backoff**event.attempts
        )
        u.fetch_logger(__name__).info(
            "Retrying event",
            event_id=retry_event.id,
            attempt=retry_event.attempts,
            delay=delay,
        )
        time.sleep(delay)
        process_result = self._process_event(retry_event)
        if process_result.success:
            self._handle_successful_retry(retry_event)
            return (True, False)
        if retry_event.attempts < self._settings.max_retries:
            self._append_limited(
                self._state.retry_queue,
                retry_event,
                self._settings.retry_queue_limit,
            )
            return (False, True)
        self._record_delivery(
            retry_event.id,
            self._build_delivery(
                retry_event,
                status="failed",
                error=process_result.error or "Webhook processing failed",
                attempts=retry_event.attempts,
            ),
        )
        return (False, False)

    def _resolve_event_id(self, event_data: t.ContainerValueMapping) -> str:
        """Resolve one event id, generating a UUID when absent."""
        event_id_result = self._string_value(event_data.get("id"))
        if event_id_result.success:
            return event_id_result.value
        return str(uuid.uuid4())

    def _resolve_event_type(
        self,
        event_data: t.ContainerValueMapping,
    ) -> p.Result[str]:
        """Resolve canonical event type from supported payload fields."""
        for key in ("type", "event_type"):
            event_type_result = self._string_value(event_data.get(key))
            if event_type_result.success:
                return event_type_result
        return r[str].fail("Missing event type in payload")

    def _resolve_webhook_settings(
        self,
        settings: m.Api.Webhook.Settings | Mapping[str, t.ValueOrModel] | None,
        overrides: Mapping[str, t.ValueOrModel],
    ) -> m.Api.Webhook.Settings:
        """Resolve one canonical webhook settings model."""
        if isinstance(settings, m.Api.Webhook.Settings):
            return settings.model_copy(update=dict(overrides) or None)
        payload: dict[str, t.ValueOrModel] = {}
        if isinstance(settings, Mapping):
            payload.update(settings)
        elif settings is not None:
            msg = "Webhook settings must be a mapping or Webhook.Settings model"
            raise TypeError(msg)
        payload.update(overrides)
        if not payload:
            return m.Api.Webhook.Settings()
        settings_result = u.load(
            m.Api.Webhook.Settings,
            t.ConfigMap(root=payload),
        )
        if settings_result.failure:
            msg = settings_result.error or "Webhook settings validation failed"
            raise ValueError(msg)
        return settings_result.value

    def _verify_signature(
        self,
        payload: bytes | str,
        headers: t.StrMapping,
    ) -> p.Result[bool]:
        """Verify webhook signature against the configured secret."""
        signature_value = headers.get(self._settings.signature_header)
        signature_result = self._string_value(signature_value)
        if signature_result.failure:
            return r[bool].fail(
                f"Missing signature header: {self._settings.signature_header}",
            )
        payload_bytes = (
            payload if isinstance(payload, bytes) else payload.encode("utf-8")
        )
        secret = self._settings.secret
        if secret is None:
            return r[bool].fail("Webhook secret is not configured")
        digest = (
            hashlib.sha256 if self._settings.algorithm == "sha256" else hashlib.sha512
        )
        expected = hmac.new(
            secret.encode("utf-8"),
            payload_bytes,
            digest,
        ).hexdigest()
        if not hmac.compare_digest(signature_result.value, expected):
            return r[bool].fail("Signature mismatch")
        return r[bool].ok(True)


__all__: list[str] = ["FlextWebhookHandler"]

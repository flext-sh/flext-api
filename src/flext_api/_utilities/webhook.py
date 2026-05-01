"""Webhook handler backed by centralized Pydantic models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import hashlib
import hmac
import time
import uuid
from collections.abc import (
    MutableMapping,
    MutableSequence,
)
from typing import override

from flext_api import c, m, p, r, s, t
from flext_web import u


class FlextApiWebhookHandler(s[bool]):
    """Webhook handler with centralized settings, event, delivery, and state models."""

    _settings: m.Api.Webhook.Settings = u.PrivateAttr()
    state: m.Api.Webhook.State = u.Field(
        default_factory=lambda: m.Api.Webhook.State(),
        description="Webhook runtime state",
    )

    def __init__(
        self,
        settings: m.Api.Webhook.Settings
        | t.MappingKV[str, t.JsonPayload]
        | None = None,
        **overrides: t.JsonPayload,
    ) -> None:
        """Create one webhook handler from the canonical webhook settings model."""
        super().__init__()
        existing_payload: dict[str, t.JsonPayload] = (
            dict(settings.model_dump())
            if isinstance(settings, m.Api.Webhook.Settings)
            else dict(settings or {})
        )
        self._settings = m.Api.Webhook.Settings.model_validate({
            **existing_payload,
            **overrides,
        })
        self.state = m.Api.Webhook.State()

    @property
    def webhook_settings(self) -> m.Api.Webhook.Settings:
        """Return canonical webhook settings."""
        return self._settings

    @override
    def execute(self) -> p.Result[bool]:
        """Execute webhook lifecycle parity with other FLEXT services."""
        return r[bool].ok(True)

    def resolve_delivery_status(self, event_id: str) -> p.Result[t.JsonMapping]:
        """Return one delivery status payload."""
        key_result = self._string_value(event_id)
        if key_result.failure:
            return r[t.JsonMapping].fail(key_result.error or "Invalid event id")
        delivery = self.state.deliveries.get(key_result.value)
        if delivery is None:
            return r[t.JsonMapping].fail(f"Event not found: {key_result.value}")
        return r[t.JsonMapping].ok(self._delivery_payload(delivery))

    def queue_stats(self) -> t.JsonMapping:
        """Return observable queue statistics."""
        return {
            "event_queue_size": self.state.event_queue_size,
            "retry_queue_size": self.state.retry_queue_size,
            "total_deliveries": self.state.total_deliveries,
            "successful_deliveries": self.state.successful_deliveries,
            "failed_deliveries": self.state.failed_deliveries,
        }

    def process_retry_queue(self) -> p.Result[t.JsonMapping]:
        """Process all queued retries and report counts."""
        processed = 0
        failed = 0
        while self.state.retry_queue:
            event = self.state.retry_queue.pop(0)
            success, _should_retry = self._process_single_retry(event)
            if success:
                processed += 1
            else:
                failed += 1
        return r[t.JsonMapping].ok({"processed": processed, "failed": failed})

    def receive_webhook(
        self,
        payload: bytes | str,
        headers: t.StrMapping,
    ) -> p.Result[t.JsonMapping]:
        """Receive and process one webhook request."""
        if self._settings.secret is not None:
            signature_result = self._verify_signature(payload, headers)
            if signature_result.failure:
                return r[t.JsonMapping].fail(
                    f"Signature verification failed: {signature_result.error}",
                )
        event_data_result = self._parse_payload(payload)
        if event_data_result.failure:
            return r[t.JsonMapping].fail(
                event_data_result.error or "Payload parse failed"
            )
        event_result = self._build_event(event_data_result.value)
        if event_result.failure:
            return r[t.JsonMapping].fail(
                event_result.error or "Webhook event validation failed",
            )
        event = event_result.value
        self._append_limited(
            self.state.event_queue,
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
        handlers: MutableMapping[str, MutableSequence[t.Api.WebhookHandler]] = {
            key: list(value) for key, value in self.state.handlers.items()
        }
        handlers.setdefault(event_type_result.value, []).append(handler)
        self.state.handlers = handlers
        u.fetch_logger(__name__).info(
            "Event handler registered",
            event_type=event_type_result.value,
        )
        return r[bool].ok(True)

    @staticmethod
    def _append_limited[TItem](
        queue: MutableSequence[TItem],
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
    ) -> t.JsonMapping:
        """Project one delivery model into the public payload."""
        return t.json_mapping_adapter().validate_python({
            "event_type": delivery.event_type,
            "timestamp": delivery.timestamp,
            "status": delivery.status,
            **(
                {"attempts": delivery.attempts} if delivery.attempts is not None else {}
            ),
            **({"error": delivery.error} if delivery.error is not None else {}),
        })

    def _record_delivery(
        self,
        event_id: str,
        delivery: m.Api.Webhook.Delivery,
    ) -> None:
        """Persist one delivery update through the centralized state model."""
        deliveries = dict(self.state.deliveries)
        deliveries[event_id] = delivery
        self.state.deliveries = deliveries

    def _build_event(
        self,
        event_data: t.JsonMapping,
    ) -> p.Result[m.Api.Webhook.Event]:
        """Build one canonical webhook event model."""
        event_type_result = self._resolve_event_type(event_data)
        if event_type_result.failure:
            return r[m.Api.Webhook.Event].fail(
                event_type_result.error or "Missing event type in payload",
            )
        return u.try_(
            lambda: m.Api.Webhook.Event.model_validate({
                "id": self._resolve_event_id(event_data),
                "type": event_type_result.value,
                "data": event_data,
                "timestamp": time.time(),
                "attempts": 0,
            }),
            catch=(c.ValidationError, ValueError, TypeError),
        ).map_error(lambda e: f"Webhook event validation failed: {e}")

    def _build_delivery(
        self,
        event: m.Api.Webhook.Event,
        *,
        status: str,
        error: str | None = None,
        attempts: int | None = None,
    ) -> m.Api.Webhook.Delivery:
        """Build one canonical delivery model."""
        delivery_payload: MutableMapping[str, t.JsonPayload] = {
            "event_type": event.type,
            "timestamp": time.time(),
            "status": status,
        }
        if attempts is not None:
            delivery_payload["attempts"] = attempts
        if error is not None:
            delivery_payload["error"] = error
        delivery_result = u.parse_model(delivery_payload, m.Api.Webhook.Delivery)
        if delivery_result.failure:
            msg = delivery_result.error or "Webhook delivery validation failed"
            raise ValueError(msg)
        return delivery_result.value

    @staticmethod
    def _string_value(value: t.JsonPayload | None) -> p.Result[str]:
        """Validate and normalize one string input."""
        if value is None:
            return r[str].fail("Invalid string value")
        value_result: p.Result[str] = u.validate_value(t.Api.STRING_ADAPTER, value)
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
    ) -> p.Result[t.JsonMapping]:
        """Handle one failed event processing attempt."""
        if event.attempts < self._settings.max_retries:
            self._append_limited(
                self.state.retry_queue,
                event,
                self._settings.retry_queue_limit,
            )
            u.fetch_logger(__name__).warning(
                "Webhook processing failed, added to retry queue",
                event_id=event.id,
                event_type=event.type,
                error=process_result.error or "Webhook processing failed",
            )
            return r[t.JsonMapping].ok({
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
        return r[t.JsonMapping].fail(
            f"Processing failed: {process_result.error or 'Webhook processing failed'}",
        )

    def _handle_processing_success(
        self,
        event: m.Api.Webhook.Event,
    ) -> p.Result[t.JsonMapping]:
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
        return r[t.JsonMapping].ok({"event_id": event.id, "status": "processed"})

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

    def _parse_payload(self, payload: bytes | str) -> p.Result[t.JsonMapping]:
        """Parse and normalize one webhook payload."""
        payload_text = (
            payload.decode(c.DEFAULT_ENCODING)
            if isinstance(payload, bytes)
            else payload
        )
        event_data_result: p.Result[t.JsonValue] = u.validate_value(
            t.Api.API_JSON_VALUE_ADAPTER,
            payload_text,
            from_json=True,
        )
        if event_data_result.failure:
            return r[t.JsonMapping].fail(
                f"Failed to parse payload: {event_data_result.error}",
            )
        mapping_result: p.Result[t.JsonMapping] = u.validate_value(
            t.Api.DICT_BODY_ADAPTER,
            event_data_result.value,
        )
        if mapping_result.failure:
            return r[t.JsonMapping].fail("Payload must be a JSON object")
        return r[t.JsonMapping].ok(mapping_result.value)

    def _process_event(self, event: m.Api.Webhook.Event) -> p.Result[bool]:
        """Dispatch one event to registered handlers."""
        handlers = self.state.handlers.get(event.type, [])
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
            if isinstance(outcome, p.ResultLike) and outcome.failure:
                return r[bool].fail(outcome.error or "handler failed")
        return r[bool].ok(True)

    def _process_single_retry(
        self,
        event: m.Api.Webhook.Event,
    ) -> t.Pair[bool, bool]:
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
                self.state.retry_queue,
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

    def _resolve_event_id(self, event_data: t.JsonMapping) -> str:
        """Resolve one event id, generating a UUID when absent."""
        event_id_result = self._string_value(event_data.get("id"))
        if event_id_result.success:
            return event_id_result.value
        return str(uuid.uuid4())

    def _resolve_event_type(
        self,
        event_data: t.JsonMapping,
    ) -> p.Result[str]:
        """Resolve canonical event type from supported payload fields."""
        for key in ("type", "event_type"):
            event_type_result = self._string_value(event_data.get(key))
            if event_type_result.success:
                return event_type_result
        return r[str].fail("Missing event type in payload")

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
            payload
            if isinstance(payload, bytes)
            else payload.encode(c.DEFAULT_ENCODING)
        )
        secret = self._settings.secret
        if secret is None:
            return r[bool].fail("Webhook secret is not configured")
        digest = (
            hashlib.sha256
            if self._settings.algorithm == c.Api.WebhookAlgorithm.SHA256.value
            else hashlib.sha512
        )
        expected = hmac.new(
            secret.encode(c.DEFAULT_ENCODING),
            payload_bytes,
            digest,
        ).hexdigest()
        if not hmac.compare_digest(signature_result.value, expected):
            return r[bool].fail("Signature mismatch")
        return r[bool].ok(True)


__all__: t.MutableSequenceOf[str] = ["FlextApiWebhookHandler"]

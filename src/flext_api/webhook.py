"""Webhook handler for flext-api.

Provides webhook functionality with:
- Webhook receiver with signature verification
- Event processing and routing
- Retry handling with exponential backoff
- Delivery confirmation tracking
- Event queue management
- Webhook registration and management

See TRANSFORMATION_PLAN.md - Phase 6 for implementation details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
import time as time_module
import uuid
from collections import deque
from collections.abc import Callable

from flext_core import (
    FlextContainer,
    FlextContext,
    FlextDispatcher,
    FlextService,
    r,
)

from flext_api.typings import t as t_api


class FlextWebhookHandler(FlextService[object]):
    """Webhook handler with signature verification and event processing.

    Features:
    - Webhook receiver with request validation
    - Signature verification (HMAC-SHA256, HMAC-SHA512)
    - Event processing and routing
    - Retry handling with exponential backoff
    - Delivery confirmation tracking
    - Event queue management
    - Webhook registration and lifecycle

    Integration:
    - Complete flext-core integration (FlextBus, FlextContainer, FlextContext, FlextDispatcher, u)
    - Signature verification using HMAC
    - Event routing to registered handlers
    - Retry queue with configurable attempts
    - FlextResult for railway-oriented error handling
    - FlextLogger for structured audit logging
    - FlextService for service lifecycle management
    - ual utility functions
    """

    # Declare attributes to satisfy type checkers
    # These are initialized directly in __init__() (no PrivateAttr needed)
    # Note: _container type matches parent FlextService (optional type)
    _flext_context: FlextContext
    _dispatcher: FlextDispatcher
    _secret: str | None
    _signature_header: str
    _algorithm: str
    _max_retries: int
    _retry_delay: float
    _retry_backoff: float
    _event_handlers: dict[str, list[Callable[..., None]]]
    _event_queue: deque[t_api.JsonObject]
    _delivery_confirmations: dict[str, t_api.JsonObject]
    _retry_queue: deque[t_api.JsonObject]

    def __init__(
        self,
        secret: str | None = None,
        signature_header: str = "X-Webhook-Signature",
        algorithm: str = "sha256",
        max_retries: int = 3,
        retry_delay: float = 1.0,
        retry_backoff: float = 2.0,
    ) -> None:
        """Initialize webhook handler.

        Args:
        secret: Webhook signing secret
        signature_header: HTTP header containing signature
        algorithm: HMAC algorithm (sha256, sha512)
        max_retries: Maximum retry attempts
        retry_delay: Initial retry delay in seconds
        retry_backoff: Retry backoff multiplier

        """
        super().__init__()

        # Initialize flext-core components
        # FlextContainer() returns singleton via __new__
        # Set attributes directly (no PrivateAttr needed, compatible with FlextService)
        self._container = FlextContainer()
        self._flext_context = FlextContext()
        self._dispatcher = FlextDispatcher()

        # Webhook configuration
        self._secret = secret
        self._signature_header = signature_header
        self._algorithm = algorithm
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._retry_backoff = retry_backoff

        # Event handlers
        self._event_handlers = {}

        # Event queue
        self._event_queue = deque(maxlen=1000)

        # Delivery tracking
        self._delivery_confirmations = {}

        # Retry queue
        self._retry_queue = deque(maxlen=500)

    def execute(self, **_kwargs: object) -> r[object]:
        """Execute webhook service lifecycle operations.

        FlextService requires this method for service execution.
        For webhook handler, this is a no-op as webhook processing is event-driven.

        Returns:
        r[object]: Success result

        """
        return r[object].ok(True)

    def register_event_handler(
        self,
        event_type: str,
        handler: Callable,
    ) -> r[bool]:
        """Register event handler for webhook events.

        Args:
            event_type: Event type to handle (e.g., "user.created")
            handler: Event handler function

        Returns:
            FlextResult indicating success or failure

        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []

        self._event_handlers[event_type].append(handler)

        self.logger.info(
            "Event handler registered",
            extra={"event_type": event_type},
        )

        return r[bool].ok(True)

    def _parse_payload(self, payload: bytes | str) -> r[t_api.JsonObject]:
        """Parse webhook payload."""
        try:
            if isinstance(payload, bytes):
                payload_str = payload.decode("utf-8")
            else:
                payload_str = payload

            event_data = json.loads(payload_str)
            if not isinstance(event_data, dict):
                return r[t_api.JsonObject].fail("Payload must be a JSON object")
            # Convert to JsonObject (dict[str, JsonValue])
            json_object: t_api.JsonObject = {}
            for key, value in event_data.items():
                if isinstance(value, (str, int, float, bool, type(None), list, dict)):
                    json_object[key] = value
                else:
                    json_object[key] = str(value)
            return r[t_api.JsonObject].ok(json_object)
        except Exception as e:
            return r[t_api.JsonObject].fail(f"Failed to parse payload: {e}")

    def _extract_event_type(self, event_data: t_api.JsonObject) -> r[str]:
        """Extract event type from event data."""
        event_type: str | None = None
        if "type" in event_data:
            type_value = event_data["type"]
            if isinstance(type_value, str):
                event_type = type_value
        if not event_type and "event_type" in event_data:
            event_type_value = event_data["event_type"]
            if isinstance(event_type_value, str):
                event_type = event_type_value
        if not event_type:
            return r[str].fail("Missing event type in payload")
        return r[str].ok(event_type)

    def _extract_event_id(self, event_data: t_api.JsonObject) -> str:
        """Extract or generate event ID."""
        if "id" in event_data:
            id_value = event_data["id"]
            if isinstance(id_value, str):
                return id_value
        return self._generate_event_id()

    def _handle_processing_success(
        self,
        event_id: str,
        event_type: str,
    ) -> r[t_api.JsonObject]:
        """Handle successful event processing."""
        confirmation: t_api.JsonObject = {
            "event_type": event_type,
            "timestamp": time.time(),
            "status": "delivered",
        }
        self._delivery_confirmations[event_id] = confirmation

        self.logger.info(
            "Webhook processed successfully",
            extra={"event_id": event_id, "event_type": event_type},
        )

        return r[t_api.JsonObject].ok(
            {
                "event_id": event_id,
                "status": "processed",
            }
        )

    def _handle_processing_failure(
        self,
        event: t_api.JsonObject,
        event_id: str,
        event_type: str,
        process_result: r[bool],
    ) -> r[t_api.JsonObject]:
        """Handle failed event processing."""
        attempts_value: int = 0
        if "attempts" in event:
            attempts_raw = event["attempts"]
            if isinstance(attempts_raw, int):
                attempts_value = attempts_raw

        if attempts_value < self._max_retries:
            self._retry_queue.append(event)

            self.logger.warning(
                "Webhook processing failed, added to retry queue",
                extra={
                    "event_id": event_id,
                    "event_type": event_type,
                    "error": process_result.error,
                },
            )

            return r[t_api.JsonObject].ok(
                {
                    "event_id": event_id,
                    "status": "queued_for_retry",
                }
            )

        # Max retries exceeded
        failure_confirmation: t_api.JsonObject = {
            "event_type": event_type,
            "timestamp": time.time(),
            "status": "failed",
        }
        if process_result.error:
            failure_confirmation["error"] = process_result.error
        self._delivery_confirmations[event_id] = failure_confirmation

        self.logger.error(
            "Webhook processing failed after max retries",
            extra={
                "event_id": event_id,
                "event_type": event_type,
                "error": process_result.error,
            },
        )

        return r[t_api.JsonObject].fail(
            f"Processing failed: {process_result.error}",
        )

    def receive_webhook(
        self,
        payload: bytes | str,
        headers: dict[str, str],
    ) -> r[t_api.JsonObject]:
        """Receive and process webhook request.

        Args:
        payload: Webhook payload
        headers: HTTP headers

        Returns:
        FlextResult containing processing result or error

        """
        # Verify signature if secret is configured
        if self._secret:
            signature_result = self._verify_signature(payload, headers)
            if signature_result.is_failure:
                return r[t_api.JsonObject].fail(
                    f"Signature verification failed: {signature_result.error}",
                )

        # Parse payload
        parse_result = self._parse_payload(payload)
        if parse_result.is_failure:
            return parse_result
        event_data = parse_result.unwrap()

        # Extract event type
        event_type_result = self._extract_event_type(event_data)
        if event_type_result.is_failure:
            return r[t_api.JsonObject].fail(
                event_type_result.error or "Event type extraction failed",
            )
        event_type = event_type_result.unwrap()

        # Generate event ID
        event_id = self._extract_event_id(event_data)

        # Add to event queue
        event: t_api.JsonObject = {
            "id": event_id,
            "type": event_type,
            "data": event_data,
            "timestamp": time.time(),
            "attempts": 0,
        }
        self._event_queue.append(event)

        # Process event
        process_result = self._process_event(event)

        if process_result.is_success:
            return self._handle_processing_success(event_id, event_type)

        return self._handle_processing_failure(
            event,
            event_id,
            event_type,
            process_result,
        )

    def _verify_signature(
        self,
        payload: bytes | str,
        headers: dict[str, str],
    ) -> r[bool]:
        """Verify webhook signature.

        Args:
        payload: Webhook payload
        headers: HTTP headers

        Returns:
        FlextResult indicating verification success or failure

        """
        # Get signature from headers
        if self._signature_header not in headers:
            return r[bool].fail(f"Missing signature header: {self._signature_header}")

        signature_value = headers[self._signature_header]
        if not isinstance(signature_value, str) or not signature_value:
            return r[bool].fail(
                f"Invalid signature header value: {self._signature_header}",
            )

        signature: str = signature_value

        # Convert payload to bytes if needed
        payload_bytes = payload.encode("utf-8") if isinstance(payload, str) else payload

        # Compute expected signature
        try:
            if self._secret is None:
                return r[bool].fail("Webhook secret is not configured")

            secret_bytes = self._secret.encode("utf-8")
            if self._algorithm == "sha256":
                expected = hmac.new(
                    secret_bytes,
                    payload_bytes,
                    hashlib.sha256,
                ).hexdigest()
            elif self._algorithm == "sha512":
                expected = hmac.new(
                    secret_bytes,
                    payload_bytes,
                    hashlib.sha512,
                ).hexdigest()
            else:
                return r[bool].fail(f"Unsupported algorithm: {self._algorithm}")

            # Compare signatures (constant-time comparison)
            if not hmac.compare_digest(signature, expected):
                return r[bool].fail("Signature mismatch")

            return r[bool].ok(True)

        except Exception as e:
            return r[bool].fail(f"Signature verification error: {e}")

    def _process_event(
        self,
        event: t_api.JsonObject,
    ) -> r[bool]:
        """Process webhook event.

        Args:
        event: Event dictionary

        Returns:
        FlextResult indicating processing success or failure

        """
        # Extract event type with type narrowing
        event_type_value = event.get("type")
        if not isinstance(event_type_value, str):
            return r[bool].fail("Event type must be a string")
        event_type: str = event_type_value

        event_data = event.get("data", {})

        # Get handlers for event type
        handlers: list[Callable[..., None]] = []
        if event_type in self._event_handlers:
            handlers_value = self._event_handlers[event_type]
            if isinstance(handlers_value, list):
                handlers = handlers_value

        if not handlers:
            self.logger.warning(
                "No handlers registered for event type",
                extra={"event_type": event_type},
            )
            return r[bool].ok(True)

        # Execute handlers
        for handler in handlers:
            try:
                result = handler(event_data)
                if isinstance(result, r) and result.is_failure:
                    return result
            except Exception as e:
                return r[bool].fail(f"Handler execution failed: {e}")

        return r[bool].ok(True)

    def _get_attempts_count(self, event: t_api.JsonObject) -> int:
        """Extract attempts count from event with type safety."""
        if (attempts_raw := event.get("attempts")) is not None and isinstance(
            attempts_raw,
            int,
        ):
            return attempts_raw
        return 0

    def _handle_successful_retry(self, event: t_api.JsonObject) -> None:
        """Handle successful retry delivery."""
        if (event_id := event.get("id")) is not None and isinstance(event_id, str):
            event_type = "unknown"
            if (type_value := event.get("type")) is not None and isinstance(
                type_value,
                str,
            ):
                event_type = type_value

            attempts_count = self._get_attempts_count(event)
            self._delivery_confirmations[event_id] = {
                "event_type": event_type,
                "timestamp": time.time(),
                "status": "delivered_after_retry",
                "attempts": attempts_count,
            }

    def _should_retry_event(self, event: t_api.JsonObject) -> bool:
        """Determine if event should be retried."""
        return self._get_attempts_count(event) < self._max_retries

    def _process_single_retry(
        self,
        event: t_api.JsonObject,
    ) -> tuple[bool, bool]:
        """Process a single retry event. Returns (success, should_retry)."""
        attempts_value = self._get_attempts_count(event)
        event["attempts"] = attempts_value + 1
        delay = self._retry_delay * (self._retry_backoff**attempts_value)

        self.logger.info(
            "Retrying event",
            extra={
                "event_id": event["id"],
                "attempt": event["attempts"],
                "delay": delay,
            },
        )

        time_module.sleep(delay)
        process_result = self._process_event(event)

        if process_result.is_success:
            self._handle_successful_retry(event)
            return (True, False)

        should_retry = self._should_retry_event(event)
        if should_retry:
            self._retry_queue.append(event)

        return (False, should_retry)

    def process_retry_queue(self) -> r[t_api.JsonObject]:
        """Process events in retry queue.

        Returns:
        FlextResult containing processing statistics

        """
        processed = 0
        failed = 0

        while self._retry_queue:
            event = self._retry_queue.popleft()
            success, _should_retry = self._process_single_retry(event)
            if success:
                processed += 1
            else:
                failed += 1

        return r[t_api.JsonObject].ok(
            {
                "processed": processed,
                "failed": failed,
            }
        )

    def _generate_event_id(self) -> str:
        """Generate unique event ID.

        Returns:
        Event ID string

        """
        return str(uuid.uuid4())

    def get_delivery_status(
        self,
        event_id: str,
    ) -> r[t_api.JsonObject]:
        """Get delivery status for event.

        Args:
        event_id: Event ID

        Returns:
        FlextResult containing delivery status or error

        """
        if event_id not in self._delivery_confirmations:
            return r[t_api.JsonObject].fail(f"Event not found: {event_id}")

        return r[t_api.JsonObject].ok(self._delivery_confirmations[event_id])

    def get_queue_stats(self) -> t_api.JsonObject:
        """Get event queue statistics.

        Returns:
        Dictionary containing queue statistics

        """
        return {
            "event_queue_size": len(self._event_queue),
            "retry_queue_size": len(self._retry_queue),
            "total_deliveries": len(self._delivery_confirmations),
            "successful_deliveries": sum(
                1
                for conf in self._delivery_confirmations.values()
                if isinstance(conf, dict)
                and conf["status"] in {"delivered", "delivered_after_retry"}
            ),
            "failed_deliveries": sum(
                1
                for conf in self._delivery_confirmations.values()
                if isinstance(conf, dict) and conf["status"] == "failed"
            ),
        }


__all__ = ["FlextWebhookHandler"]

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
from typing import Any

from flext_core import (
    FlextBus,
    FlextContainer,
    FlextContext,
    FlextDispatcher,
    FlextResult,
    FlextService,
    FlextTypes,
)


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
    - Complete flext-core integration (FlextBus, FlextContainer, FlextContext, FlextDispatcher, FlextUtilities)
    - Signature verification using HMAC
    - Event routing to registered handlers
    - Retry queue with configurable attempts
    - FlextResult for railway-oriented error handling
    - FlextLogger for structured audit logging
    - FlextService for service lifecycle management
    - FlextUtilities for additional utility functions
    """

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
        self._container = FlextContainer.get_global()
        self._context = FlextContext()
        self._bus = FlextBus()
        self._dispatcher = FlextDispatcher()

        # Webhook configuration
        self._secret = secret
        self._signature_header = signature_header
        self._algorithm = algorithm
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._retry_backoff = retry_backoff

        # Event handlers
        self._event_handlers: dict[str, list[Callable]] = {}

        # Event queue
        self._event_queue: deque[dict[str, Any]] = deque(maxlen=1000)

        # Delivery tracking
        self._delivery_confirmations: FlextTypes.NestedDict = {}

        # Retry queue
        self._retry_queue: deque[dict[str, Any]] = deque(maxlen=500)

    def execute(self, *_args: object, **_kwargs: object) -> FlextResult[object]:
        """Execute webhook service lifecycle operations.

        FlextService requires this method for service execution.
        For webhook handler, this is a no-op as webhook processing is event-driven.

        Returns:
        FlextResult[object]: Success result

        """
        return FlextResult[object].ok(None)

    def register_event_handler(
        self,
        event_type: str,
        handler: Callable,
    ) -> FlextResult[None]:
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

        return FlextResult[None].ok(None)

    def receive_webhook(
        self,
        payload: bytes | str,
        headers: dict[str, str],
    ) -> FlextResult[dict[str, Any]]:
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
                return FlextResult[dict[str, Any]].fail(
                    f"Signature verification failed: {signature_result.error}"
                )

        # Parse payload
        try:
            if isinstance(payload, bytes):
                payload_str = payload.decode("utf-8")
            else:
                payload_str = payload

            event_data = json.loads(payload_str)
        except Exception as e:
            return FlextResult[dict[str, Any]].fail(f"Failed to parse payload: {e}")

        # Extract event type
        event_type = event_data.get("type") or event_data.get("event_type")
        if not event_type:
            return FlextResult[dict[str, Any]].fail("Missing event type in payload")

        # Generate event ID
        event_id = event_data.get("id") or self._generate_event_id()

        # Add to event queue
        event = {
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
            # Track delivery confirmation
            self._delivery_confirmations[event_id] = {
                "event_type": event_type,
                "timestamp": time.time(),
                "status": "delivered",
            }

            self.logger.info(
                "Webhook processed successfully",
                extra={"event_id": event_id, "event_type": event_type},
            )

            return FlextResult[dict[str, Any]].ok({
                "event_id": event_id,
                "status": "processed",
            })
        # Add to retry queue
        attempts = event.get("attempts", 0)
        if isinstance(attempts, int) and attempts < self._max_retries:
            self._retry_queue.append(event)

            self.logger.warning(
                "Webhook processing failed, added to retry queue",
                extra={
                    "event_id": event_id,
                    "event_type": event_type,
                    "error": process_result.error,
                },
            )

            return FlextResult[dict[str, Any]].ok({
                "event_id": event_id,
                "status": "queued_for_retry",
            })
        # Max retries exceeded
        self._delivery_confirmations[event_id] = {
            "event_type": event_type,
            "timestamp": time.time(),
            "status": "failed",
            "error": process_result.error,
        }

        self.logger.error(
            "Webhook processing failed after max retries",
            extra={
                "event_id": event_id,
                "event_type": event_type,
                "error": process_result.error,
            },
        )

        return FlextResult[dict[str, Any]].fail(
            f"Processing failed: {process_result.error}"
        )

    def _verify_signature(
        self,
        payload: bytes | str,
        headers: dict[str, str],
    ) -> FlextResult[None]:
        """Verify webhook signature.

        Args:
        payload: Webhook payload
        headers: HTTP headers

        Returns:
        FlextResult indicating verification success or failure

        """
        # Get signature from headers
        signature = headers.get(self._signature_header)
        if not signature:
            return FlextResult[None].fail(
                f"Missing signature header: {self._signature_header}"
            )

        # Convert payload to bytes if needed
        payload_bytes = payload.encode("utf-8") if isinstance(payload, str) else payload

        # Compute expected signature
        try:
            if self._secret is None:
                return FlextResult[None].fail("Webhook secret is not configured")

            secret_bytes = self._secret.encode("utf-8")
            if self._algorithm == "sha256":
                expected = hmac.new(
                    secret_bytes, payload_bytes, hashlib.sha256
                ).hexdigest()
            elif self._algorithm == "sha512":
                expected = hmac.new(
                    secret_bytes, payload_bytes, hashlib.sha512
                ).hexdigest()
            else:
                return FlextResult[None].fail(
                    f"Unsupported algorithm: {self._algorithm}"
                )

            # Compare signatures (constant-time comparison)
            if not hmac.compare_digest(signature, expected):
                return FlextResult[None].fail("Signature mismatch")

            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Signature verification error: {e}")

    def _process_event(
        self,
        event: dict[str, Any],
    ) -> FlextResult[None]:
        """Process webhook event.

        Args:
        event: Event dictionary

        Returns:
        FlextResult indicating processing success or failure

        """
        event_type = event["type"]
        event_data = event["data"]

        # Get handlers for event type
        handlers = self._event_handlers.get(event_type, [])
        if not isinstance(handlers, list):
            handlers = []

        if not handlers:
            self.logger.warning(
                "No handlers registered for event type",
                extra={"event_type": event_type},
            )
            return FlextResult[None].ok(None)

        # Execute handlers
        for handler in handlers:
            try:
                result = handler(event_data)
                if isinstance(result, FlextResult) and result.is_failure:
                    return result
            except Exception as e:
                return FlextResult[None].fail(f"Handler execution failed: {e}")

        return FlextResult[None].ok(None)

    def process_retry_queue(self) -> FlextResult[dict[str, Any]]:
        """Process events in retry queue.

        Returns:
        FlextResult containing processing statistics

        """
        processed = 0
        failed = 0

        while self._retry_queue:
            event = self._retry_queue.popleft()
            attempts = event.get("attempts", 0)
            if isinstance(attempts, int):
                event["attempts"] = attempts + 1
                # Calculate retry delay
                delay = self._retry_delay * (self._retry_backoff**attempts)
            else:
                # Skip invalid event
                continue

            self.logger.info(
                "Retrying event",
                extra={
                    "event_id": event["id"],
                    "attempt": event["attempts"],
                    "delay": delay,
                },
            )

            # Wait before retry

            time_module.sleep(delay)

            # Retry processing
            process_result = self._process_event(event)

            if process_result.is_success:
                processed += 1
                event_id = event.get("id")
                if isinstance(event_id, str):
                    self._delivery_confirmations[event_id] = {
                        "event_type": event.get("type", "unknown"),
                        "timestamp": time.time(),
                        "status": "delivered_after_retry",
                        "attempts": event.get("attempts", 1),
                    }
            else:
                failed += 1
                attempts = event.get("attempts", 0)
                if isinstance(attempts, int) and attempts < self._max_retries:
                    # Re-add to retry queue
                    self._retry_queue.append(event)

        return FlextResult[dict[str, Any]].ok({
            "processed": processed,
            "failed": failed,
        })

    def _generate_event_id(self) -> str:
        """Generate unique event ID.

        Returns:
        Event ID string

        """
        return str(uuid.uuid4())

    def get_delivery_status(
        self,
        event_id: str,
    ) -> FlextResult[dict[str, Any]]:
        """Get delivery status for event.

        Args:
        event_id: Event ID

        Returns:
        FlextResult containing delivery status or error

        """
        if event_id not in self._delivery_confirmations:
            return FlextResult[dict[str, Any]].fail(f"Event not found: {event_id}")

        return FlextResult[dict[str, Any]].ok(self._delivery_confirmations[event_id])

    def get_queue_stats(self) -> dict[str, Any]:
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
                if conf["status"] in {"delivered", "delivered_after_retry"}
            ),
            "failed_deliveries": sum(
                1
                for conf in self._delivery_confirmations.values()
                if conf["status"] == "failed"
            ),
        }


__all__ = ["FlextWebhookHandler"]

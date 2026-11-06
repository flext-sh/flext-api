# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_api/_protocols/webhook
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, MutableSequence, Sequence
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_cli import FlextCliProtocols

if TYPE_CHECKING:
    from flext_api import t


class FlextApiProtocolsWebhook:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class WebhookSettings(FlextCliProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def secret(self) -> str | None:
            """Shared secret for signature verification."""
            ...

        @property
        def signature_header(self) -> str:
            """Header name containing the webhook signature."""
            ...

        @property
        def algorithm(self) -> t.Api.WebhookAlgorithm:
            """Supported HMAC signature algorithm."""
            ...

        @property
        def max_retries(self) -> int:
            """Maximum retry attempts per event."""
            ...

        @property
        def retry_delay(self) -> float:
            """Initial retry delay in seconds."""
            ...

        @property
        def retry_backoff(self) -> float:
            """Retry backoff multiplier."""
            ...

        @property
        def queue_limit(self) -> int:
            """Maximum number of events kept in the main queue."""
            ...

        @property
        def retry_queue_limit(self) -> int:
            """Maximum number of events kept in the retry queue."""
            ...

    @runtime_checkable
    class WebhookEvent(FlextCliProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def id(self) -> str:
            """Unique event identifier."""
            ...

        @property
        def type(self) -> str:
            """Canonical event type."""
            ...

        @property
        def data(self) -> t.JsonMapping:
            """Normalized event payload."""
            ...

        @property
        def timestamp(self) -> float:
            """Event creation timestamp."""
            ...

        @property
        def attempts(self) -> int:
            """Number of processing attempts."""
            ...

    @runtime_checkable
    class WebhookDelivery(FlextCliProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def event_type(self) -> str:
            """Associated event type."""
            ...

        @property
        def timestamp(self) -> float:
            """Delivery status timestamp."""
            ...

        @property
        def status(self) -> t.Api.WebhookDeliveryStatus:
            """Delivery terminal status."""
            ...

        @property
        def attempts(self) -> int | None:
            """Attempts performed before reaching this status."""
            ...

        @property
        def error(self) -> str | None:
            """Terminal failure message when delivery failed."""
            ...

    @runtime_checkable
    class WebhookState(FlextCliProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        handlers: MutableMapping[str, MutableSequence[t.Api.WebhookHandler]]

        @property
        def event_queue(self) -> Sequence[FlextApiProtocolsWebhook.WebhookEvent]:
            """Main event queue."""
            ...

        @property
        def retry_queue(self) -> Sequence[FlextApiProtocolsWebhook.WebhookEvent]:
            """Retry event queue."""
            ...

        @property
        def deliveries(self) -> Mapping[str, FlextApiProtocolsWebhook.WebhookDelivery]:
            """Delivery records by event id."""
            ...

        @property
        def event_queue_size(self) -> int:
            """Current main queue length."""
            ...

        @property
        def retry_queue_size(self) -> int:
            """Current retry queue length."""
            ...

        @property
        def total_deliveries(self) -> int:
            """Number of delivery confirmations."""
            ...

        @property
        def successful_deliveries(self) -> int:
            """Number of successful deliveries."""
            ...

        @property
        def failed_deliveries(self) -> int:
            """Number of failed deliveries."""
            ...


__all__: list[str] = [
    "FlextApiProtocolsWebhook",
]

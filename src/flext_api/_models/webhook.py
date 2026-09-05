"""API webhook models."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Annotated, ClassVar

from flext_api.constants import c
from flext_api.typings import t
from flext_web import m, u

if TYPE_CHECKING:
    from collections.abc import MutableMapping, MutableSequence


class FlextApiModelsWebhook:
    """Webhook model shard for ``m.Api``."""

    class Webhook:
        """Webhook-related models namespace."""

        class Settings(m.Value):
            """Canonical webhook runtime settings."""

            secret: Annotated[
                str | None,
                u.Field(None, description="Shared secret for signature verification"),
            ] = None
            signature_header: Annotated[
                str,
                u.Field(
                    "X-Webhook-Signature",
                    description="Header name containing the webhook signature",
                    min_length=1,
                ),
            ] = "X-Webhook-Signature"
            algorithm: Annotated[
                t.Api.WebhookAlgorithm,
                u.Field("sha256", description="Supported HMAC signature algorithm"),
            ] = c.Api.WebhookAlgorithm.SHA256
            max_retries: Annotated[
                int, u.Field(3, description="Maximum retry attempts per event", ge=0)
            ] = 3
            retry_delay: Annotated[
                float, u.Field(1.0, description="Initial retry delay in seconds", gt=0)
            ] = 1.0
            retry_backoff: Annotated[
                float, u.Field(2.0, description="Retry backoff multiplier", gt=0)
            ] = 2.0
            queue_limit: Annotated[
                int,
                u.Field(
                    1000,
                    description="Maximum number of events kept in the main queue",
                    gt=0,
                ),
            ] = 1000
            retry_queue_limit: Annotated[
                int,
                u.Field(
                    500,
                    description="Maximum number of events kept in the retry queue",
                    gt=0,
                ),
            ] = 500

        class Event(m.Value):
            """Canonical webhook event envelope."""

            id: str = u.Field(description="Unique event identifier", min_length=1)
            type: str = u.Field(description="Canonical event type", min_length=1)
            data: t.JsonMapping = u.Field(description="Normalized event payload")
            timestamp: float = u.Field(
                default_factory=time.time, description="Event creation timestamp"
            )
            attempts: Annotated[
                int, u.Field(0, description="Number of processing attempts", ge=0)
            ] = 0

        class Delivery(m.Value):
            """Canonical delivery status for one webhook event."""

            event_type: str = u.Field(description="Associated event type", min_length=1)
            timestamp: float = u.Field(
                default_factory=time.time, description="Delivery status timestamp"
            )
            status: t.Api.WebhookDeliveryStatus = u.Field(
                description="Delivery terminal status"
            )
            attempts: Annotated[
                int | None,
                u.Field(
                    default=None,
                    description="Attempts performed before reaching this status",
                    ge=0,
                ),
            ] = None
            error: Annotated[
                str | None,
                u.Field(
                    default=None,
                    description="Terminal failure message when delivery failed",
                ),
            ] = None

        class State(m.FlexibleInternalModel):
            """Mutable webhook runtime state centralized in one model."""

            model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
                extra="forbid", validate_assignment=True, arbitrary_types_allowed=True
            )
            handlers: MutableMapping[str, MutableSequence[t.Api.WebhookHandler]] = (
                u.Field(
                    default_factory=dict,
                    description="Registered webhook handlers by event type",
                )
            )
            event_queue: MutableSequence[FlextApiModelsWebhook.Webhook.Event] = u.Field(
                default_factory=list, description="Main event queue"
            )
            retry_queue: MutableSequence[FlextApiModelsWebhook.Webhook.Event] = u.Field(
                default_factory=list, description="Retry event queue"
            )
            deliveries: MutableMapping[str, FlextApiModelsWebhook.Webhook.Delivery] = (
                u.Field(
                    default_factory=dict, description="Delivery records by event id"
                )
            )

            @property
            def event_queue_size(self) -> int:
                """Current main queue length."""
                return len(self.event_queue)

            @property
            def retry_queue_size(self) -> int:
                """Current retry queue length."""
                return len(self.retry_queue)

            @property
            def total_deliveries(self) -> int:
                """Number of delivery confirmations."""
                return len(self.deliveries)

            @property
            def successful_deliveries(self) -> int:
                """Number of successful deliveries."""
                return sum(
                    1
                    for delivery in self.deliveries.values()
                    if delivery.status in {"delivered", "delivered_after_retry"}
                )

            @property
            def failed_deliveries(self) -> int:
                """Number of failed deliveries."""
                return sum(
                    1
                    for delivery in self.deliveries.values()
                    if delivery.status == c.Api.WebhookDeliveryStatus.FAILED.value
                )


__all__: t.MutableSequenceOf[str] = ["FlextApiModelsWebhook"]

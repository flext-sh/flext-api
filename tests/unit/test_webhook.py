"""Public-contract tests for the API webhook handler.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import tm

from flext_api import FlextApiWebhookHandler
from tests import m, p, r, t


class TestsFlextApiWebhook:
    """Validate webhook behavior through public methods only."""

    def test_receive_webhook_processes_registered_handler(self) -> None:
        """Webhook handler processes one event and stores delivered status."""
        received_payloads: t.MutableSequenceOf[t.JsonMapping] = []
        handler = FlextApiWebhookHandler(
            settings=m.Api.Webhook.Settings(max_retries=0),
        )

        def on_created(payload: t.JsonMapping) -> None:
            received_payloads.append(payload)

        register_result = handler.register_event_handler("user.created", on_created)
        receive_result = handler.receive_webhook(
            '{"id":"evt-1","type":"user.created","name":"Ada"}',
            {},
        )
        delivery_result = handler.resolve_delivery_status("evt-1")

        tm.that(register_result.success, eq=True)
        tm.that(receive_result.success, eq=True)
        tm.that(receive_result.value["status"], eq="processed")
        tm.that(len(received_payloads), eq=1)
        tm.that(delivery_result.success, eq=True)
        tm.that(delivery_result.value["status"], eq="delivered")

    def test_receive_webhook_rejects_invalid_signature(self) -> None:
        """Webhook handler rejects invalid signatures when a secret is configured."""
        handler = FlextApiWebhookHandler(
            settings=m.Api.Webhook.Settings(secret="top-secret"),
        )

        result = handler.receive_webhook(
            '{"id":"evt-2","type":"secure.event"}',
            {"X-Webhook-Signature": "invalid"},
        )

        tm.that(result.failure, eq=True)
        tm.that(result.error, has="Signature verification failed")

    def test_failed_event_without_retries_records_failed_delivery(self) -> None:
        """Webhook handler records terminal failure when retries are disabled."""
        handler = FlextApiWebhookHandler(
            settings=m.Api.Webhook.Settings(max_retries=0),
        )

        def on_failed(_payload: t.JsonMapping) -> p.Result[bool]:
            return r[bool].fail("boom")

        handler.register_event_handler("job.failed", on_failed)
        receive_result = handler.receive_webhook(
            '{"id":"evt-3","type":"job.failed"}',
            {},
        )
        delivery_result = handler.resolve_delivery_status("evt-3")

        tm.that(receive_result.failure, eq=True)
        tm.that(delivery_result.success, eq=True)
        tm.that(delivery_result.value["status"], eq="failed")
        tm.that(delivery_result.value["error"], eq="boom")

    def test_process_retry_queue_retries_and_marks_success(self) -> None:
        """Webhook handler retries queued events and stores retry delivery status."""
        attempts = {"count": 0}
        handler = FlextApiWebhookHandler(
            settings=m.Api.Webhook.Settings(
                max_retries=1,
                retry_delay=0.001,
                retry_backoff=1.0,
            ),
        )

        def flaky(_payload: t.JsonMapping) -> p.Result[bool]:
            attempts["count"] += 1
            if attempts["count"] == 1:
                return r[bool].fail("retry once")
            return r[bool].ok(True)

        handler.register_event_handler("job.retry", flaky)
        receive_result = handler.receive_webhook(
            '{"id":"evt-4","type":"job.retry"}',
            {},
        )
        retry_result = handler.process_retry_queue()
        delivery_result = handler.resolve_delivery_status("evt-4")

        tm.that(receive_result.success, eq=True)
        tm.that(receive_result.value["status"], eq="queued_for_retry")
        tm.that(retry_result.success, eq=True)
        tm.that(retry_result.value["processed"], eq=1)
        tm.that(delivery_result.success, eq=True)
        tm.that(delivery_result.value["status"], eq="delivered_after_retry")

"""Behavioral tests for FlextWebTransport observable contract.

Exercises only the public transport surface (``connect`` / ``disconnect`` /
``send`` / ``request_model``) and the ``TransportPlugin`` protocol contract
via the ``r[T]`` outcome, never implementation internals.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_api import m, t
from flext_api._protocols.base import FlextApiProtocolsBase as pb
from flext_api._protocols.transports import FlextApiProtocolsTransports
from flext_tests import tm


class TestsFlextApiTransportsCharacterization:
    """Lock the observable behavior of the HTTP transport public contract."""

    @pytest.fixture
    def transport(self) -> FlextApiProtocolsTransports.FlextWebTransport:
        """Return a fresh, disconnected HTTP transport."""
        return FlextApiProtocolsTransports.FlextWebTransport()

    def test_connect_rejects_empty_url(
        self, transport: FlextApiProtocolsTransports.FlextWebTransport
    ) -> None:
        result = transport.connect("")

        tm.that(result.failure, eq=True)
        tm.that(str(result.error), has="URL is required")

    @pytest.mark.parametrize(
        "url",
        [
            "https://example.test",
            "http://localhost:8080/path",
            "https://api.example.test/v1/resource?q=1",
        ],
    )
    def test_connect_accepts_url_and_echoes_it(
        self, transport: FlextApiProtocolsTransports.FlextWebTransport, url: str
    ) -> None:
        result = transport.connect(url)

        tm.that(result.success, eq=True)
        tm.that(result.value, eq=url)
        tm.that(result.unwrap(), eq=url)

    @pytest.mark.parametrize(
        "options",
        [
            {},
            {"timeout": 5},
            {"follow_redirects": False},
            {"max_redirects": 3},
            {"timeout": 1.5, "follow_redirects": True, "max_redirects": 10},
        ],
    )
    def test_connect_accepts_documented_client_options(
        self,
        transport: FlextApiProtocolsTransports.FlextWebTransport,
        options: dict[str, t.JsonValue],
    ) -> None:
        # connect's public signature accepts optional httpx client options; each
        # supported combination must still yield a successful connection.
        result = transport.connect("https://example.test", **options)

        tm.that(result.success, eq=True)
        tm.that(result.value, eq="https://example.test")

    def test_disconnect_after_connect_succeeds(
        self, transport: FlextApiProtocolsTransports.FlextWebTransport
    ) -> None:
        _ = transport.connect("https://example.test")

        result = transport.disconnect("https://example.test")

        tm.that(result.success, eq=True)
        tm.that(result.value, eq=True)

    def test_disconnect_without_connect_is_idempotent(
        self, transport: FlextApiProtocolsTransports.FlextWebTransport
    ) -> None:
        result = transport.disconnect("https://example.test")

        tm.that(result.success, eq=True)
        tm.that(result.value, eq=True)

    def test_disconnect_twice_stays_successful(
        self, transport: FlextApiProtocolsTransports.FlextWebTransport
    ) -> None:
        _ = transport.connect("https://example.test")

        first = transport.disconnect("https://example.test")
        second = transport.disconnect("https://example.test")

        tm.that(first.success, eq=True)
        tm.that(second.success, eq=True)
        tm.that(second.value, eq=True)

    def test_send_without_connect_reports_disconnected_failure(
        self, transport: FlextApiProtocolsTransports.FlextWebTransport
    ) -> None:
        result = transport.send("https://example.test", {"method": "GET"})

        tm.that(result.failure, eq=True)
        tm.that(str(result.error), has="not connected")

    def test_send_after_disconnect_reports_disconnected_failure(
        self, transport: FlextApiProtocolsTransports.FlextWebTransport
    ) -> None:
        _ = transport.connect("https://example.test")
        _ = transport.disconnect("https://example.test")

        result = transport.send("https://example.test", {"method": "GET"})

        tm.that(result.failure, eq=True)
        tm.that(str(result.error), has="not connected")

    def test_request_model_without_connect_reports_disconnected_failure(
        self, transport: FlextApiProtocolsTransports.FlextWebTransport
    ) -> None:
        request = m.Api.HttpRequest(
            url="https://example.test", method="GET", timeout=30.0
        )

        result = transport.request_model(request)

        tm.that(result.failure, eq=True)
        tm.that(str(result.error), has="not connected")

    def test_transport_satisfies_transport_plugin_protocol(
        self, transport: FlextApiProtocolsTransports.FlextWebTransport
    ) -> None:
        tm.that(transport, is_=pb.TransportPlugin)

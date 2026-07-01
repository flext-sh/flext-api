"""Characterization tests pinning FlextWebTransport observable behavior.

These tests lock the public + composed-helper behavior of the HTTP transport
before the loc-cap MRO decomposition, and must stay green after the split.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api._protocols.base import FlextApiProtocolsBase as pb
from flext_api._protocols.transports import FlextApiProtocolsTransports


class TestsFlextApiTransportsCharacterization:
    """Lock transport behavior across the MRO decomposition."""

    def _transport(self) -> FlextApiProtocolsTransports.FlextWebTransport:
        return FlextApiProtocolsTransports.FlextWebTransport()

    def test_connect_rejects_empty_url(self) -> None:
        result = self._transport().connect("")
        assert result.failure is True

    def test_connect_accepts_url(self) -> None:
        result = self._transport().connect("https://example.test")
        assert result.success is True
        assert result.value == "https://example.test"

    def test_client_timeout_override_and_default(self) -> None:
        transport = self._transport()
        assert abs(transport._client_timeout({"timeout": 5}) - 5.0) < 1e-9
        assert transport._client_timeout({}) > 0

    def test_client_follow_redirects_default_true(self) -> None:
        transport = self._transport()
        assert transport._client_follow_redirects({}) is True
        assert transport._client_follow_redirects({"follow_redirects": False}) is False

    def test_client_max_redirects_default_and_override(self) -> None:
        transport = self._transport()
        assert transport._client_max_redirects({}) == 20
        assert transport._client_max_redirects({"max_redirects": 3}) == 3

    def test_disconnect_after_connect(self) -> None:
        transport = self._transport()
        _ = transport.connect("https://example.test")
        result = transport.disconnect("https://example.test")
        assert result.success is True
        assert result.value is True

    def test_response_mapping_shape(self) -> None:
        transport = self._transport()
        connect_result = transport.connect("https://example.test")
        assert connect_result.success is True

    def test_satisfies_transport_plugin_protocol(self) -> None:
        assert isinstance(self._transport(), pb.TransportPlugin)

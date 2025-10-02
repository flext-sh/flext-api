"""Simple unit tests for HTTP protocol plugin.

Focused tests for HTTP protocol implementation validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.protocol_impls.http import HttpProtocolPlugin


class TestHttpProtocolPluginSimple:
    """Simple test suite for HttpProtocolPlugin."""

    def test_plugin_initialization(self) -> None:
        """Test HTTP plugin initialization."""
        plugin = HttpProtocolPlugin(
            http2=True,
            max_connections=100,
            max_retries=3,
        )

        assert plugin is not None
        assert plugin.name == "http"
        assert plugin._max_retries == 3

    def test_plugin_supports_protocol(self) -> None:
        """Test protocol support checking."""
        plugin = HttpProtocolPlugin()

        assert plugin.supports_protocol("http") is True
        assert plugin.supports_protocol("https") is True
        assert plugin.supports_protocol("websocket") is False

    def test_plugin_get_supported_protocols(self) -> None:
        """Test getting list of supported protocols."""
        plugin = HttpProtocolPlugin()

        protocols = plugin.get_supported_protocols()

        assert "http" in protocols
        assert "https" in protocols

    def test_plugin_initialization_lifecycle(self) -> None:
        """Test plugin initialization and shutdown lifecycle."""
        plugin = HttpProtocolPlugin()

        # Test initialization
        init_result = plugin.initialize()
        assert init_result.is_success
        assert plugin.is_initialized

        # Test double initialization fails
        init_result_2 = plugin.initialize()
        assert init_result_2.is_failure

        # Test shutdown
        shutdown_result = plugin.shutdown()
        assert shutdown_result.is_success
        assert not plugin.is_initialized

        # Test double shutdown fails
        shutdown_result_2 = plugin.shutdown()
        assert shutdown_result_2.is_failure

    def test_plugin_metadata(self) -> None:
        """Test plugin metadata retrieval."""
        plugin = HttpProtocolPlugin()

        metadata = plugin.get_metadata()

        assert metadata["name"] == "http"
        assert "version" in metadata
        assert "description" in metadata
        assert "initialized" in metadata

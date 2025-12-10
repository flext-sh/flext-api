"""Comprehensive tests for FlextApiRegistry.

Tests validate registry functionality using real objects.
No mocks - uses actual registry operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_api.registry import FlextApiRegistry


class TestFlextApiRegistry:
    """Test API registry functionality."""

    def test_registry_initialization(self) -> None:
        """Test registry can be initialized."""
        registry = FlextApiRegistry()
        assert registry is not None

    def test_get_global_singleton(self) -> None:
        """Test global registry is singleton."""
        registry1 = FlextApiRegistry.get_global()
        registry2 = FlextApiRegistry.get_global()
        assert registry1 is registry2

    def test_register_protocol_success(self) -> None:
        """Test protocol registration."""
        registry = FlextApiRegistry()

        # Mock protocol plugin
        class MockProtocol:
            def get_name(self) -> str:
                return "mock_protocol"

        result = registry.register_protocol("http", MockProtocol())
        assert result.is_success

    def test_get_protocol_success(self) -> None:
        """Test protocol retrieval."""
        registry = FlextApiRegistry()

        class MockProtocol:
            def get_name(self) -> str:
                return "mock_protocol"

        # Register first
        registry.register_protocol("http", MockProtocol())

        # Get it back
        result = registry.get_protocol("http")
        assert result.is_success
        protocol = result.value
        assert protocol.get_name() == "mock_protocol"

    def test_register_schema_success(self) -> None:
        """Test schema registration."""
        registry = FlextApiRegistry()

        class MockSchema:
            def get_name(self) -> str:
                return "mock_schema"

        result = registry.register_schema("json", MockSchema())
        assert result.is_success

    def test_get_schema_success(self) -> None:
        """Test schema retrieval."""
        registry = FlextApiRegistry()

        class MockSchema:
            def get_name(self) -> str:
                return "mock_schema"

        registry.register_schema("json", MockSchema())
        result = registry.get_schema("json")
        assert result.is_success
        schema = result.value
        assert schema.get_name() == "mock_schema"

    def test_register_transport_success(self) -> None:
        """Test transport registration."""
        registry = FlextApiRegistry()

        class MockTransport:
            def get_name(self) -> str:
                return "mock_transport"

        result = registry.register_transport("httpx", MockTransport())
        assert result.is_success

    def test_get_transport_success(self) -> None:
        """Test transport retrieval."""
        registry = FlextApiRegistry()

        class MockTransport:
            def get_name(self) -> str:
                return "mock_transport"

        registry.register_transport("httpx", MockTransport())
        result = registry.get_transport("httpx")
        assert result.is_success
        transport = result.value
        assert transport.get_name() == "mock_transport"

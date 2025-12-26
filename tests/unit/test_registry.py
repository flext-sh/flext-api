"""Comprehensive tests for FlextApiRegistry.

Tests validate registry functionality using real objects.
No mocks - uses actual registry operations with real plugin implementations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import r

from flext_api.plugins import FlextApiPlugins
from flext_api.registry import FlextApiRegistry


# Real plugin implementations (not mocks!)
class TestProtocol(FlextApiPlugins.Protocol):
    """Test protocol implementation."""

    def __init__(self) -> None:
        """Initialize test protocol."""
        super().__init__(name="test_protocol", version="1.0.0")

    def send_request(
        self, request: dict[str, object], **kwargs: object
    ) -> r[dict[str, object]]:
        """Send a test request."""
        return r[dict[str, object]].ok({"status": "ok"})

    def supports_protocol(self, protocol: str) -> bool:
        """Check if protocol is supported."""
        return protocol in ("http", "https")


class TestSchema(FlextApiPlugins.Schema):
    """Test schema implementation."""

    def __init__(self) -> None:
        """Initialize test schema."""
        super().__init__(name="test_schema", version="1.0.0")

    def validate_request(
        self, request: dict[str, object], schema: dict[str, object]
    ) -> r[bool]:
        """Validate request against schema."""
        return r[bool].ok(True)

    def validate_response(
        self, response: dict[str, object], schema: dict[str, object]
    ) -> r[bool]:
        """Validate response against schema."""
        return r[bool].ok(True)

    def load_schema(self, schema_source: str) -> r[object]:
        """Load schema from source."""
        return r[object].ok({})


class TestTransport(FlextApiPlugins.Transport):
    """Test transport implementation."""

    def __init__(self) -> None:
        """Initialize test transport."""
        super().__init__(name="test_transport", version="1.0.0")

    def connect(self, url: str, **options: object) -> r[bool]:
        """Establish connection."""
        return r[bool].ok(True)

    def disconnect(self, connection: object) -> r[bool]:
        """Close connection."""
        return r[bool].ok(True)

    def send(
        self,
        connection: object,
        data: dict[str, object] | str | bytes,
        **options: object,
    ) -> r[bool]:
        """Send data through connection."""
        return r[bool].ok(True)

    def receive(
        self, connection: object, **options: object
    ) -> r[dict[str, object] | str | bytes]:
        """Receive data from connection."""
        return r[dict[str, object] | str | bytes].ok(b"response")


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
        result = registry.register_protocol("http", TestProtocol())
        assert result.is_success

    def test_get_protocol_success(self) -> None:
        """Test protocol retrieval."""
        registry = FlextApiRegistry()

        # Register first
        registry.register_protocol("http", TestProtocol())

        # Get it back
        result = registry.get_protocol("http")
        assert result.is_success
        protocol = result.value
        assert protocol.name == "test_protocol"

    def test_register_schema_success(self) -> None:
        """Test schema registration."""
        registry = FlextApiRegistry()
        result = registry.register_schema("json", TestSchema())
        assert result.is_success

    def test_get_schema_success(self) -> None:
        """Test schema retrieval."""
        registry = FlextApiRegistry()

        registry.register_schema("json", TestSchema())
        result = registry.get_schema("json")
        assert result.is_success
        schema = result.value
        assert schema.name == "test_schema"

    def test_register_transport_success(self) -> None:
        """Test transport registration."""
        registry = FlextApiRegistry()
        result = registry.register_transport("httpx", TestTransport())
        assert result.is_success

    def test_get_transport_success(self) -> None:
        """Test transport retrieval."""
        registry = FlextApiRegistry()

        registry.register_transport("httpx", TestTransport())
        result = registry.get_transport("httpx")
        assert result.is_success
        transport = result.value
        assert transport.name == "test_transport"

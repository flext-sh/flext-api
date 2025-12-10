"""Comprehensive tests for FlextApiSerializers.

Tests validate serialization functionality using real data.
No mocks - uses actual serialization operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_api.serializers import FlextApiSerializers


class TestFlextApiSerializers:
    """Test serialization functionality."""

    def test_execute_service_interface(self) -> None:
        """Test FlextService execute method."""
        serializers = FlextApiSerializers()
        result = serializers.execute()
        assert result.is_success
        assert result.value is True

    def test_json_serialize_success(self) -> None:
        """Test JSON serialization."""
        data = {"key": "value", "number": 42, "list": [1, 2, 3]}

        serializer = FlextApiSerializers.JSONSerializer()
        result = serializer.serialize(data)
        assert isinstance(result, bytes)

    def test_json_deserialize_success(self) -> None:
        """Test JSON deserialization."""
        data = {"key": "value", "number": 42}
        serializer = FlextApiSerializers.JSONSerializer()
        serialized = serializer.serialize(data)

        deserialized = serializer.deserialize(serialized)
        assert deserialized == data

    def test_msgpack_serialize_success(self) -> None:
        """Test MessagePack serialization."""
        data = {"key": "value", "number": 42}

        serializer = FlextApiSerializers.MessagePackSerializer()
        serialized = serializer.serialize(data)
        assert isinstance(serialized, bytes)

    def test_msgpack_deserialize_success(self) -> None:
        """Test MessagePack deserialization."""
        data = {"key": "value", "number": 42}
        serializer = FlextApiSerializers.MessagePackSerializer()
        serialized = serializer.serialize(data)

        deserialized = serializer.deserialize(serialized)
        assert deserialized == data

    def test_cbor_serialize_success(self) -> None:
        """Test CBOR serialization."""
        data = {"key": "value", "number": 42}

        serializer = FlextApiSerializers.CBORSerializer()
        serialized = serializer.serialize(data)
        assert isinstance(serialized, bytes)

    def test_cbor_deserialize_success(self) -> None:
        """Test CBOR deserialization."""
        data = {"key": "value", "number": 42}
        serializer = FlextApiSerializers.CBORSerializer()
        serialized = serializer.serialize(data)

        deserialized = serializer.deserialize(serialized)
        assert deserialized == data

    def test_serializer_registry_get_json(self) -> None:
        """Test serializer registry for JSON."""
        registry = FlextApiSerializers.SerializerRegistry()
        result = registry.get_serializer("application/json")
        assert result.is_success
        serializer = result.value
        assert hasattr(serializer, "serialize")

    def test_serializer_registry_get_msgpack(self) -> None:
        """Test serializer registry for MessagePack."""
        registry = FlextApiSerializers.SerializerRegistry()
        result = registry.get_serializer("application/x-msgpack")
        assert result.is_success
        serializer = result.value
        assert hasattr(serializer, "serialize")

    def test_serializer_registry_get_cbor(self) -> None:
        """Test serializer registry for CBOR."""
        registry = FlextApiSerializers.SerializerRegistry()
        result = registry.get_serializer("application/cbor")
        assert result.is_success
        serializer = result.value
        assert hasattr(serializer, "serialize")

    def test_serializer_registry_get_unknown(self) -> None:
        """Test serializer registry for unknown type."""
        registry = FlextApiSerializers.SerializerRegistry()
        result = registry.get_serializer("unknown/type")
        assert result.is_failure

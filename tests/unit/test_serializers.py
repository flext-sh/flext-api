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
        assert result.unwrap() is True

    def test_json_serialize_success(self) -> None:
        """Test JSON serialization."""
        data = {"key": "value", "number": 42, "list": [1, 2, 3]}

        result = FlextApiSerializers.JSONSerializer.serialize(data)
        assert result.is_success
        serialized = result.unwrap()
        assert isinstance(serialized, bytes)

    def test_json_deserialize_success(self) -> None:
        """Test JSON deserialization."""
        data = {"key": "value", "number": 42}
        result = FlextApiSerializers.JSONSerializer.serialize(data)
        serialized = result.unwrap()

        result = FlextApiSerializers.JSONSerializer.deserialize(serialized)
        assert result.is_success
        deserialized = result.unwrap()
        assert deserialized == data

    def test_msgpack_serialize_success(self) -> None:
        """Test MessagePack serialization."""
        data = {"key": "value", "number": 42}

        result = FlextApiSerializers.MessagePackSerializer.serialize(data)
        assert result.is_success
        serialized = result.unwrap()
        assert isinstance(serialized, bytes)

    def test_msgpack_deserialize_success(self) -> None:
        """Test MessagePack deserialization."""
        data = {"key": "value", "number": 42}
        result = FlextApiSerializers.MessagePackSerializer.serialize(data)
        serialized = result.unwrap()

        result = FlextApiSerializers.MessagePackSerializer.deserialize(serialized)
        assert result.is_success
        deserialized = result.unwrap()
        assert deserialized == data

    def test_cbor_serialize_success(self) -> None:
        """Test CBOR serialization."""
        data = {"key": "value", "number": 42}

        result = FlextApiSerializers.CBORSerializer.serialize(data)
        assert result.is_success
        serialized = result.unwrap()
        assert isinstance(serialized, bytes)

    def test_cbor_deserialize_success(self) -> None:
        """Test CBOR deserialization."""
        data = {"key": "value", "number": 42}
        result = FlextApiSerializers.CBORSerializer.serialize(data)
        serialized = result.unwrap()

        result = FlextApiSerializers.CBORSerializer.deserialize(serialized)
        assert result.is_success
        deserialized = result.unwrap()
        assert deserialized == data

    def test_serializer_registry_get_json(self) -> None:
        """Test serializer registry for JSON."""
        result = FlextApiSerializers.SerializerRegistry.get_serializer(
            "application/json"
        )
        assert result.is_success
        serializer = result.unwrap()
        assert hasattr(serializer, "serialize")

    def test_serializer_registry_get_msgpack(self) -> None:
        """Test serializer registry for MessagePack."""
        result = FlextApiSerializers.SerializerRegistry.get_serializer(
            "application/x-msgpack"
        )
        assert result.is_success
        serializer = result.unwrap()
        assert hasattr(serializer, "serialize")

    def test_serializer_registry_get_cbor(self) -> None:
        """Test serializer registry for CBOR."""
        result = FlextApiSerializers.SerializerRegistry.get_serializer(
            "application/cbor"
        )
        assert result.is_success
        serializer = result.unwrap()
        assert hasattr(serializer, "serialize")

    def test_serializer_registry_get_unknown(self) -> None:
        """Test serializer registry for unknown type."""
        result = FlextApiSerializers.SerializerRegistry.get_serializer("unknown/type")
        assert result.is_failure

"""Simple unit tests for serializers functionality.

Tests for JSONSerializer, MessagePackSerializer, CBORSerializer, and SerializerRegistry.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_api.serializers import (
    CBORSerializer,
    JSONSerializer,
    MessagePackSerializer,
    SerializationFormat,
    SerializerRegistry,
)


class TestJSONSerializer:
    """Test suite for JSONSerializer."""

    def test_json_serializer_serialize(self) -> None:
        """Test JSON serialization."""
        serializer = JSONSerializer()
        data = {"key": "value", "number": 42}

        result = serializer.serialize(data)

        assert result is not None
        assert isinstance(result, bytes)
        assert b"key" in result
        assert b"value" in result

    def test_json_serializer_deserialize(self) -> None:
        """Test JSON deserialization."""
        serializer = JSONSerializer()
        data = b'{"key": "value", "number": 42}'

        result = serializer.deserialize(data)

        assert result is not None
        assert result["key"] == "value"
        assert result["number"] == 42

    def test_json_serializer_roundtrip(self) -> None:
        """Test JSON serialization roundtrip."""
        serializer = JSONSerializer()
        original_data = {"test": "data", "nested": {"key": "value"}}

        serialized = serializer.serialize(original_data)
        deserialized = serializer.deserialize(serialized)

        assert deserialized == original_data

    def test_json_serializer_pretty_print(self) -> None:
        """Test JSON pretty printing."""
        serializer = JSONSerializer(pretty=True)
        data = {"key": "value"}

        result = serializer.serialize(data)

        assert result is not None
        assert b"\n" in result or b"  " in result  # Has formatting

    def test_json_serializer_content_type(self) -> None:
        """Test JSON serializer content type."""
        serializer = JSONSerializer()

        assert serializer.content_type == "application/json"


class TestMessagePackSerializer:
    """Test suite for MessagePackSerializer."""

    def test_msgpack_serializer_serialize(self) -> None:
        """Test MessagePack serialization."""
        serializer = MessagePackSerializer()

        if not serializer._available:
            pytest.skip("msgpack not installed")

        data = {"key": "value", "number": 42}

        result = serializer.serialize(data)

        assert result is not None
        assert isinstance(result, bytes)

    def test_msgpack_serializer_deserialize(self) -> None:
        """Test MessagePack deserialization."""
        serializer = MessagePackSerializer()

        if not serializer._available:
            pytest.skip("msgpack not installed")

        data = {"key": "value", "number": 42}
        serialized = serializer.serialize(data)

        result = serializer.deserialize(serialized)

        assert result is not None
        assert result["key"] == "value"
        assert result["number"] == 42

    def test_msgpack_serializer_roundtrip(self) -> None:
        """Test MessagePack serialization roundtrip."""
        serializer = MessagePackSerializer()

        if not serializer._available:
            pytest.skip("msgpack not installed")

        original_data = {"test": "data", "list": [1, 2, 3]}

        serialized = serializer.serialize(original_data)
        deserialized = serializer.deserialize(serialized)

        assert deserialized == original_data

    def test_msgpack_serializer_content_type(self) -> None:
        """Test MessagePack serializer content type."""
        serializer = MessagePackSerializer()

        assert serializer.content_type == "application/msgpack"

    def test_msgpack_serializer_not_available(self) -> None:
        """Test MessagePack serializer when not installed."""
        serializer = MessagePackSerializer()

        if serializer._available:
            pytest.skip("msgpack is installed")

        with pytest.raises(ImportError):
            serializer.serialize({"key": "value"})


class TestCBORSerializer:
    """Test suite for CBORSerializer."""

    def test_cbor_serializer_serialize(self) -> None:
        """Test CBOR serialization."""
        serializer = CBORSerializer()

        if not serializer._available:
            pytest.skip("cbor2 not installed")

        data = {"key": "value", "number": 42}

        result = serializer.serialize(data)

        assert result is not None
        assert isinstance(result, bytes)

    def test_cbor_serializer_deserialize(self) -> None:
        """Test CBOR deserialization."""
        serializer = CBORSerializer()

        if not serializer._available:
            pytest.skip("cbor2 not installed")

        data = {"key": "value", "number": 42}
        serialized = serializer.serialize(data)

        result = serializer.deserialize(serialized)

        assert result is not None
        assert result["key"] == "value"
        assert result["number"] == 42

    def test_cbor_serializer_roundtrip(self) -> None:
        """Test CBOR serialization roundtrip."""
        serializer = CBORSerializer()

        if not serializer._available:
            pytest.skip("cbor2 not installed")

        original_data = {"test": "data", "binary": b"bytes"}

        serialized = serializer.serialize(original_data)
        deserialized = serializer.deserialize(serialized)

        assert deserialized["test"] == original_data["test"]

    def test_cbor_serializer_content_type(self) -> None:
        """Test CBOR serializer content type."""
        serializer = CBORSerializer()

        assert serializer.content_type == "application/cbor"

    def test_cbor_serializer_not_available(self) -> None:
        """Test CBOR serializer when not installed."""
        serializer = CBORSerializer()

        if serializer._available:
            pytest.skip("cbor2 is installed")

        with pytest.raises(ImportError):
            serializer.serialize({"key": "value"})


class TestSerializerRegistry:
    """Test suite for SerializerRegistry."""

    def test_registry_initialization(self) -> None:
        """Test registry initialization with default serializers."""
        registry = SerializerRegistry()

        # Should have default serializers registered
        json_result = registry.get_serializer(SerializationFormat.JSON)
        assert json_result.is_success

        msgpack_result = registry.get_serializer(SerializationFormat.MSGPACK)
        assert msgpack_result.is_success

        cbor_result = registry.get_serializer(SerializationFormat.CBOR)
        assert cbor_result.is_success

    def test_registry_get_serializer_by_content_type(self) -> None:
        """Test getting serializer by content type."""
        registry = SerializerRegistry()

        json_result = registry.get_serializer_by_content_type("application/json")
        assert json_result.is_success

        msgpack_result = registry.get_serializer_by_content_type("application/msgpack")
        assert msgpack_result.is_success

    def test_registry_serialize_json(self) -> None:
        """Test serialization using registry with JSON format."""
        registry = SerializerRegistry()
        data = {"key": "value"}

        result = registry.serialize(data, SerializationFormat.JSON)

        assert result.is_success
        serialized = result.unwrap()
        assert isinstance(serialized, bytes)
        assert b"key" in serialized

    def test_registry_deserialize_json(self) -> None:
        """Test deserialization using registry with JSON format."""
        registry = SerializerRegistry()
        data = b'{"key": "value"}'

        result = registry.deserialize(data, SerializationFormat.JSON)

        assert result.is_success
        deserialized = result.unwrap()
        assert deserialized["key"] == "value"

    def test_registry_serialize_default_format(self) -> None:
        """Test serialization using default format."""
        registry = SerializerRegistry()
        data = {"key": "value"}

        result = registry.serialize(data)  # Uses default JSON

        assert result.is_success
        serialized = result.unwrap()
        assert isinstance(serialized, bytes)

    def test_registry_set_default_format(self) -> None:
        """Test setting default serialization format."""
        registry = SerializerRegistry()

        result = registry.set_default_format(SerializationFormat.JSON)

        assert result.is_success

    def test_registry_unknown_format(self) -> None:
        """Test getting serializer for unknown format."""
        registry = SerializerRegistry()

        result = registry.get_serializer("unknown_format")

        assert result.is_failure
        assert "No serializer registered" in result.error

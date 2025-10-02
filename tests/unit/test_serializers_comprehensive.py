"""Comprehensive tests for flext-api serializers with real functionality.

Tests all serializer classes with real data transformations:
- JSONSerializer
- MessagePackSerializer (if available)
- CBORSerializer (if available)
- SerializerRegistry

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import math

import pytest

from flext_api.serializers import (
    CBORSerializer,
    JSONSerializer,
    MessagePackSerializer,
    SerializationFormat,
    SerializerRegistry,
)


class TestJSONSerializer:
    """Comprehensive tests for JSON serializer."""

    def test_serializer_initialization(self) -> None:
        """Test JSON serializer initialization."""
        serializer = JSONSerializer()

        assert serializer is not None
        assert serializer._logger is not None
        assert serializer._pretty is False

    def test_serializer_initialization_pretty_mode(self) -> None:
        """Test JSON serializer with pretty printing."""
        serializer = JSONSerializer(pretty=True)

        assert serializer._pretty is True

    def test_serialize_simple_dict(self) -> None:
        """Test serializing simple dictionary."""
        serializer = JSONSerializer()

        data = {"name": "John", "age": 30, "active": True}
        result = serializer.serialize(data)

        assert isinstance(result, bytes)
        assert b'"name"' in result
        assert b'"John"' in result
        assert b'"age"' in result
        assert b"30" in result

    def test_serialize_nested_structure(self) -> None:
        """Test serializing nested data structure."""
        serializer = JSONSerializer()

        data = {
            "user": {
                "id": 123,
                "name": "John Doe",
                "roles": ["admin", "user"],
                "metadata": {"created": "2025-01-01", "active": True},
            }
        }

        result = serializer.serialize(data)

        assert isinstance(result, bytes)
        assert b'"user"' in result
        assert b'"admin"' in result
        assert b'"2025-01-01"' in result

    def test_serialize_list(self) -> None:
        """Test serializing list."""
        serializer = JSONSerializer()

        data = [1, 2, 3, "test", True, None, {"key": "value"}]
        result = serializer.serialize(data)

        assert isinstance(result, bytes)
        assert b"[" in result
        assert b"]" in result
        assert b'"test"' in result
        assert b"null" in result

    def test_deserialize_simple_dict(self) -> None:
        """Test deserializing simple dictionary."""
        serializer = JSONSerializer()

        json_bytes = b'{"name": "John", "age": 30, "active": true}'
        result = serializer.deserialize(json_bytes)

        assert isinstance(result, dict)
        assert result["name"] == "John"
        assert result["age"] == 30
        assert result["active"] is True

    def test_deserialize_nested_structure(self) -> None:
        """Test deserializing nested structure."""
        serializer = JSONSerializer()

        json_bytes = (
            b'{"user": {"id": 123, "name": "John", "roles": ["admin", "user"]}}'
        )
        result = serializer.deserialize(json_bytes)

        assert isinstance(result, dict)
        assert result["user"]["id"] == 123
        assert result["user"]["name"] == "John"
        assert "admin" in result["user"]["roles"]

    def test_serialize_deserialize_roundtrip(self) -> None:
        """Test serialize/deserialize roundtrip."""
        serializer = JSONSerializer()

        original_data = {
            "string": "test",
            "integer": 42,
            "float": math.pi,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3],
            "nested": {"key": "value"},
        }

        serialized = serializer.serialize(original_data)
        deserialized = serializer.deserialize(serialized)

        assert deserialized == original_data

    def test_content_type(self) -> None:
        """Test content type property."""
        serializer = JSONSerializer()

        assert serializer.content_type == "application/json"

    def test_pretty_printing(self) -> None:
        """Test pretty printing mode."""
        serializer = JSONSerializer(pretty=True)

        data = {"key1": "value1", "key2": "value2"}
        result = serializer.serialize(data)

        # Pretty printed JSON should have newlines
        assert b"\n" in result or b"  " in result  # Either newlines or indentation


class TestMessagePackSerializer:
    """Comprehensive tests for MessagePack serializer."""

    def test_serializer_initialization(self) -> None:
        """Test MessagePack serializer initialization."""
        serializer = MessagePackSerializer()

        assert serializer is not None
        assert serializer._logger is not None

    def test_content_type(self) -> None:
        """Test content type property."""
        serializer = MessagePackSerializer()

        assert serializer.content_type == "application/msgpack"

    def test_serialize_when_msgpack_available(self) -> None:
        """Test serialization when msgpack is available."""
        serializer = MessagePackSerializer()

        if not serializer._available:
            pytest.skip("msgpack not installed")

        data = {"name": "John", "age": 30, "tags": ["python", "api"]}
        result = serializer.serialize(data)

        # MessagePack produces binary data
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_deserialize_when_msgpack_available(self) -> None:
        """Test deserialization when msgpack is available."""
        serializer = MessagePackSerializer()

        if not serializer._available:
            pytest.skip("msgpack not installed")

        data = {"name": "John", "age": 30}
        serialized = serializer.serialize(data)
        deserialized = serializer.deserialize(serialized)

        assert deserialized == data

    def test_serialize_raises_when_msgpack_not_available(self) -> None:
        """Test that serialize raises ImportError when msgpack not available."""
        serializer = MessagePackSerializer()

        if serializer._available:
            pytest.skip("msgpack is installed")

        data = {"test": "data"}

        with pytest.raises(ImportError) as exc_info:
            serializer.serialize(data)

        assert "msgpack not installed" in str(exc_info.value)

    def test_deserialize_raises_when_msgpack_not_available(self) -> None:
        """Test that deserialize raises ImportError when msgpack not available."""
        serializer = MessagePackSerializer()

        if serializer._available:
            pytest.skip("msgpack is installed")

        with pytest.raises(ImportError) as exc_info:
            serializer.deserialize(b"dummy_data")

        assert "msgpack not installed" in str(exc_info.value)


class TestCBORSerializer:
    """Comprehensive tests for CBOR serializer."""

    def test_serializer_initialization(self) -> None:
        """Test CBOR serializer initialization."""
        serializer = CBORSerializer()

        assert serializer is not None
        assert serializer._logger is not None

    def test_content_type(self) -> None:
        """Test content type property."""
        serializer = CBORSerializer()

        assert serializer.content_type == "application/cbor"

    def test_serialize_when_cbor_available(self) -> None:
        """Test serialization when cbor2 is available."""
        serializer = CBORSerializer()

        if not serializer._available:
            pytest.skip("cbor2 not installed")

        data = {"name": "John", "age": 30, "tags": ["python", "api"]}
        result = serializer.serialize(data)

        # CBOR produces binary data
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_deserialize_when_cbor_available(self) -> None:
        """Test deserialization when cbor2 is available."""
        serializer = CBORSerializer()

        if not serializer._available:
            pytest.skip("cbor2 not installed")

        data = {"name": "John", "age": 30}
        serialized = serializer.serialize(data)
        deserialized = serializer.deserialize(serialized)

        assert deserialized == data

    def test_serialize_raises_when_cbor_not_available(self) -> None:
        """Test that serialize raises ImportError when cbor2 not available."""
        serializer = CBORSerializer()

        if serializer._available:
            pytest.skip("cbor2 is installed")

        data = {"test": "data"}

        with pytest.raises(ImportError) as exc_info:
            serializer.serialize(data)

        assert "cbor2 not installed" in str(exc_info.value)

    def test_deserialize_raises_when_cbor_not_available(self) -> None:
        """Test that deserialize raises ImportError when cbor2 not available."""
        serializer = CBORSerializer()

        if serializer._available:
            pytest.skip("cbor2 is installed")

        with pytest.raises(ImportError) as exc_info:
            serializer.deserialize(b"dummy_data")

        assert "cbor2 not installed" in str(exc_info.value)


class TestSerializerRegistry:
    """Comprehensive tests for serializer registry."""

    def test_registry_initialization(self) -> None:
        """Test serializer registry initialization."""
        registry = SerializerRegistry()

        assert registry is not None
        assert registry._logger is not None
        assert len(registry._serializers) >= 1  # At least JSON registered

    def test_default_serializers_registered(self) -> None:
        """Test that default serializers are registered."""
        registry = SerializerRegistry()

        # JSON should always be registered
        json_result = registry.get_serializer(SerializationFormat.JSON)
        assert json_result.is_success

    def test_register_custom_serializer(self) -> None:
        """Test registering custom serializer."""
        registry = SerializerRegistry()
        custom_serializer = JSONSerializer()  # Use JSON as example

        result = registry.register_serializer("custom", custom_serializer)

        assert result.is_success

        # Verify retrieval
        get_result = registry.get_serializer("custom")
        assert get_result.is_success

    def test_register_serializer_overwrites_existing(self) -> None:
        """Test that registering existing format works (with warning)."""
        registry = SerializerRegistry()

        # Register JSON again
        new_serializer = JSONSerializer(pretty=True)
        result = registry.register_serializer(SerializationFormat.JSON, new_serializer)

        assert result.is_success

    def test_get_serializer_by_format(self) -> None:
        """Test getting serializer by format."""
        registry = SerializerRegistry()

        # Get JSON serializer
        result = registry.get_serializer(SerializationFormat.JSON)

        assert result.is_success
        serializer = result.unwrap()
        assert isinstance(serializer, JSONSerializer)

    def test_get_serializer_by_string_format(self) -> None:
        """Test getting serializer by string format."""
        registry = SerializerRegistry()

        result = registry.get_serializer("json")

        assert result.is_success
        serializer = result.unwrap()
        assert isinstance(serializer, JSONSerializer)

    def test_get_serializer_unknown_format(self) -> None:
        """Test getting serializer for unknown format."""
        registry = SerializerRegistry()

        result = registry.get_serializer("unknown_format")

        assert result.is_failure
        assert "No serializer registered" in result.error

    def test_get_serializer_by_content_type(self) -> None:
        """Test getting serializer by content type."""
        registry = SerializerRegistry()

        result = registry.get_serializer_by_content_type("application/json")

        assert result.is_success
        serializer = result.unwrap()
        assert serializer.content_type == "application/json"

    def test_get_serializer_by_content_type_with_charset(self) -> None:
        """Test getting serializer by content type with charset."""
        registry = SerializerRegistry()

        # Content type with charset should be normalized
        result = registry.get_serializer_by_content_type(
            "application/json; charset=utf-8"
        )

        assert result.is_success
        serializer = result.unwrap()
        assert serializer.content_type == "application/json"

    def test_get_serializer_by_unknown_content_type(self) -> None:
        """Test getting serializer for unknown content type."""
        registry = SerializerRegistry()

        result = registry.get_serializer_by_content_type("application/unknown")

        assert result.is_failure
        assert "No serializer found" in result.error

    def test_serialize_with_default_format(self) -> None:
        """Test serializing with default format."""
        registry = SerializerRegistry()

        data = {"name": "John", "age": 30}
        result = registry.serialize(data)

        assert result.is_success
        serialized = result.unwrap()
        assert isinstance(serialized, bytes)

    def test_serialize_with_specific_format(self) -> None:
        """Test serializing with specific format."""
        registry = SerializerRegistry()

        data = {"name": "John", "age": 30}
        result = registry.serialize(data, format=SerializationFormat.JSON)

        assert result.is_success
        serialized = result.unwrap()
        assert isinstance(serialized, bytes)

    def test_serialize_with_string_format(self) -> None:
        """Test serializing with string format."""
        registry = SerializerRegistry()

        data = {"name": "John", "age": 30}
        result = registry.serialize(data, format="json")

        assert result.is_success

    def test_serialize_with_unknown_format(self) -> None:
        """Test serializing with unknown format."""
        registry = SerializerRegistry()

        data = {"test": "data"}
        result = registry.serialize(data, format="unknown")

        assert result.is_failure
        assert "No serializer registered" in result.error

    def test_deserialize_with_default_format(self) -> None:
        """Test deserializing with default format."""
        registry = SerializerRegistry()

        data = {"name": "John", "age": 30}
        serialized = registry.serialize(data).unwrap()
        result = registry.deserialize(serialized)

        assert result.is_success
        deserialized = result.unwrap()
        assert deserialized == data

    def test_deserialize_with_specific_format(self) -> None:
        """Test deserializing with specific format."""
        registry = SerializerRegistry()

        data = {"name": "John", "age": 30}
        serialized = registry.serialize(data, format=SerializationFormat.JSON).unwrap()
        result = registry.deserialize(serialized, format=SerializationFormat.JSON)

        assert result.is_success
        deserialized = result.unwrap()
        assert deserialized == data

    def test_deserialize_with_unknown_format(self) -> None:
        """Test deserializing with unknown format."""
        registry = SerializerRegistry()

        result = registry.deserialize(b"dummy_data", format="unknown")

        assert result.is_failure
        assert "No serializer registered" in result.error

    def test_set_default_format(self) -> None:
        """Test setting default serialization format."""
        registry = SerializerRegistry()

        result = registry.set_default_format(SerializationFormat.JSON)

        assert result.is_success
        assert registry._default_format == SerializationFormat.JSON

    def test_serialize_deserialize_roundtrip(self) -> None:
        """Test full serialize/deserialize roundtrip through registry."""
        registry = SerializerRegistry()

        original_data = {
            "user": {
                "id": 123,
                "name": "John Doe",
                "roles": ["admin", "user"],
                "metadata": {"created": "2025-01-01", "active": True},
            }
        }

        # Serialize
        serialize_result = registry.serialize(
            original_data, format=SerializationFormat.JSON
        )
        assert serialize_result.is_success
        serialized = serialize_result.unwrap()

        # Deserialize
        deserialize_result = registry.deserialize(
            serialized, format=SerializationFormat.JSON
        )
        assert deserialize_result.is_success
        deserialized = deserialize_result.unwrap()

        assert deserialized == original_data


class TestSerializationFormats:
    """Tests for SerializationFormat enum."""

    def test_format_enum_values(self) -> None:
        """Test serialization format enum values."""
        assert SerializationFormat.JSON.value == "json"
        assert SerializationFormat.MSGPACK.value == "msgpack"
        assert SerializationFormat.CBOR.value == "cbor"
        assert SerializationFormat.CUSTOM.value == "custom"

    def test_format_enum_string_comparison(self) -> None:
        """Test comparing format enum with strings."""
        assert SerializationFormat.JSON == "json"
        assert SerializationFormat.MSGPACK == "msgpack"
        assert SerializationFormat.CBOR == "cbor"

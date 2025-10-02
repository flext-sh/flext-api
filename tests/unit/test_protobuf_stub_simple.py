"""Simple unit tests for Protobuf stub functionality.

Tests for Protocol Buffers placeholder classes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.protocol_stubs.protobuf_stub import (
    ProtobufField,
    ProtobufMessage,
    ProtobufSchema,
    ProtobufSerializer,
)


class TestProtobufMessage:
    """Test suite for ProtobufMessage stub."""

    def test_message_initialization(self) -> None:
        """Test message initialization."""
        message = ProtobufMessage(data={"name": "John", "age": 30})

        assert message is not None
        assert message._data == {"name": "John", "age": 30}

    def test_message_empty_initialization(self) -> None:
        """Test empty message initialization."""
        message = ProtobufMessage()

        assert message is not None
        assert message._data == {}

    def test_message_serialize_placeholder(self) -> None:
        """Test message serialization (placeholder)."""
        message = ProtobufMessage(data={"name": "John"})
        result = message.serialize()

        assert result.is_failure
        assert result.error is not None and "placeholder" in result.error

    def test_message_deserialize_placeholder(self) -> None:
        """Test message deserialization (placeholder)."""
        result = ProtobufMessage.deserialize(b"data")

        assert result.is_failure
        assert result.error is not None and "placeholder" in result.error

    def test_message_to_dict(self) -> None:
        """Test message to dictionary conversion."""
        data = {"name": "John", "age": 30}
        message = ProtobufMessage(data=data)

        result = message.to_dict()

        assert result == data

    def test_message_from_dict(self) -> None:
        """Test message from dictionary creation."""
        data = {"name": "John", "age": 30}
        message = ProtobufMessage.from_dict(data)

        assert message is not None
        assert message._data == data

    def test_message_to_json(self) -> None:
        """Test message to JSON conversion."""
        message = ProtobufMessage(data={"name": "John", "age": 30})
        result = message.to_json()

        assert result.is_success
        json_str = result.unwrap()
        assert "John" in json_str
        assert "30" in json_str

    def test_message_from_json(self) -> None:
        """Test message from JSON creation."""
        json_str = '{"name": "John", "age": 30}'
        result = ProtobufMessage.from_json(json_str)

        assert result.is_success
        message = result.unwrap()
        assert message._data["name"] == "John"
        assert message._data["age"] == 30

    def test_message_from_json_invalid(self) -> None:
        """Test message from invalid JSON."""
        result = ProtobufMessage.from_json("invalid json")

        assert result.is_failure
        assert result.error is not None and "parsing failed" in result.error


class TestProtobufSerializer:
    """Test suite for ProtobufSerializer stub."""

    def test_serializer_initialization(self) -> None:
        """Test serializer initialization."""
        serializer = ProtobufSerializer()

        assert serializer is not None
        assert serializer._schema == {}

    def test_serializer_with_schema(self) -> None:
        """Test serializer with schema."""
        schema = {"name": "User", "fields": ["name", "age"]}
        serializer = ProtobufSerializer(schema=schema)

        assert serializer._schema == schema

    def test_serializer_content_type(self) -> None:
        """Test serializer content type."""
        serializer = ProtobufSerializer()

        assert serializer.content_type == "application/protobuf"

    def test_serializer_serialize_placeholder(self) -> None:
        """Test serializer serialize (placeholder)."""
        serializer = ProtobufSerializer()
        message = ProtobufMessage(data={"name": "John"})

        result = serializer.serialize(message)

        assert result.is_failure
        assert result.error is not None and "placeholder" in result.error

    def test_serializer_deserialize_placeholder(self) -> None:
        """Test serializer deserialize (placeholder)."""
        serializer = ProtobufSerializer()
        result = serializer.deserialize(b"data")

        assert result.is_failure
        assert result.error is not None and "placeholder" in result.error


class TestProtobufField:
    """Test suite for ProtobufField."""

    def test_field_initialization(self) -> None:
        """Test field initialization."""
        field = ProtobufField(
            name="username",
            field_number=1,
            field_type=str,
        )

        assert field is not None
        assert field.name == "username"
        assert field.field_number == 1

    def test_field_required(self) -> None:
        """Test required field."""
        field = ProtobufField(
            name="id",
            field_number=1,
            field_type=int,
            required=True,
        )

        assert field.is_required

    def test_field_repeated(self) -> None:
        """Test repeated field."""
        field = ProtobufField(
            name="tags",
            field_number=5,
            field_type=list,
            repeated=True,
        )

        assert field.is_repeated

    def test_field_validate_type_success(self) -> None:
        """Test field type validation success."""
        field = ProtobufField(
            name="username",
            field_number=1,
            field_type=str,
        )

        result = field.validate("john")

        assert result.is_success

    def test_field_validate_type_failure(self) -> None:
        """Test field type validation failure."""
        field = ProtobufField(
            name="username",
            field_number=1,
            field_type=str,
        )

        result = field.validate(123)

        assert result.is_failure
        assert result.error is not None and "expects str" in result.error

    def test_field_validate_required_success(self) -> None:
        """Test required field validation success."""
        field = ProtobufField(
            name="id",
            field_number=1,
            field_type=int,
            required=True,
        )

        result = field.validate(123)

        assert result.is_success

    def test_field_validate_required_failure(self) -> None:
        """Test required field validation failure."""
        field = ProtobufField(
            name="id",
            field_number=1,
            field_type=int,
            required=True,
        )

        result = field.validate(None)

        assert result.is_failure
        assert result.error is not None and "Required field" in result.error

    def test_field_validate_repeated_success(self) -> None:
        """Test repeated field validation success."""
        field = ProtobufField(
            name="tags",
            field_number=5,
            field_type=list,
            repeated=True,
        )

        result = field.validate(["tag1", "tag2"])

        assert result.is_success

    def test_field_validate_repeated_failure(self) -> None:
        """Test repeated field validation failure."""
        field = ProtobufField(
            name="tags",
            field_number=5,
            field_type=list,
            repeated=True,
        )

        result = field.validate("not a list")

        assert result.is_failure
        assert result.error is not None and "must be a list" in result.error


class TestProtobufSchema:
    """Test suite for ProtobufSchema."""

    def test_schema_initialization(self) -> None:
        """Test schema initialization."""
        schema = ProtobufSchema(name="User")

        assert schema is not None
        assert schema.name == "User"
        assert len(schema.fields) == 0

    def test_schema_add_field(self) -> None:
        """Test adding field to schema."""
        schema = ProtobufSchema(name="User")
        field = ProtobufField(
            name="username",
            field_number=1,
            field_type=str,
        )

        result = schema.add_field(field)

        assert result.is_success
        assert "username" in schema.fields

    def test_schema_add_duplicate_field(self) -> None:
        """Test adding duplicate field."""
        schema = ProtobufSchema(name="User")
        field = ProtobufField(
            name="username",
            field_number=1,
            field_type=str,
        )

        schema.add_field(field)
        result = schema.add_field(field)

        assert result.is_failure
        assert result.error is not None and "already exists" in result.error

    def test_schema_validate_message_success(self) -> None:
        """Test schema message validation success."""
        schema = ProtobufSchema(name="User")
        schema.add_field(
            ProtobufField(
                name="username",
                field_number=1,
                field_type=str,
            )
        )

        message = ProtobufMessage(data={"username": "john"})
        result = schema.validate_message(message)

        assert result.is_success

    def test_schema_validate_message_failure(self) -> None:
        """Test schema message validation failure."""
        schema = ProtobufSchema(name="User")
        schema.add_field(
            ProtobufField(
                name="id",
                field_number=1,
                field_type=int,
                required=True,
            )
        )

        message = ProtobufMessage(data={})
        result = schema.validate_message(message)

        assert result.is_failure
        assert result.error is not None and "Required field" in result.error

    def test_schema_fields_property(self) -> None:
        """Test schema fields property returns copy."""
        schema = ProtobufSchema(name="User")
        field = ProtobufField(
            name="username",
            field_number=1,
            field_type=str,
        )
        schema.add_field(field)

        fields1 = schema.fields
        fields2 = schema.fields

        # Should return copies, not same reference
        assert fields1 is not fields2
        assert fields1 == fields2

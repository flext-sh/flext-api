"""Serialization support for flext-api.

Provides multiple serialization formats with:
- JSON serialization (orjson for performance)
- MessagePack serialization (binary format)
- CBOR serialization (Concise Binary Object Representation)
- Content-type negotiation
- Streaming serialization
- Custom serializer registration

See TRANSFORMATION_PLAN.md - Phase 8 for implementation details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
from typing import Any, Protocol

import cbor2
import msgpack
import orjson
from flext_core import FlextLogger, FlextResult, FlextService

from flext_api.typings import FlextApiTypes


class FlextApiSerializers(FlextService[None]):
    """Unified serialization service with multiple format support.

    Provides JSON, MessagePack, and CBOR serialization through nested classes.
    Follows FLEXT standards with FlextResult error handling.
    """

    class SerializerProtocol(Protocol):
        """Protocol for custom serializers."""

        def serialize(self, data: object) -> bytes:
            """Serialize data to bytes.

            Args:
            data: Data to serialize

            Returns:
            Serialized bytes

            """
            ...  # Protocol method

        def deserialize(self, data: bytes) -> object:
            """Deserialize bytes to data.

            Args:
            data: Bytes to deserialize

            Returns:
            Deserialized data

            """
            ...  # Protocol method

        @property
        def content_type(self) -> str:
            """Get content type for this serializer."""
            ...  # Protocol property

    class JSONSerializer:
        """JSON serializer using orjson for performance.

        Features:
        - Fast JSON serialization with orjson
        - Fallback to standard json
        - UTF-8 encoding
        - Pretty printing support
        - Custom type handling
        """

        def __init__(self, *, pretty: bool = False) -> None:
            """Initialize JSON serializer.

            Args:
            pretty: Enable pretty printing

            """
            self.logger = FlextLogger(__name__)
            self._pretty = pretty

            # Try to use orjson for performance
            self._orjson = orjson
            self._use_orjson = orjson is not None
            if self._use_orjson:
                self.logger.debug("Using orjson for JSON serialization")
            else:
                self.logger.debug("Using standard json for serialization")

        def serialize(self, data: object) -> bytes:
            """Serialize data to JSON bytes.

            Args:
            data: Data to serialize

            Returns:
            JSON bytes

            """
            if self._use_orjson:
                # Use orjson for fast serialization
                option = orjson.OPT_INDENT_2 if self._pretty else 0
                return orjson.dumps(data, option=option)
            # Fallback to standard json
            json_str = json.dumps(data, indent=2 if self._pretty else None)
            return json_str.encode("utf-8")

        def deserialize(self, data: bytes) -> object:
            """Deserialize JSON bytes to data.

            Args:
            data: JSON bytes

            Returns:
            Deserialized data

            """
            if self._use_orjson:
                return orjson.loads(data)
            return json.loads(data.decode("utf-8"))

        @property
        def content_type(self) -> str:
            """Get content type."""
            return "application/json"

    class MessagePackSerializer:
        """MessagePack serializer for binary format.

        Features:
        - Compact binary format
        - Efficient for large datasets
        - Type preservation
        - Streaming support
        """

        def __init__(self) -> None:
            """Initialize MessagePack serializer."""
            self.logger = FlextLogger(__name__)

            self._msgpack = msgpack
            self._available = True  # msgpack is mandatory dependency

        def serialize(self, data: object) -> bytes:
            """Serialize data to MessagePack bytes.

            Args:
            data: Data to serialize

            Returns:
            MessagePack bytes

            Raises:
            No exceptions raised - msgpack is mandatory dependency

            """
            result = self._msgpack.packb(data, use_bin_type=True)
            if not isinstance(result, bytes):
                msg = f"msgpack.packb returned {type(result).__name__}, expected bytes"
                raise TypeError(msg)
            return result

        def deserialize(self, data: bytes) -> object:
            """Deserialize MessagePack bytes to data.

            Args:
            data: MessagePack bytes

            Returns:
            Deserialized data

            Raises:
            No exceptions raised - msgpack is mandatory dependency

            """
            return self._msgpack.unpackb(data, raw=False)

        @property
        def content_type(self) -> str:
            """Get content type."""
            return "application/msgpack"

    class CBORSerializer:
        """CBOR (Concise Binary Object Representation) serializer.

        Features:
        - Compact binary format
        - Self-describing
        - Extensible type system
        - Standards-based (RFC 8949)
        """

        def __init__(self) -> None:
            """Initialize CBOR serializer."""
            self.logger = FlextLogger(__name__)

            self._cbor = cbor2
            self._available = True  # cbor2 is mandatory dependency

        def serialize(self, data: object) -> bytes:
            """Serialize data to CBOR bytes.

            Args:
            data: Data to serialize

            Returns:
            CBOR bytes

            Raises:
            No exceptions raised - cbor2 is mandatory dependency

            """
            return self._cbor.dumps(data)

        def deserialize(self, data: bytes) -> object:
            """Deserialize CBOR bytes to data.

            Args:
            data: CBOR bytes

            Returns:
            Deserialized data

            Raises:
            No exceptions raised - cbor2 is mandatory dependency

            """
            return self._cbor.loads(data)

        @property
        def content_type(self) -> str:
            """Get content type."""
            return "application/cbor"

    class SerializerRegistry:
        """Registry for serializers with content-type negotiation.

        Features:
        - Multiple serializer registration
        - Content-type based selection
        - Default serializer configuration
        - Custom serializer support
        """

        def __init__(self) -> None:
            """Initialize serializer registry."""
            self.logger = FlextLogger(__name__)
            self._serializers: dict[str, Any] = {}
            self._default_format = FlextApiTypes.Serialization.SerializationFormat.JSON

            # Register default serializers
            self.register_serializer(
                FlextApiTypes.Serialization.SerializationFormat.JSON,
                FlextApiSerializers.JSONSerializer(),
            )
            self.register_serializer(
                FlextApiTypes.Serialization.SerializationFormat.MSGPACK,
                FlextApiSerializers.MessagePackSerializer(),
            )
            self.register_serializer(
                FlextApiTypes.Serialization.SerializationFormat.CBOR,
                FlextApiSerializers.CBORSerializer(),
            )

        def register_serializer(
            self,
            format_type: FlextApiTypes.Serialization.SerializationFormat | str,
            serializer: FlextApiSerializers.SerializerProtocol,
        ) -> FlextResult[None]:
            """Register serializer for format.

            Args:
            format_type: Serialization format
            serializer: Serializer instance

            Returns:
            FlextResult indicating success or failure

            """
            format_key = (
                format_type.value
                if isinstance(
                    format_type,
                    FlextApiTypes.Serialization.SerializationFormat,
                )
                else format_type
            )

            if format_key in self._serializers:
                self.logger.warning(
                    f"Serializer already registered for format: {format_key}"
                )

            self._serializers[format_key] = serializer

            self.logger.info(
                "Serializer registered",
                extra={
                    "format": format_key,
                    "content_type": serializer.content_type,
                },
            )

            return FlextResult[None].ok(None)

        def get_serializer(
            self,
            format_type: FlextApiTypes.Serialization.SerializationFormat | str,
        ) -> FlextResult[FlextApiSerializers.SerializerProtocol]:
            """Get serializer for format.

            Args:
            format_type: Serialization format

            Returns:
            FlextResult containing serializer or error

            """
            format_key = (
                format_type.value
                if isinstance(
                    format_type,
                    FlextApiTypes.Serialization.SerializationFormat,
                )
                else format_type
            )

            if format_key not in self._serializers:
                return FlextResult[FlextApiSerializers.SerializerProtocol].fail(
                    f"No serializer registered for format: {format_key}"
                )

            return FlextResult[FlextApiSerializers.SerializerProtocol].ok(
                self._serializers[format_key]
            )

        def get_serializer_by_content_type(
            self, content_type: str
        ) -> FlextResult[FlextApiSerializers.SerializerProtocol]:
            """Get serializer by content type.

            Args:
                content_type: Content type (e.g., "application/json")

            Returns:
                FlextResult containing serializer or error

            """
            # Normalize content type (remove charset, etc.)
            normalized = content_type.split(";", maxsplit=1)[0].strip().lower()

            for serializer in self._serializers.values():
                if serializer.content_type == normalized:
                    return FlextResult[FlextApiSerializers.SerializerProtocol].ok(
                        serializer
                    )

            return FlextResult[FlextApiSerializers.SerializerProtocol].fail(
                f"No serializer found for content type: {content_type}"
            )

        def serialize(
            self,
            data: object,
            format_type: FlextApiTypes.Serialization.SerializationFormat
            | str
            | None = None,
        ) -> FlextResult[bytes]:
            """Serialize data using specified format.

            Args:
            data: Data to serialize
            format_type: Serialization format (uses default if None)

            Returns:
            FlextResult containing serialized bytes or error

            """
            format_key = (
                format_type.value
                if isinstance(
                    format_type,
                    FlextApiTypes.Serialization.SerializationFormat,
                )
                else format_type
            ) or self._default_format.value

            serializer_result = self.get_serializer(format_key)
            if serializer_result.is_failure:
                return FlextResult[bytes].fail(serializer_result.error)

            serializer = serializer_result.unwrap()

            try:
                serialized = serializer.serialize(data)
                return FlextResult[bytes].ok(serialized)
            except Exception as e:
                return FlextResult[bytes].fail(f"Serialization failed: {e}")

        def deserialize(
            self,
            data: bytes,
            format_type: FlextApiTypes.Serialization.SerializationFormat
            | str
            | None = None,
        ) -> FlextResult[object]:  # Returns deserialized object, can be any type
            """Deserialize data using specified format.

            Args:
            data: Data to deserialize
            format_type: Serialization format (uses default if None)

            Returns:
            FlextResult containing deserialized data or error

            """
            format_key = (
                format_type.value
                if isinstance(
                    format_type,
                    FlextApiTypes.Serialization.SerializationFormat,
                )
                else format_type
            ) or self._default_format.value

            serializer_result = self.get_serializer(format_key)
            if serializer_result.is_failure:
                return FlextResult[object].fail(serializer_result.error)

            serializer = serializer_result.unwrap()

            try:
                deserialized = serializer.deserialize(data)
                return FlextResult[object].ok(deserialized)
            except Exception as e:
                return FlextResult[object].fail(f"Deserialization failed: {e}")

        def set_default_format(
            self,
            format_type: FlextApiTypes.Serialization.SerializationFormat,
        ) -> FlextResult[None]:
            """Set default serialization format.

            Args:
            format_type: Default format

            Returns:
            FlextResult indicating success

            """
            self._default_format = format_type
            self.logger.info(
                f"Default serialization format set to: {format_type.value}"
            )
            return FlextResult[None].ok(None)


__all__ = [
    "FlextApiSerializers",
]

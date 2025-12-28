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

import cbor2
import msgpack
import orjson
from flext_core import FlextService, r
from flext_core.loggings import FlextLogger

from flext_api.constants import FlextApiConstants
from flext_api.protocols import p


class FlextApiSerializers(FlextService[bool]):
    """Unified serialization service with multiple format support.

    Provides JSON, MessagePack, and CBOR serialization through nested classes.
    Follows FLEXT standards with FlextResult error handling.

    Protocols:
        Use p.Api.Serialization.SerializerProtocol for custom serializers.
    """

    def execute(self, **kwargs: object) -> r[bool]:
        """Execute FlextService interface - serializers are always ready."""
        if kwargs:
            FlextLogger(__name__).info(
                f"Serializer.execute received kwargs: {list(kwargs.keys())}",
            )
        return r[bool].ok(True)

    class JSONSerializer:
        """JSON serializer using orjson for performance.

        Features:
        - Fast JSON serialization with orjson
        - UTF-8 encoding
        - Pretty printing support
        - Custom type handling
        """

        def __init__(self, *, pretty: bool = False) -> None:
            """Initialize JSON serializer.

            Args:
            pretty: Enable pretty printing

            """
            self._logger = FlextLogger(__name__)
            self._pretty = pretty

            # Use orjson for performance - required dependency
            if orjson is None:
                error_msg = (
                    "orjson is required for JSON serialization. "
                    "Install with: pip install orjson"
                )
                raise ImportError(error_msg)
            self._logger.debug("Using orjson for JSON serialization")

        def serialize(self, data: object) -> bytes:
            """Serialize data to JSON bytes.

            Args:
            data: Data to serialize

            Returns:
            JSON bytes

            """
            # Use orjson for fast serialization
            option = orjson.OPT_INDENT_2 if self._pretty else 0
            return orjson.dumps(data, option=option)

        def deserialize(self, data: bytes) -> object:
            """Deserialize JSON bytes to data.

            Args:
            data: JSON bytes

            Returns:
            Deserialized data

            """
            # Use orjson for fast deserialization
            return orjson.loads(data)

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
            self._logger = FlextLogger(__name__)
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
            return "application/x-msgpack"

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
            self._logger = FlextLogger(__name__)
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
            self._logger = FlextLogger(__name__)
            self._serializers: dict[str, p.Api.Serialization.SerializerProtocol] = {}
            self._default_format = FlextApiConstants.Api.HttpSerializationFormat.JSON

            # Register default serializers
            self.register_serializer(
                FlextApiConstants.Api.HttpSerializationFormat.JSON,
                FlextApiSerializers.JSONSerializer(),
            )
            self.register_serializer(
                FlextApiConstants.Api.HttpSerializationFormat.MSGPACK,
                FlextApiSerializers.MessagePackSerializer(),
            )
            self.register_serializer(
                FlextApiConstants.Api.HttpSerializationFormat.CBOR,
                FlextApiSerializers.CBORSerializer(),
            )

        def register_serializer(
            self,
            format_type: FlextApiConstants.Api.HttpSerializationFormat | str,
            serializer: p.Api.Serialization.SerializerProtocol,
        ) -> r[bool]:
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
                    FlextApiConstants.Api.HttpSerializationFormat,
                )
                else format_type
            )

            if format_key in self._serializers:
                FlextLogger(__name__).warning(
                    "Serializer already registered for format: %s",
                    format_key,
                )

            self._serializers[format_key] = serializer

            FlextLogger(__name__).info(
                "Serializer registered",
                extra={
                    "format": format_key,
                    "content_type": serializer.content_type,
                },
            )

            return r[bool].ok(True)

        def get_serializer(
            self,
            format_type: FlextApiConstants.Api.HttpSerializationFormat | str,
        ) -> r[p.Api.Serialization.SerializerProtocol]:
            """Get serializer for format or content-type.

            Tries to find serializer by format first, then by content-type.

            Args:
            format_type: Serialization format ("json") or content-type ("application/json")

            Returns:
            FlextResult containing serializer or error

            """
            format_key = (
                format_type.value
                if isinstance(
                    format_type,
                    FlextApiConstants.Api.HttpSerializationFormat,
                )
                else format_type
            )

            # Try by format key first
            if format_key in self._serializers:
                return r[p.Api.Serialization.SerializerProtocol].ok(
                    self._serializers[format_key],
                )

            # Try by content-type if format key not found
            for serializer in self._serializers.values():
                if (
                    serializer.content_type
                    == format_key.split(";", maxsplit=1)[0].strip().lower()
                ):
                    return r[p.Api.Serialization.SerializerProtocol].ok(serializer)

            return r[p.Api.Serialization.SerializerProtocol].fail(
                f"No serializer registered for format: {format_key}",
            )

        def get_serializer_by_content_type(
            self,
            content_type: str,
        ) -> r[p.Api.Serialization.SerializerProtocol]:
            """Get serializer by content type.

            Args:
                content_type: Content type (e.g., "application/json")

            Returns:
                FlextResult containing serializer or error

            """
            # Normalize content type (remove charset, etc.)
            for serializer in self._serializers.values():
                if (
                    serializer.content_type
                    == content_type.split(";", maxsplit=1)[0].strip().lower()
                ):
                    return r[p.Api.Serialization.SerializerProtocol].ok(serializer)

            return r[p.Api.Serialization.SerializerProtocol].fail(
                f"No serializer found for content type: {content_type}",
            )

        def serialize(
            self,
            data: object,
            format_type: FlextApiConstants.Api.HttpSerializationFormat
            | str
            | None = None,
        ) -> r[bytes]:
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
                    FlextApiConstants.Api.HttpSerializationFormat,
                )
                else format_type
            )
            if not format_key:
                format_key = self._default_format.value

            serializer_result = self.get_serializer(format_key)
            if serializer_result.is_failure:
                return r[bytes].fail(
                    serializer_result.error or "Serializer retrieval failed",
                )

            try:
                serialized = serializer_result.value.serialize(data)
                return r[bytes].ok(serialized)
            except Exception as e:
                return r[bytes].fail(f"Serialization failed: {e}")

        def deserialize(
            self,
            data: bytes,
            format_type: FlextApiConstants.Api.HttpSerializationFormat
            | str
            | None = None,
        ) -> r[object]:  # Returns deserialized object, can be any type
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
                    FlextApiConstants.Api.HttpSerializationFormat,
                )
                else format_type
            )
            if not format_key:
                format_key = self._default_format.value

            serializer_result = self.get_serializer(format_key)
            if serializer_result.is_failure:
                return r[object].fail(
                    serializer_result.error or "Serializer retrieval failed",
                )

            try:
                deserialized = serializer_result.value.deserialize(data)
                return r[object].ok(deserialized)
            except Exception as e:
                return r[object].fail(f"Deserialization failed: {e}")

        def set_default_format(
            self,
            format_type: FlextApiConstants.Api.HttpSerializationFormat,
        ) -> r[bool]:
            """Set default serialization format.

            Args:
            format_type: Default format

            Returns:
            FlextResult indicating success

            """
            self._default_format = format_type
            FlextLogger(__name__).info(
                f"Default serialization format set to: {format_type.value}",
            )
            return r[bool].ok(True)


__all__ = [
    "FlextApiSerializers",
]

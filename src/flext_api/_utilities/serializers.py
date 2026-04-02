"""Serialization utilities for flext-api.

Provides type-safe wrappers for untyped serialization libraries like msgpack.
"""

from __future__ import annotations

import msgpack
from pydantic import ValidationError

from flext_api import t
from flext_core import r


class FlextApiSerializers:
    """Serialization utilities for API operations."""

    class MessagePack:
        """Type-safe wrappers for msgpack library."""

        @staticmethod
        def pack_raw(obj: t.JsonValue) -> object:
            """Return the raw msgpack payload for explicit runtime narrowing."""
            return t.Api.BINARY_CONTENT_ADAPTER.validate_python(msgpack.packb(obj))

        @staticmethod
        def packb(obj: t.JsonValue) -> bytes:
            """Type-safe wrapper for msgpack.packb().

            Args:
                obj: Object to pack using the canonical `t.JsonValue` contract.

            Returns:
                bytes: Packed binary data.

            """
            packed = FlextApiSerializers.MessagePack.pack_raw(obj)
            if isinstance(packed, bytes):
                return packed
            if isinstance(packed, bytearray):
                return bytes(packed)
            msg = "msgpack.packb returned non-bytes payload"
            raise TypeError(msg)

        @staticmethod
        def unpackb(
            data: bytes,
        ) -> r[t.JsonValue]:
            """Type-safe wrapper for msgpack.unpackb().

            Args:
                data: Binary data to unpack.

            Returns:
                Result containing unpacked `t.JsonValue`.

            """
            try:
                result = msgpack.unpackb(data)
                validated = t.Api.JSON_VALUE_ADAPTER.validate_python(result)
                return r[t.JsonValue].ok(
                    validated,
                )
            except (TypeError, ValidationError, ValueError) as e:
                return r[t.JsonValue].fail(f"msgpack deserialization failed: {e}")

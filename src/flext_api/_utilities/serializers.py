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

    @staticmethod
    def _load_msgpack() -> object | None:
        """Return the msgpack module used by the serializers."""
        return msgpack

    class MessagePack:
        """Type-safe wrappers for msgpack library."""

        @staticmethod
        def pack_raw(obj: t.JsonValue) -> object:
            """Return the raw msgpack payload for explicit runtime narrowing."""
            module = FlextApiSerializers._load_msgpack()
            if module is None:
                msg = "msgpack module not available"
                raise TypeError(msg)
            packb = getattr(module, "packb", None)
            if not callable(packb):
                msg = "msgpack.packb function not found"
                raise TypeError(msg)
            return t.Api.BINARY_CONTENT_ADAPTER.validate_python(packb(obj))

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
            module = FlextApiSerializers._load_msgpack()
            if module is None:
                return r[t.JsonValue].fail("msgpack module not available")
            unpackb = getattr(module, "unpackb", None)
            if not callable(unpackb):
                return r[t.JsonValue].fail("msgpack.unpackb function not found")
            try:
                result = unpackb(data)
                validated = t.Api.JSON_VALUE_ADAPTER.validate_python(result)
                return r[t.JsonValue].ok(
                    validated,
                )
            except (TypeError, ValidationError, ValueError) as e:
                return r[t.JsonValue].fail(f"msgpack deserialization failed: {e}")

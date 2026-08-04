"""Serialization utilities for flext-api.

Provides type-safe wrappers for untyped serialization libraries like msgpack.
"""

from __future__ import annotations

import msgpack

from flext_api import c, p, r, t


class FlextApiUtilitiesSerializers:
    """Serialization utilities for API operations."""

    @staticmethod
    def packb(obj: t.JsonPayload) -> bytes:
        """Type-safe wrapper for msgpack.packb().

        Args:
            obj: Object to pack using the shared metadata payload contract.

        Returns:
            bytes: Packed binary data.

        """
        normalized = t.Api.API_JSON_VALUE_ADAPTER.validate_python(obj)
        packed = t.Api.BINARY_CONTENT_ADAPTER.validate_python(msgpack.packb(normalized))
        if isinstance(packed, bytes):
            return packed
        return bytes(packed)

    @staticmethod
    def unpackb(data: bytes) -> p.Result[t.JsonValue]:
        """Type-safe wrapper for msgpack.unpackb().

        Args:
            data: Binary data to unpack.

        Returns:
            Result containing unpacked t.JsonValue.

        """
        try:
            result = msgpack.unpackb(data)
            if result is None:
                return r[t.JsonValue].fail(
                    "msgpack nil is forbidden because None cannot be a "
                    "success payload"
                )
            normalized = t.Api.API_JSON_VALUE_ADAPTER.validate_python(result)
            return r[t.JsonValue].ok(normalized)
        except c.EXC_VALIDATION_TYPE_VALUE as e:
            return r[t.JsonValue].fail_op("msgpack deserialization", e)

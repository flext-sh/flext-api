"""Serialization utilities for flext-api.

Provides type-safe wrappers for untyped serialization libraries like msgpack.
"""

from __future__ import annotations

from typing import TypeIs

import msgpack

from flext_api import c, p, r, t, u


class FlextApiUtilitiesSerializers:
    """Serialization utilities for API operations."""

    @staticmethod
    def _is_msgpack_module(value: object) -> TypeIs[p.Api.Serialization.MsgpackModule]:
        """Return whether the value satisfies the msgpack module protocol."""
        return callable(getattr(value, "packb", None)) and callable(
            getattr(value, "unpackb", None),
        )

    @staticmethod
    def _load_msgpack() -> p.Api.Serialization.MsgpackModule | None:
        """Return the msgpack module used by the serializers."""
        return (
            msgpack
            if FlextApiUtilitiesSerializers._is_msgpack_module(msgpack)
            else None
        )

    @staticmethod
    def pack_raw(obj: t.RecursiveValue) -> t.Api.MsgpackBinary:
        """Return the raw msgpack payload for explicit runtime narrowing."""
        module = FlextApiUtilitiesSerializers._load_msgpack()
        if module is None:
            msg = "msgpack module not available"
            raise TypeError(msg)
        return t.Api.BINARY_CONTENT_ADAPTER.validate_python(module.packb(obj))

    @staticmethod
    def packb(obj: t.RecursiveValue) -> bytes:
        """Type-safe wrapper for msgpack.packb().

        Args:
            obj: Object to pack using the canonical t.RecursiveValue contract.

        Returns:
            bytes: Packed binary data.

        """
        packed = FlextApiUtilitiesSerializers.pack_raw(obj)
        if isinstance(packed, bytes):
            return packed
        if isinstance(packed, bytearray):
            return bytes(packed)
        msg = "msgpack.packb returned non-bytes payload"
        raise TypeError(msg)

    @staticmethod
    def unpackb(
        data: bytes,
    ) -> p.Result[t.RecursiveValue]:
        """Type-safe wrapper for msgpack.unpackb().

        Args:
            data: Binary data to unpack.

        Returns:
            Result containing unpacked t.RecursiveValue.

        """
        module = FlextApiUtilitiesSerializers._load_msgpack()
        if module is None:
            return r[t.RecursiveValue].fail("msgpack module not available")
        try:
            result = module.unpackb(data)
            return u.validate_value(t.RecursiveValue, result)
        except (TypeError, c.ValidationError, ValueError) as e:
            return r[t.RecursiveValue].fail(f"msgpack deserialization failed: {e}")

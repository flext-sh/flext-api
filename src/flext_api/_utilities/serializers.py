"""Serialization utilities for flext-api.

Provides type-safe wrappers for untyped serialization libraries like msgpack.
"""

from __future__ import annotations

from typing import TypeIs

import msgpack

from flext_api import c, p, t
from flext_core import r, u


class FlextApiUtilitiesSerializers:
    """Serialization utilities for API operations."""

    @staticmethod
    def _is_msgpack_module(
        value: t.RuntimeModule | p.Api.MsgpackModule,
    ) -> TypeIs[p.Api.MsgpackModule]:
        """Return whether the runtime module satisfies the msgpack contract."""
        return callable(getattr(value, "packb", None)) and callable(
            getattr(value, "unpackb", None),
        )

    @staticmethod
    def pack_raw(obj: t.ApiJsonValue) -> t.Api.MsgpackBinary:
        """Return the raw msgpack payload for explicit runtime narrowing."""
        module = msgpack
        if not FlextApiUtilitiesSerializers._is_msgpack_module(module):
            msg = "msgpack module not available"
            raise TypeError(msg)
        return t.Api.BINARY_CONTENT_ADAPTER.validate_python(module.packb(obj))

    @staticmethod
    def packb(obj: t.ApiJsonValue) -> bytes:
        """Type-safe wrapper for msgpack.packb().

        Args:
            obj: Object to pack using the canonical t.ApiJsonValue contract.

        Returns:
            bytes: Packed binary data.

        """
        packed = FlextApiUtilitiesSerializers.pack_raw(obj)
        if isinstance(packed, bytes):
            return packed
        return bytes(packed)

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
        try:
            module = msgpack
            if not FlextApiUtilitiesSerializers._is_msgpack_module(module):
                return r[t.RecursiveValue].fail("msgpack module not available")
            result = module.unpackb(data)
            return u.validate_value(t.RecursiveValue, result)
        except (TypeError, c.ValidationError, ValueError) as e:
            return r[t.RecursiveValue].fail(f"msgpack deserialization failed: {e}")

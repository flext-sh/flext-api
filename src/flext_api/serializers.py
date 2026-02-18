"""Serialization utilities for flext-api.

Provides type-safe wrappers for untyped serialization libraries like msgpack.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import msgpack as _msgpack
from flext_core.typings import t


class FlextApiSerializers:
    """Serialization utilities for API operations."""

    class MessagePack:
        """Type-safe wrappers for msgpack library."""

        @staticmethod
        def packb(
            obj: dict[
                str,
                str
                | int
                | float
                | bool
                | Sequence[object]
                | Mapping[str, object]
                | None,
            ]
            | t.GeneralValueType,
        ) -> bytes:
            """Type-safe wrapper for msgpack.packb().

            Args:
                obj: Object to pack (JsonObject or GeneralValueType).

            Returns:
                bytes: Packed binary data.

            """
            result = _msgpack.packb(obj)
            if isinstance(result, bytes):
                return result
            # Fallback - should not reach here with valid msgpack
            return bytes(result) if result is not None else b""

        @staticmethod
        def unpackb(
            data: bytes,
        ) -> str | int | float | bool | dict[str, object] | list[object] | None:
            """Type-safe wrapper for msgpack.unpackb().

            Args:
                data: Binary data to unpack.

            Returns:
                Unpacked object (dict, list, scalar, or None).

            """
            unpackb_fn = getattr(_msgpack, "unpackb", None)
            if unpackb_fn is None:
                return None
            # Return the raw result; caller must narrow to GeneralValueType if needed
            return unpackb_fn(data)

"""Serialization utilities for flext-api.

Provides type-safe wrappers for untyped serialization libraries like msgpack.
"""

from __future__ import annotations

import importlib
from collections.abc import Mapping, Sequence
from types import ModuleType

from flext_core.typings import t


def _load_msgpack() -> ModuleType | None:
    """Load msgpack lazily to avoid static typing dependency issues."""
    try:
        module = importlib.import_module("msgpack")
    except ModuleNotFoundError:
        return None
    return module if isinstance(module, ModuleType) else None


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
            module = _load_msgpack()
            if module is None:
                return b""
            packb_fn = getattr(module, "packb", None)
            if not callable(packb_fn):
                return b""

            result = packb_fn(obj)
            if isinstance(result, bytes):
                return result
            if isinstance(result, bytearray | memoryview):
                return bytes(result)
            return b""

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
            module = _load_msgpack()
            if module is None:
                return None
            unpackb_fn = getattr(module, "unpackb", None)
            if unpackb_fn is None:
                return None
            # Return the raw result; caller must narrow to GeneralValueType if needed
            result = unpackb_fn(data)
            if (
                isinstance(result, str | int | float | bool | dict | list)
                or result is None
            ):
                return result
            return None

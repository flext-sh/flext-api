"""Serialization utilities for flext-api.

Provides type-safe wrappers for untyped serialization libraries like msgpack.
"""

from __future__ import annotations

import importlib
from collections.abc import Mapping, Sequence
from types import ModuleType

from pydantic import TypeAdapter, ValidationError

from flext_api import t

_MESSAGEPACK_RESULT_ADAPTER = TypeAdapter(
    str | int | float | bool | Mapping[str, object] | list[object] | None,
)


def _load_msgpack() -> ModuleType | None:
    """Load msgpack lazily to avoid static typing dependency issues."""
    try:
        module = importlib.import_module("msgpack")
    except ModuleNotFoundError:
        return None
    return module


class FlextApiSerializers:
    """Serialization utilities for API operations."""

    class MessagePack:
        """Type-safe wrappers for msgpack library."""

        @staticmethod
        def packb(
            obj: Mapping[
                str,
                str
                | int
                | float
                | bool
                | Sequence[object]
                | Mapping[str, object]
                | None,
            ]
            | t.ApiJsonValue,
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
            if isinstance(result, bytes | bytearray):
                return bytes(result)
            return b""

        @staticmethod
        def unpackb(
            data: bytes,
        ) -> str | int | float | bool | Mapping[str, object] | list[object] | None:
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
            result = unpackb_fn(data)
            try:
                return _MESSAGEPACK_RESULT_ADAPTER.validate_python(result)
            except ValidationError:
                return None

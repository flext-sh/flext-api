"""Serialization utilities for flext-api.

Provides type-safe wrappers for untyped serialization libraries like msgpack.
"""

from __future__ import annotations

import importlib
from collections.abc import Mapping, Sequence
from types import ModuleType

from flext_core import r
from pydantic import TypeAdapter, ValidationError

from flext_api import t

_MESSAGEPACK_RESULT_ADAPTER: TypeAdapter[
    t.Scalar | Mapping[str, t.ContainerValue] | list[t.ContainerValue] | None
] = TypeAdapter(
    t.Scalar | Mapping[str, t.ContainerValue] | list[t.ContainerValue] | None,
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
                t.Scalar | Sequence[t.Scalar] | Mapping[str, t.ContainerValue] | None,
            ]
            | t.ApiJsonValue,
        ) -> bytes:
            """Type-safe wrapper for msgpack.packb().

            Args:
                obj: Object to pack (JsonObject or object).

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
        ) -> r[t.Scalar | Mapping[str, t.ContainerValue] | list[t.ContainerValue]]:
            """Type-safe wrapper for msgpack.unpackb().

            Args:
                data: Binary data to unpack.

            Returns:
                Result containing unpacked object (dict, list, or scalar).

            """
            module = _load_msgpack()
            if module is None:
                return r[
                    t.Scalar | Mapping[str, t.ContainerValue] | list[t.ContainerValue]
                ].fail("msgpack module not available")
            unpackb_fn = getattr(module, "unpackb", None)
            if unpackb_fn is None:
                return r[
                    t.Scalar | Mapping[str, t.ContainerValue] | list[t.ContainerValue]
                ].fail("msgpack.unpackb function not found")
            try:
                result = unpackb_fn(data)
                validated = _MESSAGEPACK_RESULT_ADAPTER.validate_python(result)
                if validated is None:
                    return r[
                        t.Scalar
                        | Mapping[str, t.ContainerValue]
                        | list[t.ContainerValue]
                    ].fail("msgpack deserialization returned None")
                non_none_value: (
                    t.Scalar | Mapping[str, t.ContainerValue] | list[t.ContainerValue]
                ) = validated
                return r[
                    t.Scalar | Mapping[str, t.ContainerValue] | list[t.ContainerValue]
                ].ok(non_none_value)
            except (ValidationError, Exception) as e:
                return r[
                    t.Scalar | Mapping[str, t.ContainerValue] | list[t.ContainerValue]
                ].fail(f"msgpack deserialization failed: {e}")

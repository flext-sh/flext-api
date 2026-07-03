"""Serialization type aliases for flext-api private typing composition."""

from __future__ import annotations


class FlextApiTypingsSerialization:
    """Serialization-domain type aliases exposed through ``t.Api``."""

    type MsgpackBinary = bytes | bytearray
    """Canonical binary payload produced by msgpack pack operations."""


__all__: list[str] = ["FlextApiTypingsSerialization"]

"""Serialization protocol contracts for flext-api internal composition."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_api import t


@runtime_checkable
class FlextApiProtocolsSerialization(Protocol):
    """Serialization-domain protocol mixins."""

    @runtime_checkable
    class MsgpackModule(Protocol):
        """Structural contract for the msgpack module entrypoints in use."""

        def packb(self, obj: t.JsonPayload) -> bytes | bytearray:
            """Pack recursive payload to binary msgpack content."""
            ...

        def unpackb(self, data: bytes) -> t.JsonValue:
            """Unpack msgpack binary content into recursive payload."""
            ...


__all__: list[str] = ["FlextApiProtocolsSerialization"]

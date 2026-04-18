"""Serialization protocol contracts for flext-api internal composition."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from flext_api import t


class FlextApiProtocolsSerialization(Protocol):
    """Serialization-domain protocol mixins."""

    @runtime_checkable
    class MsgpackModule(Protocol):
        """Structural contract for the msgpack module entrypoints in use."""

        def packb(self, obj: t.ContainerValue | None) -> bytes | bytearray:
            """Pack recursive payload to binary msgpack content."""
            ...

        def unpackb(self, data: bytes) -> t.RecursiveValue:
            """Unpack msgpack binary content into recursive payload."""
            ...


__all__: list[str] = ["FlextApiProtocolsSerialization"]

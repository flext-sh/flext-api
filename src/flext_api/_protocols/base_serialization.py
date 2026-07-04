"""Serialization protocol shard."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from flext_api import t


class FlextApiProtocolsSerializer:
    """Serialization protocol shard."""

    @runtime_checkable
    class Serializer(Protocol):
        """Protocol for custom serializers."""

        @property
        def content_type(self) -> str:
            """Get content type for this serializer."""
            ...

        def deserialize(self, data: bytes) -> t.JsonValue:
            """Deserialize bytes to data."""
            ...

        def serialize(self, data: t.JsonValue) -> bytes:
            """Serialize data to bytes."""
            ...


__all__: list[str] = ["FlextApiProtocolsSerializer"]

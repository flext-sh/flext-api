"""Serialization protocol shard."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_api import t


class FlextApiProtocolsSerializer:
    """Serialization protocol shard."""

    @runtime_checkable
    class Serializer(Protocol):
        """Protocol for custom serializers."""

        @property
        def content_type(self) -> str:
            """Content type for this serializer."""
            ...

        def deserialize(self, data: bytes) -> t.JsonValue:
            """Deserialize bytes to data."""
            ...

        def serialize(self, data: t.JsonValue) -> bytes:
            """Serialize data to bytes."""
            ...


__all__: list[str] = ["FlextApiProtocolsSerializer"]

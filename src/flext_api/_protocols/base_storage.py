"""Storage backend protocol shard."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from flext_api import t
    from flext_web import p


class FlextApiProtocolsStorage:
    """Storage protocol shard."""

    @runtime_checkable
    class StorageBackend(Protocol):
        """Protocol for generic storage backend implementations."""

        def clear(self) -> p.Result[bool]:
            """Clear all stored values."""
            ...

        def delete(self, key: str) -> p.Result[bool]:
            """Delete value by key."""
            ...

        def exists(self, key: str) -> p.Result[bool]:
            """Check if key exists."""
            ...

        def get(self, key: str) -> p.Result[t.JsonValue]:
            """Retrieve value by key."""
            ...

        def keys(self) -> p.Result[t.StrSequence]:
            """Get all keys."""
            ...

        def set(
            self, key: str, value: t.JsonValue, timeout: int | None = None
        ) -> p.Result[bool]:
            """Store value with optional timeout."""
            ...


__all__: list[str] = ["FlextApiProtocolsStorage"]

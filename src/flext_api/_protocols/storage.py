# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_api/_protocols/storage
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol, runtime_checkable

from flext_cli import FlextCliProtocols

from flext_api import t


class FlextApiProtocolsStorage:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class StorageSettings(FlextCliProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def namespace(self) -> str:
            """Logical namespace for this storage instance."""
            ...

        @property
        def backend(self) -> str:
            """Storage backend identifier."""
            ...

        @property
        def max_size(self) -> int | None:
            """Maximum number of entries kept in memory."""
            ...

        @property
        def default_ttl(self) -> int | None:
            """Default entry TTL in seconds."""
            ...

    @runtime_checkable
    class StorageMetadata(FlextCliProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def value(self) -> t.JsonValue:
            """Stored JSON-compatible value payload."""
            ...

        @property
        def timestamp(self) -> str:
            """Entry creation timestamp in ISO format."""
            ...

        @property
        def ttl(self) -> t.Numeric | None:
            """Optional time-to-live seconds."""
            ...

        @property
        def created_at(self) -> float:
            """Monotonic creation timestamp."""
            ...

        @property
        def expired(self) -> bool:
            """Whether the entry is expired."""
            ...

    @runtime_checkable
    class StorageState(FlextCliProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def entries(self) -> Mapping[str, FlextApiProtocolsStorage.StorageMetadata]:
            """Storage entries by key."""
            ...

        operations_count: int
        cache_hits: int
        cache_misses: int
        created_at: str

    @runtime_checkable
    class StorageStats(FlextCliProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def total_operations(self) -> int:
            """Total storage operations count."""
            ...

        @property
        def cache_hits(self) -> int:
            """Number of cache hits."""
            ...

        @property
        def cache_misses(self) -> int:
            """Number of cache misses."""
            ...

        @property
        def storage_size(self) -> int:
            """Current storage size in entries."""
            ...

        @property
        def memory_usage(self) -> int:
            """Estimated memory usage in bytes."""
            ...

        @property
        def namespace(self) -> str:
            """Storage namespace identifier."""
            ...

        @property
        def hit_ratio(self) -> float:
            """Cache hit ratio."""
            ...


__all__: list[str] = [
    "FlextApiProtocolsStorage",
]

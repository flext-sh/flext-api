"""API storage models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

import time
from collections.abc import MutableMapping, MutableSequence
from datetime import UTC, datetime
from typing import Annotated, ClassVar

from flext_web import m

from flext_api import t


class FlextApiModelsStorage:
    """Storage model shard for ``m.Api``."""

    """Storage-related models namespace."""

    class StorageSettings(m.Value):
        """Canonical storage settings."""

        namespace: str = m.Field(
            default="flext_api",
            description="Logical namespace for this storage instance",
            validate_default=True,
        )
        backend: str = m.Field(
            default="memory",
            description="Storage backend identifier",
            validate_default=True,
        )
        max_size: int | None = m.Field(
            default=None,
            description="Maximum number of entries kept in memory",
            gt=0,
            validate_default=True,
        )
        default_ttl: int | None = m.Field(
            default=None,
            description="Default entry TTL in seconds",
            gt=0,
            validate_default=True,
        )

    class StorageMetadata(m.Value):
        """Internal metadata for stored values."""

        _flext_enforcement_exempt: ClassVar[bool] = True

        value: Annotated[
            t.JsonValue,
            m.Field(description="Stored JSON-compatible value payload"),
        ]
        timestamp: Annotated[
            str,
            m.Field(description="Entry creation timestamp in ISO format"),
        ]
        ttl: Annotated[
            t.Numeric | None,
            m.Field(default=None, description="Optional time-to-live seconds"),
        ] = None
        created_at: Annotated[
            float,
            m.Field(
                description="Monotonic creation timestamp",
            ),
        ] = m.Field(default_factory=time.time)

        @property
        def expired(self) -> bool:
            """Whether the entry is expired."""
            if self.ttl is None:
                return False
            return time.time() - self.created_at > float(self.ttl)

    class StorageState(m.FlexibleInternalModel):
        """Mutable storage runtime state kept in one central model."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
            extra="forbid",
            validate_assignment=True,
        )
        entries: MutableMapping[str, FlextApiModelsStorage.StorageMetadata] = m.Field(
            default_factory=dict[str, "FlextApiModelsStorage.StorageMetadata"],
            description="Storage entries by key",
        )
        operations_count: int = m.Field(
            0,
            description="Total operations performed by this storage",
            validate_default=True,
        )
        cache_hits: int = m.Field(
            0,
            description="Successful cache reads",
            validate_default=True,
        )
        cache_misses: int = m.Field(
            0,
            description="Failed cache reads",
            validate_default=True,
        )
        created_at: str = m.Field(
            default_factory=lambda: (
                datetime.now(UTC).replace(microsecond=0).isoformat()
            ),
            description="Creation timestamp for this storage instance",
        )

    class StorageStats(m.Value):
        """Storage statistics model."""

        total_operations: int = m.Field(
            0,
            description="Total storage operations count",
            validate_default=True,
        )
        cache_hits: int = m.Field(
            0,
            description="Number of cache hits",
            validate_default=True,
        )
        cache_misses: int = m.Field(
            0,
            description="Number of cache misses",
            validate_default=True,
        )
        storage_size: int = m.Field(
            0,
            description="Current storage size in entries",
            validate_default=True,
        )
        memory_usage: int = m.Field(
            0,
            description="Estimated memory usage in bytes",
            validate_default=True,
        )
        namespace: str = m.Field(
            "flext",
            description="Storage namespace identifier",
            validate_default=True,
        )

        @property
        def hit_ratio(self) -> float:
            """Cache hit ratio."""
            if self.total_operations == 0:
                return 0.0
            return self.cache_hits / self.total_operations


__all__: MutableSequence[str] = ["FlextApiModelsStorage"]

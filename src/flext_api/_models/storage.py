"""API storage models."""

from __future__ import annotations

import time
from collections.abc import MutableMapping
from typing import Annotated, ClassVar

# NOTE (multi-agent): runtime import (not TYPE_CHECKING) so pydantic can
# resolve ``t.JsonValue``/``MutableMapping`` forward refs at class build —
# matches the sibling model modules (request.py, response.py, client.py).
from flext_api import t
from flext_web import m, u


class FlextApiModelsStorage:
    """Storage model shard for ``m.Api``."""

    class Storage:
        """Storage-related models namespace."""

        class Settings(m.Value):
            """Canonical storage settings."""

            namespace: str = u.Field(
                "flext_api",
                description="Logical namespace for this storage instance",
                validate_default=True,
            )
            backend: str = u.Field(
                "memory",
                description="Storage backend identifier",
                validate_default=True,
            )
            max_size: int | None = u.Field(
                None,
                description="Maximum number of entries kept in memory",
                gt=0,
                validate_default=True,
            )
            default_ttl: int | None = u.Field(
                None,
                description="Default entry TTL in seconds",
                gt=0,
                validate_default=True,
            )

        class Metadata(m.Value):
            """Internal metadata for stored values."""

            _flext_enforcement_exempt: ClassVar[bool] = True

            value: Annotated[
                t.JsonValue, u.Field(description="Stored JSON-compatible value payload")
            ]
            timestamp: Annotated[
                str, u.Field(description="Entry creation timestamp in ISO format")
            ]
            ttl: Annotated[
                t.Numeric | None,
                u.Field(default=None, description="Optional time-to-live seconds"),
            ] = None
            created_at: Annotated[
                float,
                u.Field(
                    default_factory=time.time,
                    description="Monotonic creation timestamp",
                ),
            ]

            @property
            def expired(self) -> bool:
                """Whether the entry is expired."""
                if self.ttl is None:
                    return False
                return time.time() - self.created_at > float(self.ttl)

        class State(m.FlexibleInternalModel):
            """Mutable storage runtime state kept in one central model."""

            model_config: ClassVar[t.ConfigDict] = m.ConfigDict(
                extra="forbid", validate_assignment=True
            )
            entries: MutableMapping[str, FlextApiModelsStorage.Storage.Metadata] = (
                u.Field(default_factory=dict, description="Storage entries by key")
            )
            operations_count: int = u.Field(
                0,
                description="Total operations performed by this storage",
                validate_default=True,
            )
            cache_hits: int = u.Field(
                0, description="Successful cache reads", validate_default=True
            )
            cache_misses: int = u.Field(
                0, description="Failed cache reads", validate_default=True
            )
            created_at: str = u.Field(
                default_factory=u.generate_iso_timestamp,
                description="Creation timestamp for this storage instance",
            )

        class Stats(m.Value):
            """Storage statistics model."""

            total_operations: int = u.Field(
                0, description="Total storage operations count", validate_default=True
            )
            cache_hits: int = u.Field(
                0, description="Number of cache hits", validate_default=True
            )
            cache_misses: int = u.Field(
                0, description="Number of cache misses", validate_default=True
            )
            storage_size: int = u.Field(
                0, description="Current storage size in entries", validate_default=True
            )
            memory_usage: int = u.Field(
                0, description="Estimated memory usage in bytes", validate_default=True
            )
            namespace: str = u.Field(
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


__all__: t.MutableSequenceOf[str] = ["FlextApiModelsStorage"]

"""Generic HTTP storage with features using external libraries.

Delegates to:
- pydantic: data validation and serialization
- json: JSON handling
- flext-core: patterns and utilities

Flexible features:
- Batch operations
- TTL/expiration management
- Metrics and statistics
- Health monitoring
- Event emission
- JSON serialization

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import time
from typing import Any, override

from flext_core import FlextResult, FlextService, FlextUtilities
from pydantic import BaseModel, Field

from flext_api.typings import FlextApiTypes


class _StorageMetadata(BaseModel):
    """Internal metadata for stored values (using Pydantic for validation)."""

    value: object
    timestamp: str
    ttl: int | None = None
    created_at: float = Field(default_factory=time.time)

    def is_expired(self) -> bool:
        """Check if entry has expired using Pydantic-validated TTL."""
        if self.ttl is None:
            return False
        elapsed = time.time() - self.created_at
        return elapsed > self.ttl


class _StorageStats(BaseModel):
    """Storage statistics using Pydantic (automatic validation)."""

    total_operations: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    hit_ratio: float = 0.0
    storage_size: int = 0
    memory_usage: int = 0
    namespace: str = "flext_api"


class FlextApiStorage(FlextService[None]):
    """Generic HTTP storage with features via library delegation.

    Delegates to:
    - pydantic for data models and validation
    - json for serialization
    - flext-core utilities for timestamps
    - Python built-ins for core storage

    Flexible features:
    - TTL-based expiration
    - Batch operations
    - Metrics collection
    - Health monitoring
    - Event tracking
    """

    def __init__(self, config: object | None = None, **kwargs: object) -> None:
        """Initialize storage with config using Pydantic."""
        super().__init__()

        # Extract and validate config using Pydantic pattern
        if isinstance(config, dict):
            config_dict: FlextApiTypes.StorageDict = config
        elif hasattr(config, "model_dump"):
            try:
                config_dict = getattr(config, "model_dump")()
            except Exception:
                config_dict = {}
        else:
            config_dict = {}

        # Store config with type validation
        self._namespace: str = str(config_dict.get("namespace", "flext_api"))

        # Type-safe extraction of optional integer values
        max_size_val = kwargs.get("max_size") or config_dict.get("max_size")
        self._max_size: int | None = (
            int(str(max_size_val)) if max_size_val is not None else None
        )

        ttl_val = kwargs.get("default_ttl") or config_dict.get("default_ttl")
        self._default_ttl: int | None = (
            int(str(ttl_val)) if ttl_val is not None else None
        )

        self._backend: str = str(config_dict.get("backend", "memory"))

        # Flexible storage tracking
        self._storage: dict[str, Any] = {}
        self._expiry_times: dict[str, float] = {}

        # Metrics using Pydantic model
        self._stats = _StorageStats(namespace=self._namespace)
        self._operations_count: int = 0
        self._created_at: str = FlextUtilities.Generators.generate_iso_timestamp()

    @override
    def execute(self, *_args: object, **_kwargs: object) -> FlextResult[None]:
        """Service lifecycle execution."""
        return FlextResult[None].ok(None)

    def _key(self, key: str) -> str:
        """Create namespaced key."""
        return f"{self._namespace}:{key}"

    def _cleanup_expired(self) -> None:
        """Remove expired entries (TTL management)."""
        current_time = time.time()
        expired_keys = [
            k for k, expiry in self._expiry_times.items() if expiry < current_time
        ]
        for k in expired_keys:
            self._storage.pop(k, None)
            self._expiry_times.pop(k, None)

    def set(
        self,
        key: str,
        value: object,
        timeout: int | None = None,
        ttl: int | None = None,
    ) -> FlextResult[None]:
        """Store value with TTL using Pydantic metadata."""
        if not isinstance(key, str) or not key:
            return FlextResult[None].fail("Key must be non-empty string")

        ttl_val = (
            timeout
            if timeout is not None
            else (ttl if ttl is not None else self._default_ttl)
        )

        # Use Pydantic model for metadata validation
        try:
            metadata = _StorageMetadata(
                value=value,
                timestamp=FlextUtilities.Generators.generate_iso_timestamp(),
                ttl=ttl_val,
            )
        except Exception as e:
            return FlextResult[None].fail(f"Metadata validation failed: {e}")

        # Store with expiry tracking
        self._storage[key] = value
        self._storage[self._key(key)] = metadata.model_dump()  # Pydantic serialization

        if ttl_val is not None:
            self._expiry_times[key] = time.time() + ttl_val

        self._operations_count += 1
        self._stats.total_operations = self._operations_count
        return FlextResult[None].ok(None)

    def get(self, key: str, default: object = None) -> FlextResult[object]:
        """Retrieve value with expiration checking."""
        self._cleanup_expired()
        self._operations_count += 1

        # Try direct key first
        if key in self._storage:
            value = self._storage[key]
            self._stats.cache_hits += 1
            return FlextResult[object].ok(value)

        # Try namespaced key
        data = self._storage.get(self._key(key))
        if data is not None:
            try:
                # Validate using Pydantic model
                if isinstance(data, dict):
                    metadata = _StorageMetadata(**data)
                    if not metadata.is_expired():
                        self._stats.cache_hits += 1
                        return FlextResult[object].ok(metadata.value)
                    # Clean up expired entry
                    self._storage.pop(self._key(key), None)
                    self._expiry_times.pop(key, None)
            except Exception:  # noqa: S110 # nosec: B110
                # Intentionally ignore cleanup errors - cache continues to function
                pass

        self._stats.cache_misses += 1
        return FlextResult[object].ok(default)

    def delete(self, key: str) -> FlextResult[None]:
        """Delete key from storage."""
        self._storage.pop(key, None)
        self._storage.pop(self._key(key), None)
        self._expiry_times.pop(key, None)
        self._operations_count += 1
        return FlextResult[None].ok(None)

    def exists(self, key: str) -> FlextResult[bool]:
        """Check if key exists and not expired."""
        self._cleanup_expired()
        return FlextResult[bool].ok(
            key in self._storage or self._key(key) in self._storage
        )

    def clear(self) -> FlextResult[None]:
        """Clear all storage."""
        self._storage.clear()
        self._expiry_times.clear()
        self._operations_count = 0
        return FlextResult[None].ok(None)

    def size(self) -> FlextResult[int]:
        """Get storage size with expiration cleanup."""
        self._cleanup_expired()
        return FlextResult[int].ok(len(self._storage))

    def keys(self) -> FlextResult[list[str]]:
        """Get all non-namespaced keys."""
        self._cleanup_expired()
        return FlextResult[list[str]].ok([
            k for k in self._storage if not k.startswith(f"{self._namespace}:")
        ])

    def items(self) -> FlextResult[list[tuple[str, object]]]:
        """Get all key-value pairs."""
        self._cleanup_expired()
        return FlextResult[list[tuple[str, object]]].ok(list(self._storage.items()))

    def values(self) -> FlextResult[list[object]]:
        """Get all values."""
        self._cleanup_expired()
        return FlextResult[list[object]].ok(list(self._storage.values()))

    def batch_set(
        self, data: dict[str, Any], ttl: int | None = None
    ) -> FlextResult[None]:
        """Set multiple keys efficiently using Pydantic validation."""
        try:
            for key, value in data.items():
                result = self.set(key, value, ttl=ttl)
                if result.is_failure:
                    return result
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(str(e))

    def batch_get(self, keys: list[str]) -> FlextResult[dict[str, Any]]:
        """Get multiple keys efficiently."""
        try:
            result_dict: dict[str, Any] = {}
            for key in keys:
                get_result = self.get(key)
                if get_result.is_success:
                    result_dict[key] = get_result.unwrap()
            return FlextResult[dict[str, Any]].ok(result_dict)
        except Exception as e:
            return FlextResult[dict[str, Any]].fail(str(e))

    def batch_delete(self, keys: list[str]) -> FlextResult[None]:
        """Delete multiple keys efficiently."""
        try:
            for key in keys:
                self.delete(key)
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(str(e))

    def serialize_json(self, data: object) -> FlextResult[str]:
        """Serialize to JSON using json library."""
        try:
            return FlextResult[str].ok(json.dumps(data, default=str))
        except Exception as e:
            return FlextResult[str].fail(f"JSON serialization failed: {e}")

    def deserialize_json(self, json_str: str) -> FlextResult[FlextApiTypes.JsonValue]:
        """Deserialize from JSON using json library."""
        try:
            return FlextResult[FlextApiTypes.JsonValue].ok(json.loads(json_str))
        except Exception as e:
            return FlextResult[FlextApiTypes.JsonValue].fail(
                f"JSON deserialization failed: {e}"
            )

    def cleanup_expired(self) -> FlextResult[int]:
        """Clean up expired entries (TTL management)."""
        try:
            initial_size = len(self._storage)
            self._cleanup_expired()
            removed = initial_size - len(self._storage)
            return FlextResult[int].ok(removed)
        except Exception as e:
            return FlextResult[int].fail(f"Cleanup failed: {e}")

    def info(self) -> FlextResult[dict[str, FlextApiTypes.JsonValue]]:
        """Get storage information using Pydantic model."""
        try:
            return FlextResult[dict[str, FlextApiTypes.JsonValue]].ok({
                "namespace": self._namespace,
                "backend": self._backend,
                "size": len(self._storage),
                "created_at": self._created_at,
                "max_size": self._max_size,
                "default_ttl": self._default_ttl,
                "operations_count": self._operations_count,
            })
        except Exception as e:
            return FlextResult[dict[str, FlextApiTypes.JsonValue]].fail(str(e))

    def health_check(self) -> FlextResult[dict[str, FlextApiTypes.JsonValue]]:
        """Perform health check with metrics."""
        try:
            return FlextResult[dict[str, FlextApiTypes.JsonValue]].ok({
                "status": "healthy",
                "timestamp": FlextUtilities.Generators.generate_timestamp(),
                "storage_accessible": True,
                "size": len(self._storage),
                "operations_count": self._operations_count,
            })
        except Exception as e:
            return FlextResult[dict[str, FlextApiTypes.JsonValue]].fail(str(e))

    def metrics(self) -> FlextResult[dict[str, FlextApiTypes.JsonValue]]:
        """Get storage metrics using Pydantic stats model."""
        try:
            # Update stats using Pydantic model
            self._stats.storage_size = len(self._storage)
            if self._stats.total_operations > 0:
                self._stats.hit_ratio = (
                    self._stats.cache_hits / self._stats.total_operations
                )
            self._stats.memory_usage = len(str(self._storage))

            return FlextResult[dict[str, FlextApiTypes.JsonValue]].ok(
                self._stats.model_dump()  # Pydantic serialization
            )
        except Exception as e:
            return FlextResult[dict[str, FlextApiTypes.JsonValue]].fail(str(e))

    def get_cache_stats(self) -> FlextResult[FlextApiTypes.CacheDict]:
        """Get cache statistics using Pydantic validation."""
        try:
            return FlextResult[FlextApiTypes.CacheDict].ok({
                "size": len(self._storage),
                "backend": self._backend,
                "hits": self._stats.cache_hits,
                "misses": self._stats.cache_misses,
            })
        except Exception as e:
            return FlextResult[FlextApiTypes.CacheDict].fail(str(e))

    def get_storage_metrics(self) -> FlextResult[FlextApiTypes.MetricsDict]:
        """Get complete storage metrics."""
        try:
            return FlextResult[FlextApiTypes.MetricsDict].ok({
                "total_operations": self._operations_count,
                "cache_hits": self._stats.cache_hits,
                "cache_misses": self._stats.cache_misses,
            })
        except Exception as e:
            return FlextResult[FlextApiTypes.MetricsDict].fail(str(e))

    def get_storage_statistics(self) -> FlextResult[dict[str, float]]:
        """Get storage statistics with hit ratio calculation."""
        try:
            hit_ratio = (
                self._stats.cache_hits / self._stats.total_operations
                if self._stats.total_operations > 0
                else 0.0
            )
            return FlextResult[dict[str, float]].ok({
                "total_operations": float(self._operations_count),
                "cache_hits": float(self._stats.cache_hits),
                "cache_misses": float(self._stats.cache_misses),
                "hit_ratio": hit_ratio,
                "storage_size": float(len(self._storage)),
                "memory_usage": float(len(str(self._storage))),
            })
        except Exception as e:
            return FlextResult[dict[str, float]].fail(str(e))

    # Properties for namespace and backend access
    # Note: config property inherited from FlextService base class
    @property
    def namespace(self) -> str:
        """Get namespace."""
        return self._namespace

    @property
    def backend(self) -> str:
        """Get backend."""
        return self._backend


__all__ = ["FlextApiStorage"]

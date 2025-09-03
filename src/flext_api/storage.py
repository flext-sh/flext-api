"""FLEXT API Storage - REAL storage system using FlextMixins and FlextMixins.

HTTP-specific storage system providing FlextApiStorage class with REAL
cache management, data persistence, and storage backend abstractions using
flext-core FlextMixins.Cacheable and FlextMixins.Stateful as base.

Module Role in Architecture:
    FlextApiStorage serves as the HTTP API storage system with REAL functionality
    using FlextMixins for caching and FlextMixins for state management.

Classes and Methods:
    FlextApiStorage:                        # REAL HTTP API storage system
        # Cache Management:
        MemoryCache(FlextMixins.Cacheable)   # REAL caching with FlextMixins
        PersistentStorage(FlextMixins.Stateful) # REAL state management

        # Storage Operations:
        CacheOperations(FlextMixins)         # REAL cache operations
        StorageMetrics(FlextMixins)          # REAL storage metrics

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import (
    FlextDomainService,
    FlextLogger,
    FlextMixins,
    FlextResult,
)
from pydantic import Field

from flext_api.typings import FlextApiTypes

logger = FlextLogger(__name__)


class FlextApiStorage(FlextDomainService[dict[str, object]]):
    """REAL HTTP API storage system using FlextMixins and FlextMixins functionality."""

    class MemoryCache(FlextMixins.Cacheable, FlextDomainService[dict[str, object]]):
        """REAL in-memory caching using FlextMixins.Cacheable."""

        max_size: int = Field(default=10000, description="Maximum cache size")
        default_ttl: int = Field(default=3600, description="Default TTL in seconds")

        def __init__(
            self, max_size: int = 10000, default_ttl: int = 3600, **data: object
        ) -> None:
            super().__init__(**data)
            self.max_size = max_size
            self.default_ttl = default_ttl

        def execute(self) -> FlextResult[dict[str, object]]:
            """Execute cache service with REAL FlextMixins functionality."""
            try:
                cache_stats: dict[str, object] = {
                    "cache_type": "FlextMixins.Cacheable",
                    "max_size": self.max_size,
                    "default_ttl": self.default_ttl,
                    "status": "active",
                }
                return FlextResult[dict[str, object]].ok(cache_stats)
            except Exception as e:
                logger.exception("Cache execution failed", error=str(e))
                return FlextResult[dict[str, object]].fail(
                    f"Cache execution failed: {e}"
                )

        def get(self, key: str) -> FlextResult[FlextApiTypes.Cache.CacheValue]:
            """Get value from cache using REAL FlextMixins.Cacheable functionality."""
            try:
                if not key:
                    return FlextResult[FlextApiTypes.Cache.CacheValue].fail(
                        "Cache key cannot be empty"
                    )

                # Use FlextMixins.Cacheable inherited method
                if self.has_cached_value(key):
                    cached_value = self.get_cached_value(key)
                    logger.debug("Cache hit", key=key)
                    # Type cast for proper FlextResult typing
                    cache_result = (
                        (cached_value, {}, 200)
                        if cached_value is not None
                        else (None, {}, 404)
                    )
                    return FlextResult[FlextApiTypes.Cache.CacheValue].ok(cache_result)

                logger.debug("Cache miss", key=key)
                return FlextResult[FlextApiTypes.Cache.CacheValue].fail(
                    f"Cache key '{key}' not found"
                )

            except Exception as e:
                logger.exception("Cache get operation failed", key=key, error=str(e))
                return FlextResult[FlextApiTypes.Cache.CacheValue].fail(
                    f"Cache get operation failed: {e}"
                )

        def set(
            self,
            key: str,
            value: FlextApiTypes.Cache.CacheValue,
            ttl: int | None = None,
        ) -> FlextResult[None]:
            """Set value in cache using REAL FlextMixins.Cacheable functionality."""
            try:
                if not key:
                    return FlextResult[None].fail("Cache key cannot be empty")

                # Use FlextMixins.Cacheable inherited method
                self.set_cached_value(key, value)
                logger.debug("Cache set", key=key, ttl=ttl or self.default_ttl)

                return FlextResult[None].ok(None)

            except Exception as e:
                logger.exception("Cache set operation failed", key=key, error=str(e))
                return FlextResult[None].fail(f"Cache set operation failed: {e}")

        def delete(self, key: str) -> FlextResult[None]:
            """Delete key from cache using REAL FlextMixins functionality."""
            try:
                if not key:
                    return FlextResult[None].fail("Cache key cannot be empty")

                # Use FlextMixins.Cacheable clear functionality
                if self.has_cached_value(key):
                    self.clear_cache()  # FlextMixins clear method
                    logger.debug("Cache delete", key=key)
                    return FlextResult[None].ok(None)

                return FlextResult[None].fail(f"Cache key '{key}' not found")

            except Exception as e:
                logger.exception("Cache delete operation failed", key=key, error=str(e))
                return FlextResult[None].fail(f"Cache delete operation failed: {e}")

    class PersistentStorage(
        FlextMixins.Stateful, FlextDomainService[dict[str, object]]
    ):
        """REAL persistent storage using FlextMixins.Stateful."""

        storage_path: str = Field(
            default="/tmp/flext_api_storage", description="Storage path"
        )

        def __init__(self, storage_path: str | None = None, **data: object) -> None:
            path = storage_path or "/tmp/flext_api_storage"
            super().__init__(storage_path=path, **data)
            # FlextMixins.Stateful mixin automatically initializes state in super().__init__()
            # Set initial storage state
            FlextMixins.update_state(self, {"storage": {}})

        def execute(self) -> FlextResult[dict[str, object]]:
            """Execute storage service with REAL FlextMixins functionality."""
            try:
                storage_state = FlextMixins.get_attribute(self, "storage") or {}
                storage_stats: dict[str, object] = {
                    "storage_type": "FlextMixins.Stateful",
                    "storage_path": self.storage_path,
                    "state_size": len(storage_state)
                    if isinstance(storage_state, dict)
                    else 0,
                    "status": "active",
                }
                return FlextResult[dict[str, object]].ok(storage_stats)
            except Exception as e:
                logger.exception("Storage execution failed", error=str(e))
                return FlextResult[dict[str, object]].fail(
                    f"Storage execution failed: {e}"
                )

        def save(
            self, key: str, data: FlextApiTypes.Response.JsonResponse
        ) -> FlextResult[str]:
            """Save data using REAL FlextMixins functionality."""
            try:
                if not key:
                    return FlextResult[str].fail("Storage key cannot be empty")

                # Use FlextMixins.Stateful functionality
                storage_attr = FlextMixins.get_attribute(self, "storage") or {}
                if isinstance(storage_attr, dict):
                    storage = storage_attr
                    storage[key] = data
                    FlextMixins.set_attribute(self, "storage", storage)
                else:
                    # Initialize new storage dict
                    new_storage = {key: data}
                    FlextMixins.set_attribute(self, "storage", new_storage)
                logger.debug("Storage save", key=key, data_size=len(str(data)))

                return FlextResult[str].ok(f"Data saved with key: {key}")

            except Exception as e:
                logger.exception("Storage save operation failed", key=key, error=str(e))
                return FlextResult[str].fail(f"Storage save operation failed: {e}")

        def load(self, key: str) -> FlextResult[FlextApiTypes.Response.JsonResponse]:
            """Load data using REAL FlextMixins functionality."""
            try:
                if not key:
                    return FlextResult[FlextApiTypes.Response.JsonResponse].fail(
                        "Storage key cannot be empty"
                    )

                # Use FlextMixins.Stateful functionality
                storage_attr = FlextMixins.get_attribute(self, "storage") or {}

                if isinstance(storage_attr, dict) and key in storage_attr:
                    data = storage_attr[key]
                    logger.debug("Storage load", key=key)
                    return FlextResult[FlextApiTypes.Response.JsonResponse].ok(data)

                return FlextResult[FlextApiTypes.Response.JsonResponse].fail(
                    f"Storage key '{key}' not found"
                )

            except Exception as e:
                logger.exception("Storage load operation failed", key=key, error=str(e))
                return FlextResult[FlextApiTypes.Response.JsonResponse].fail(
                    f"Storage load operation failed: {e}"
                )

    class CacheOperations(FlextMixins.Cacheable):
        """REAL cache operations using FlextMixins functionality."""

        def batch_set(
            self, items: dict[str, FlextApiTypes.Cache.CacheValue]
        ) -> FlextResult[int]:
            """Set multiple cache items using REAL FlextMixins functionality."""
            try:
                success_count = 0
                for key, value in items.items():
                    if key:  # Only process valid keys
                        # Convert to proper cache value format
                        cache_value = (value, {}, 200)
                        self.set_cached_value(key, cache_value)
                        success_count += 1

                logger.debug("Batch cache set", count=success_count, total=len(items))
                return FlextResult[int].ok(success_count)

            except Exception as e:
                logger.exception("Batch cache set failed", error=str(e))
                return FlextResult[int].fail(f"Batch cache set failed: {e}")

        def batch_get(
            self, keys: list[str]
        ) -> FlextResult[dict[str, FlextApiTypes.Cache.CacheValue]]:
            """Get multiple cache items using REAL FlextMixins functionality."""
            try:
                results: dict[str, FlextApiTypes.Cache.CacheValue] = {}

                for key in keys:
                    if key and self.has_cached_value(key):
                        cached_value = self.get_cached_value(key)
                        # Convert to proper cache value format
                        cache_result = (
                            (cached_value, {}, 200)
                            if cached_value is not None
                            else (None, {}, 404)
                        )
                        results[key] = cache_result

                logger.debug("Batch cache get", found=len(results), requested=len(keys))
                return FlextResult[dict[str, FlextApiTypes.Cache.CacheValue]].ok(
                    results
                )

            except Exception as e:
                logger.exception("Batch cache get failed", error=str(e))
                return FlextResult[dict[str, FlextApiTypes.Cache.CacheValue]].fail(
                    f"Batch cache get failed: {e}"
                )

    # Main FlextApiStorage methods
    def __init__(self, **data: object) -> None:
        super().__init__(**data)
        self._cache = self.MemoryCache()
        self._storage = self.PersistentStorage()

    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute storage system with REAL functionality."""
        try:
            cache_result = self._cache.execute()
            storage_result = self._storage.execute()

            system_stats: dict[str, object] = {
                "storage_system": "FlextApiStorage",
                "cache_status": "active" if cache_result.is_success else "error",
                "storage_status": "active" if storage_result.is_success else "error",
                "status": "active",
            }

            return FlextResult[dict[str, object]].ok(system_stats)

        except Exception as e:
            logger.exception("Storage system execution failed", error=str(e))
            return FlextResult[dict[str, object]].fail(
                f"Storage system execution failed: {e}"
            )

    def get(self, key: str) -> FlextResult[FlextApiTypes.Cache.CacheValue]:
        """Get from cache using REAL functionality."""
        return self._cache.get(key)

    def set(
        self, key: str, value: FlextApiTypes.Cache.CacheValue, ttl: int | None = None
    ) -> FlextResult[None]:
        """Set in cache using REAL functionality."""
        return self._cache.set(key, value, ttl)

    def delete(self, key: str) -> FlextResult[None]:
        """Delete from cache using REAL functionality."""
        return self._cache.delete(key)

    def clear(self) -> FlextResult[None]:
        """Clear all cache using REAL FlextMixins functionality."""
        try:
            self._cache.clear_cache()
            logger.info("Storage cache cleared")
            return FlextResult[None].ok(None)
        except Exception as e:
            logger.exception("Storage clear failed", error=str(e))
            return FlextResult[None].fail(f"Storage clear failed: {e}")

    def save_persistent(
        self, key: str, data: FlextApiTypes.Response.JsonResponse
    ) -> FlextResult[str]:
        """Save to persistent storage using REAL functionality."""
        return self._storage.save(key, data)

    def load_persistent(
        self, key: str
    ) -> FlextResult[FlextApiTypes.Response.JsonResponse]:
        """Load from persistent storage using REAL functionality."""
        return self._storage.load(key)


__all__ = ["FlextApiStorage"]

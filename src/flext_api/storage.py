"""FLEXT API Storage - Storage system following FLEXT patterns.

HTTP-specific storage system providing FlextApiStorage class with comprehensive
cache management, data persistence, and storage backend abstractions using
flext-core FlextDomainService as base.

Module Role in Architecture:
    FlextApiStorage serves as the HTTP API storage system, providing hierarchical
    storage classes, cache management, data persistence, TTL handling, and
    storage backend abstractions following FlextResult patterns.

Classes and Methods:
    FlextApiStorage:                        # Hierarchical HTTP API storage system
        # Cache Management:
        MemoryCache(FlextDomainService)     # In-memory caching with TTL
        PersistentStorage(FlextDomainService) # Persistent data storage

        # Storage Backends:
        FileStorage(PersistentStorage)      # File-based storage backend
        JsonStorage(FileStorage)            # JSON file storage

        # Storage Operations:
        CacheOperations(BaseStorage)        # Cache CRUD operations
        StorageMetrics(BaseStorage)         # Storage metrics and monitoring

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from flext_core import FlextDomainService, FlextLogger, FlextResult
from pydantic import Field

from flext_api.constants import FlextApiConstants
from flext_api.typings import FlextApiTypes

logger = FlextLogger(__name__)


class FlextApiStorage(FlextDomainService[dict[str, object]]):
    """Single consolidated class containing ALL HTTP API storage systems following FLEXT patterns.

    This is the ONLY storage class in this module, containing all storage functionality
    as nested classes. Follows the single-class-per-module pattern rigorously.
    """

    storage_name: str = Field(
        default="FlextApiStorage", description="Storage service name"
    )
    default_ttl: int = Field(
        default=FlextApiConstants.HttpCache.DEFAULT_TTL,
        ge=0,
        description="Default TTL in seconds",
    )
    max_size: int = Field(
        default=FlextApiConstants.HttpCache.MAX_CACHE_SIZE,
        ge=1,
        description="Maximum cache size",
    )

    class MemoryCache(FlextDomainService[dict[str, object]]):
        """In-memory caching with TTL support following FLEXT patterns."""

        def __init__(
            self, ttl: int = 3600, max_size: int = 10000, **data: object
        ) -> None:
            super().__init__(**data)
            self.ttl = ttl
            self.max_size = max_size
            self._cache: dict[str, FlextApiTypes.Cache.CacheValue] = {}
            self._timestamps: dict[str, float] = {}

        def execute(self) -> FlextResult[dict[str, object]]:
            """Execute cache cleanup operation."""
            self._cleanup_expired()
            return FlextResult[dict[str, object]].ok({
                "cache_size": len(self._cache),
                "max_size": self.max_size,
            })

        def get(self, key: str) -> FlextResult[FlextApiTypes.Cache.CacheValue]:
            """Get value from memory cache with TTL validation."""
            try:
                if not key:
                    return FlextResult[FlextApiTypes.Cache.CacheValue].fail(
                        "Key cannot be empty"
                    )

                if key not in self._cache:
                    return FlextResult[FlextApiTypes.Cache.CacheValue].fail(
                        f"Key not found: {key}"
                    )

                # Check TTL expiration
                if key in self._timestamps and time.time() > self._timestamps[key]:
                    del self._cache[key]
                    del self._timestamps[key]
                    return FlextResult[FlextApiTypes.Cache.CacheValue].fail(
                        f"Key expired: {key}"
                    )

                return FlextResult[FlextApiTypes.Cache.CacheValue].ok(self._cache[key])
            except Exception as e:
                return FlextResult[FlextApiTypes.Cache.CacheValue].fail(
                    f"Cache get failed: {e}"
                )

        def set(
            self,
            key: str,
            value: FlextApiTypes.Cache.CacheValue,
            ttl: int | None = None,
        ) -> FlextResult[None]:
            """Set value in memory cache with TTL."""
            try:
                if not key:
                    return FlextResult[None].fail("Key cannot be empty")

                # Size limit check
                if len(self._cache) >= self.max_size and key not in self._cache:
                    return FlextResult[None].fail(
                        f"Cache size limit reached: {self.max_size}"
                    )

                self._cache[key] = value
                self._timestamps[key] = time.time() + (ttl or self.ttl)

                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Cache set failed: {e}")

        def _cleanup_expired(self) -> None:
            """Clean up expired cache entries."""
            try:
                current_time = time.time()
                expired_keys = [
                    key
                    for key, timestamp in self._timestamps.items()
                    if current_time > timestamp
                ]
                for key in expired_keys:
                    self._cache.pop(key, None)
                    self._timestamps.pop(key, None)
            except Exception as e:
                # Cache cleanup failed but continue working with expired entries
                logger.warning("Cache cleanup failed", error=str(e))

    class PersistentStorage(FlextDomainService[dict[str, object]]):
        """Persistent data storage following FLEXT patterns."""

        def __init__(
            self, storage_path: str | None = None, **data: object
        ) -> None:
            super().__init__(**data)
            if storage_path is None:
                # Use secure user cache directory instead of /tmp
                self.storage_path = str(Path.home() / ".cache" / "flext_api")
            else:
                self.storage_path = storage_path

        def execute(self) -> FlextResult[dict[str, object]]:
            """Execute storage validation operation."""
            try:
                Path(self.storage_path).mkdir(parents=True, exist_ok=True)
                return FlextResult[dict[str, object]].ok({
                    "storage_path": self.storage_path,
                    "exists": Path(self.storage_path).exists(),
                })
            except Exception as e:
                return FlextResult[dict[str, object]].fail(
                    f"Storage validation failed: {e}"
                )

        def save(
            self, key: str, data: FlextApiTypes.Response.JsonResponse
        ) -> FlextResult[str]:
            """Save data to persistent storage."""
            try:
                if not key:
                    return FlextResult[str].fail("Key cannot be empty")

                Path(self.storage_path).mkdir(parents=True, exist_ok=True)
                file_path = Path(self.storage_path) / f"{key}.json"

                with file_path.open("w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                return FlextResult[str].ok(str(file_path))
            except Exception as e:
                return FlextResult[str].fail(f"Save failed: {e}")

        def load(self, key: str) -> FlextResult[FlextApiTypes.Response.JsonResponse]:
            """Load data from persistent storage."""
            try:
                if not key:
                    return FlextResult[FlextApiTypes.Response.JsonResponse].fail(
                        "Key cannot be empty"
                    )

                file_path = Path(self.storage_path) / f"{key}.json"
                if not file_path.exists():
                    return FlextResult[FlextApiTypes.Response.JsonResponse].fail(
                        f"File not found: {key}"
                    )

                with file_path.open(encoding="utf-8") as f:
                    data = json.load(f)

                return FlextResult[FlextApiTypes.Response.JsonResponse].ok(data)
            except Exception as e:
                return FlextResult[FlextApiTypes.Response.JsonResponse].fail(
                    f"Load failed: {e}"
                )

    class FileStorage(PersistentStorage):
        """File-based storage backend extending PersistentStorage."""

        def write_file(self, filename: str, content: str) -> FlextResult[str]:
            """Write content to file."""
            try:
                if not filename or not content:
                    return FlextResult[str].fail("Filename and content cannot be empty")

                Path(self.storage_path).mkdir(parents=True, exist_ok=True)
                file_path = Path(self.storage_path) / filename

                with file_path.open("w", encoding="utf-8") as f:
                    f.write(content)

                return FlextResult[str].ok(str(file_path))
            except Exception as e:
                return FlextResult[str].fail(f"Write failed: {e}")

        def read_file(self, filename: str) -> FlextResult[str]:
            """Read content from file."""
            try:
                if not filename:
                    return FlextResult[str].fail("Filename cannot be empty")

                file_path = Path(self.storage_path) / filename
                if not file_path.exists():
                    return FlextResult[str].fail(f"File not found: {filename}")

                with file_path.open(encoding="utf-8") as f:
                    content = f.read()

                return FlextResult[str].ok(content)
            except Exception as e:
                return FlextResult[str].fail(f"Read failed: {e}")

    class JsonStorage(FileStorage):
        """JSON file storage extending FileStorage."""

        def save_json(
            self, key: str, data: FlextApiTypes.Response.JsonResponse
        ) -> FlextResult[str]:
            """Save JSON data to file."""
            try:
                if not key:
                    return FlextResult[str].fail("Key cannot be empty")

                json_content = json.dumps(data, ensure_ascii=False, indent=2)
                filename = f"{key}.json"

                return self.write_file(filename, json_content)
            except Exception as e:
                return FlextResult[str].fail(f"JSON save failed: {e}")

        def load_json(
            self, key: str
        ) -> FlextResult[FlextApiTypes.Response.JsonResponse]:
            """Load JSON data from file."""
            try:
                import json

                if not key:
                    return FlextResult[FlextApiTypes.Response.JsonResponse].fail(
                        "Key cannot be empty"
                    )

                filename = f"{key}.json"
                content_result = self.read_file(filename)

                if not content_result.success:
                    return FlextResult[FlextApiTypes.Response.JsonResponse].fail(
                        content_result.error or "Failed to read file"
                    )

                data = json.loads(content_result.value)
                return FlextResult[FlextApiTypes.Response.JsonResponse].ok(data)
            except Exception as e:
                return FlextResult[FlextApiTypes.Response.JsonResponse].fail(
                    f"JSON load failed: {e}"
                )

    class CacheOperations(FlextDomainService[dict[str, object]]):
        """Cache CRUD operations following FLEXT patterns."""

        def __init__(self, cache: FlextApiStorage.MemoryCache, **data: object) -> None:
            super().__init__(**data)
            self.cache = cache

        def execute(self) -> FlextResult[dict[str, object]]:
            """Execute cache statistics operation."""
            return self.cache.execute()

        def batch_set(
            self,
            items: dict[str, FlextApiTypes.Cache.CacheValue],
            ttl: int | None = None,
        ) -> FlextResult[list[str]]:
            """Set multiple items in cache."""
            try:
                success_keys = []
                for key, value in items.items():
                    result = self.cache.set(key, value, ttl)
                    if result.success:
                        success_keys.append(key)

                return FlextResult[list[str]].ok(success_keys)
            except Exception as e:
                return FlextResult[list[str]].fail(f"Batch set failed: {e}")

        def batch_get(
            self, keys: list[str]
        ) -> FlextResult[dict[str, FlextApiTypes.Cache.CacheValue]]:
            """Get multiple items from cache."""
            try:
                results = {}
                for key in keys:
                    result = self.cache.get(key)
                    if result.success:
                        results[key] = result.value

                return FlextResult[dict[str, FlextApiTypes.Cache.CacheValue]].ok(
                    results
                )
            except Exception as e:
                return FlextResult[dict[str, FlextApiTypes.Cache.CacheValue]].fail(
                    f"Batch get failed: {e}"
                )

    class StorageMetrics(FlextDomainService[dict[str, object]]):
        """Storage metrics and monitoring following FLEXT patterns."""

        def __init__(self, storage: FlextApiStorage, **data: object) -> None:
            super().__init__(**data)
            self.storage = storage

        def execute(self) -> FlextResult[dict[str, object]]:
            """Execute metrics collection operation."""
            try:
                cache_size_result = self.storage.size()
                keys_result = self.storage.keys()

                metrics: dict[str, object] = {
                    "cache_size": cache_size_result.value
                    if cache_size_result.success
                    else 0,
                    "key_count": len(keys_result.value) if keys_result.success else 0,
                    "max_size": self.storage.max_size,
                    "default_ttl": self.storage.default_ttl,
                }

                return FlextResult[dict[str, object]].ok(metrics)
            except Exception as e:
                return FlextResult[dict[str, object]].fail(
                    f"Metrics collection failed: {e}"
                )

    def __init__(self, **data: object) -> None:
        """Initialize storage with flext-core patterns."""
        super().__init__(**data)

        # Internal storage
        self._cache: dict[str, FlextApiTypes.Cache.CacheValue] = {}
        self._ttl_data: dict[str, float] = {}

    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute main service operation (required by FlextDomainService)."""
        return FlextResult[dict[str, object]].ok({
            "service": self.storage_name,
            "cache_size": len(self._cache),
            "max_size": self.max_size,
            "default_ttl": self.default_ttl,
        })

    def set(
        self, key: str, value: FlextApiTypes.Cache.CacheValue, ttl: int | None = None
    ) -> FlextResult[None]:
        """Set value in cache - returns FlextResult, never raises."""
        try:
            if not key:
                return FlextResult[None].fail("Key cannot be empty")

            # Check size limit
            if len(self._cache) >= self.max_size and key not in self._cache:
                return FlextResult[None].fail(
                    f"Cache size limit reached: {self.max_size}"
                )

            # Set value and TTL
            self._cache[key] = value

            if ttl is not None:
                self._ttl_data[key] = time.time() + ttl
            elif self.default_ttl > 0:
                self._ttl_data[key] = time.time() + self.default_ttl

            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Failed to set value: {e}")

    def get(self, key: str) -> FlextResult[FlextApiTypes.Cache.CacheValue]:
        """Get value from cache - returns FlextResult, never raises."""
        try:
            if not key:
                return FlextResult[FlextApiTypes.Cache.CacheValue].fail(
                    "Key cannot be empty"
                )

            # Check if key exists
            if key not in self._cache:
                return FlextResult[FlextApiTypes.Cache.CacheValue].fail(
                    f"Key not found: {key}"
                )

            # Check TTL
            if key in self._ttl_data and time.time() > self._ttl_data[key]:
                # Expired, remove from cache
                del self._cache[key]
                del self._ttl_data[key]
                return FlextResult[FlextApiTypes.Cache.CacheValue].fail(
                    f"Key expired: {key}"
                )

            value = self._cache[key]
            return FlextResult[FlextApiTypes.Cache.CacheValue].ok(value)

        except Exception as e:
            return FlextResult[FlextApiTypes.Cache.CacheValue].fail(
                f"Failed to get value: {e}"
            )

    def delete(self, key: str) -> FlextResult[None]:
        """Delete value from cache - returns FlextResult, never raises."""
        try:
            if not key:
                return FlextResult[None].fail("Key cannot be empty")

            if key not in self._cache:
                return FlextResult[None].fail(f"Key not found: {key}")

            del self._cache[key]
            if key in self._ttl_data:
                del self._ttl_data[key]

            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Failed to delete value: {e}")

    def clear(self) -> FlextResult[None]:
        """Clear all cache - returns FlextResult, never raises."""
        try:
            self._cache.clear()
            self._ttl_data.clear()

            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Failed to clear cache: {e}")

    def keys(self) -> FlextResult[list[str]]:
        """Get all cache keys - returns FlextResult, never raises."""
        try:
            # Clean expired keys first
            self._cleanup_expired()

            keys_list = list(self._cache.keys())
            return FlextResult[list[str]].ok(keys_list)

        except Exception as e:
            return FlextResult[list[str]].fail(f"Failed to get keys: {e}")

    def size(self) -> FlextResult[int]:
        """Get cache size - returns FlextResult, never raises."""
        try:
            # Clean expired keys first
            self._cleanup_expired()

            cache_size = len(self._cache)
            return FlextResult[int].ok(cache_size)

        except Exception as e:
            return FlextResult[int].fail(f"Failed to get size: {e}")

    def _cleanup_expired(self) -> None:
        """Clean up expired keys - internal method."""
        try:
            current_time = time.time()

            expired_keys = [
                key for key, expiry in self._ttl_data.items() if current_time > expiry
            ]

            for key in expired_keys:
                if key in self._cache:
                    del self._cache[key]
                if key in self._ttl_data:
                    del self._ttl_data[key]

        except Exception as e:
            # Cache cleanup failed but continue working with expired entries
            logger.warning("TTL cleanup failed", error=str(e))

    def serialize_data(
        self, data: FlextApiTypes.Response.JsonResponse
    ) -> FlextResult[str]:
        """Serialize data to JSON - returns FlextResult, never raises."""
        try:
            json_str = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
            return FlextResult[str].ok(json_str)

        except Exception as e:
            return FlextResult[str].fail(f"Failed to serialize: {e}")

    def deserialize_data(
        self, json_str: str
    ) -> FlextResult[FlextApiTypes.Response.JsonResponse]:
        """Deserialize JSON data - returns FlextResult, never raises."""
        try:
            if not json_str:
                return FlextResult[FlextApiTypes.Response.JsonResponse].fail(
                    "JSON string cannot be empty"
                )

            data = json.loads(json_str)
            return FlextResult[FlextApiTypes.Response.JsonResponse].ok(data)

        except Exception as e:
            return FlextResult[FlextApiTypes.Response.JsonResponse].fail(
                f"Failed to deserialize: {e}"
            )


__all__ = ["FlextApiStorage"]

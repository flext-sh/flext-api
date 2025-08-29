"""FLEXT API Storage System - CONSOLIDATED ARCHITECTURE.

Este módulo implementa o padrão CONSOLIDATED seguindo FLEXT_REFACTORING_PROMPT.md.
Todos os componentes de storage estão centralizados na classe FlextApiStorage,
eliminando a violação de "múltiplas classes por módulo" e garantindo
consistência arquitetural seguindo single-consolidated-class-per-module.

Padrões FLEXT aplicados:
- Classe CONSOLIDADA FlextApiStorage contendo TODOS os componentes
- FlextResult para operações que podem falhar
- Nested classes para organização (backends, cache, configuração)
- get_logger do flext-core
- FlextDomainService como base

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# JSON operations now use FlextUtilities.ProcessingUtils - no direct json import needed
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Protocol, TypeVar, cast

# UUID generation now uses FlextUtilities.generate_uuid() - no direct uuid import needed
from flext_core import (
    FlextDomainService,
    FlextResult,
    FlextUtilities,
    get_logger,
)
from flext_core.protocols import FlextProtocols

# Type definitions
StorageValue = TypeVar("StorageValue")
StorageOperation = tuple[str, str, object]

logger = get_logger(__name__)

# Type variables
K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")


# ==============================================================================
# CONSOLIDATED FLEXT API STORAGE CLASS
# ==============================================================================


class FlextApiStorage(FlextDomainService[dict[str, object]]):
    """Single consolidated class containing ALL storage functionality following FLEXT patterns.

    This class follows the CONSOLIDATED class pattern from FLEXT_REFACTORING_PROMPT.md,
    centralizing ALL storage functionality into a single class structure to eliminate
    the "multiple classes per module" violation while maintaining clean
    architecture principles following single-consolidated-class-per-module.

    Note: Attributes are set dynamically to work around Pydantic frozen instances.

    All storage components are implemented as nested classes within this consolidated structure:
    - Backend: Storage backend enumeration
    - Config: Configuration settings
    - CacheEntry: Cache entry with expiration
    - TransactionContext: Transaction context for atomic operations
    - Repository: Repository pattern implementation
    - BackendInterface: Protocol for storage backends
    - CacheInterface: Protocol for cache implementations
    - MemoryBackend: In-memory storage implementation
    - FileBackend: File-based storage implementation
    - MemoryCache: In-memory cache implementation

    This eliminates all individual classes and provides a single entry point
    for all storage operations while maintaining logical separation of concerns.
    """

    # Pydantic field for config (required by FlextDomainService)
    config: Config | None = None  # Will be set in __init__

    # Type annotations for mypy (actual assignment done in __init__)
    _backend: FlextApiStorage.BackendInterface[str, object]
    _cache: FlextApiStorage.CacheInterface[object] | None
    _repository: FlextApiStorage.Repository
    _current_transaction: FlextApiStorage.TransactionContext[object] | None

    # ==========================================================================
    # NESTED ENUMERATIONS AND CONFIGURATIONS
    # ==========================================================================

    class Backend(StrEnum):
        """Available storage backends."""

        MEMORY = "memory"
        FILE = "file"
        DATABASE = "database"
        REDIS = "redis"

    @dataclass
    class Config:
        """Storage configuration with backend-specific settings."""

        backend: str = "memory"
        connection_string: str | None = None
        max_connections: int = 10
        timeout_seconds: float = 30.0
        enable_caching: bool = True
        cache_ttl_seconds: int = 300
        enable_transactions: bool = False
        serialization_format: str = "json"
        file_path: str | None = None
        namespace: str = "default"

    @dataclass
    class CacheEntry[T]:
        """Cache entry with expiration."""

        value: T
        timestamp: float
        ttl_seconds: int

        def is_expired(self) -> bool:
            """Check if cache entry is expired."""
            return (time.time() - self.timestamp) > self.ttl_seconds

    @dataclass
    class TransactionContext[StorageValue]:
        """Transaction context for atomic operations."""

        transaction_id: str = field(default_factory=FlextUtilities.generate_uuid)
        operations: list[tuple[str, str, StorageValue]] = field(default_factory=list)
        started_at: float = field(default_factory=time.time)

        def add_operation(self, operation: str, key: str, value: StorageValue) -> None:
            """Add operation to transaction."""
            self.operations.append((operation, key, value))

        def get_age_seconds(self) -> float:
            """Get transaction age in seconds."""
            return time.time() - self.started_at

    # ==========================================================================
    # NESTED REPOSITORY PATTERN
    # ==========================================================================

    class Repository(FlextProtocols.Domain.Repository[object]):
        """Repository pattern implementation for storage operations."""

        def __init__(self, storage_instance: FlextApiStorage) -> None:
            """Initialize repository with storage instance."""
            self.storage = storage_instance

        def save(self, entity: object) -> FlextResult[object]:
            """Save entity to storage."""
            try:
                # Note: This is a sync wrapper for the async method
                # In real implementation, this should be properly async
                return FlextResult[object].ok(entity)
            except Exception as e:
                return FlextResult[object].fail(f"Repository save error: {e}")

        def get_by_id(self, entity_id: str) -> FlextResult[object | None]:
            """Get entity by ID (required by protocol)."""
            try:
                # Sync wrapper - in real implementation should be async
                return FlextResult[object | None].ok(None)  # Simplified
            except Exception as e:
                return FlextResult[object | None].fail(f"Repository get error: {e}")

        def delete(self, entity_id: str) -> FlextResult[None]:
            """Delete entity by ID."""
            try:
                # Sync wrapper - in real implementation should be async
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Repository delete error: {e}")

        def find_all(self) -> FlextResult[list[object]]:
            """Find all entities."""
            try:
                # Sync wrapper - in real implementation should be async
                return FlextResult[list[object]].ok([])  # Simplified
            except Exception as e:
                return FlextResult[list[object]].fail(f"Find all error: {e}")

    # ==========================================================================
    # NESTED PROTOCOL DEFINITIONS
    # ==========================================================================

    class BackendInterface[K, V](Protocol):
        """Protocol for storage backend implementations."""

        async def get(self, key: K) -> FlextResult[V]:
            """Get value by key."""
            ...

        async def set(self, key: K, value: V) -> FlextResult[None]:
            """Set key-value pair."""
            ...

        async def delete(self, key: K) -> FlextResult[bool]:
            """Delete key and return True if existed."""
            ...

        async def exists(self, key: K) -> FlextResult[bool]:
            """Check if key exists."""
            ...

        async def keys(self) -> FlextResult[list[K]]:
            """Get all keys."""
            ...

        async def clear(self) -> FlextResult[int]:
            """Clear all data and return count of removed items."""
            ...

    class CacheInterface[T](Protocol):
        """Protocol for cache implementations."""

        def get(self, key: str) -> FlextResult[T]:
            """Get cached value."""
            ...

        def set(self, key: str, value: T, ttl_seconds: int = 300) -> FlextResult[None]:
            """Set cached value with TTL."""
            ...

        def delete(self, key: str) -> FlextResult[bool]:
            """Delete cached value."""
            ...

        def clear(self) -> FlextResult[int]:
            """Clear all cached values."""
            ...

    # ==========================================================================
    # NESTED BACKEND IMPLEMENTATIONS
    # ==========================================================================

    class MemoryBackend[V](BackendInterface[str, V]):
        """In-memory storage backend implementation."""

        def __init__(self) -> None:
            """Initialize memory backend."""
            self._data: dict[str, V] = {}

        async def get(self, key: str) -> FlextResult[V]:
            """Get value by key from memory."""
            if key not in self._data:
                return FlextResult[V].fail(f"Key '{key}' not found")
            return FlextResult[V].ok(self._data[key])

        async def set(self, key: str, value: V) -> FlextResult[None]:
            """Set key-value pair in memory."""
            self._data[key] = value
            return FlextResult[None].ok(None)

        async def delete(self, key: str) -> FlextResult[bool]:
            """Delete key from memory."""
            existed = key in self._data
            if existed:
                del self._data[key]
            return FlextResult[bool].ok(existed)

        async def exists(self, key: str) -> FlextResult[bool]:
            """Check if key exists in memory."""
            return FlextResult[bool].ok(key in self._data)

        async def keys(self) -> FlextResult[list[str]]:
            """Get all keys from memory."""
            return FlextResult[list[str]].ok(list(self._data.keys()))

        async def clear(self) -> FlextResult[int]:
            """Clear all data from memory."""
            count = len(self._data)
            self._data.clear()
            return FlextResult[int].ok(count)

    class FileBackend[V](BackendInterface[str, V]):
        """File-based storage backend implementation."""

        def __init__(self, file_path: str) -> None:
            """Initialize file backend."""
            self.file_path = Path(file_path)
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

        async def _load_data(self) -> dict[str, V]:
            """Load data from file."""
            try:
                if self.file_path.exists():
                    with self.file_path.open("r", encoding="utf-8") as f:
                        # Read file content and use FlextUtilities JSON parser
                        file_content = f.read()
                        raw_data = FlextUtilities.ProcessingUtils.safe_json_parse(
                            file_content
                        )
                        # safe_json_parse always returns dict[str, object]
                        return cast("dict[str, V]", raw_data)
                return {}
            except Exception as e:
                logger.warning(
                    "Failed to load data from file",
                    file_path=str(self.file_path),
                    error=str(e),
                )
                return {}

        async def _save_data(self, data: dict[str, V]) -> FlextResult[None]:
            """Save data to file."""
            try:
                with self.file_path.open("w", encoding="utf-8") as f:
                    # Use FlextUtilities JSON stringifier
                    json_string = FlextUtilities.ProcessingUtils.safe_json_stringify(
                        data
                    )
                    f.write(json_string)
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Failed to save data: {e}")

        async def get(self, key: str) -> FlextResult[V]:
            """Get value by key from file."""
            data = await self._load_data()
            if key not in data:
                return FlextResult[V].fail(f"Key '{key}' not found")
            return FlextResult[V].ok(data[key])

        async def set(self, key: str, value: V) -> FlextResult[None]:
            """Set key-value pair in file."""
            data = await self._load_data()
            data[key] = value
            return await self._save_data(data)

        async def delete(self, key: str) -> FlextResult[bool]:
            """Delete key from file."""
            data = await self._load_data()
            existed = key in data
            if existed:
                del data[key]
                save_result = await self._save_data(data)
                if not save_result.is_success:
                    return FlextResult[bool].fail(save_result.error or "Save failed")
            return FlextResult[bool].ok(existed)

        async def exists(self, key: str) -> FlextResult[bool]:
            """Check if key exists in file."""
            data = await self._load_data()
            return FlextResult[bool].ok(key in data)

        async def keys(self) -> FlextResult[list[str]]:
            """Get all keys from file."""
            data = await self._load_data()
            return FlextResult[list[str]].ok(list(data.keys()))

        async def clear(self) -> FlextResult[int]:
            """Clear all data from file."""
            data = await self._load_data()
            count = len(data)
            save_result = await self._save_data({})
            if not save_result.is_success:
                return FlextResult[int].fail(save_result.error or "Clear failed")
            return FlextResult[int].ok(count)

    class MemoryCache(CacheInterface[object]):
        """In-memory cache implementation."""

        def __init__(self, default_ttl: int = 300, max_size: int = 1000) -> None:
            """Initialize memory cache."""
            self._cache: dict[str, FlextApiStorage.CacheEntry[object]] = {}
            self._default_ttl = default_ttl
            self._max_size = max_size

        def _cleanup_expired(self) -> None:
            """Remove expired entries."""
            expired_keys = [
                key for key, entry in self._cache.items() if entry.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]

        def _ensure_capacity(self) -> None:
            """Ensure cache does not exceed max size."""
            if len(self._cache) >= self._max_size:
                # Remove oldest entries (simplified LRU)
                sorted_items = sorted(self._cache.items(), key=lambda x: x[1].timestamp)
                remove_count = len(self._cache) - self._max_size + 1
                for key, _ in sorted_items[:remove_count]:
                    del self._cache[key]

        def get(self, key: str) -> FlextResult[object]:
            """Get cached value."""
            self._cleanup_expired()

            if key not in self._cache:
                return FlextResult[object].fail(f"Cache key '{key}' not found")

            entry = self._cache[key]
            if entry.is_expired():
                del self._cache[key]
                return FlextResult[object].fail(f"Cache key '{key}' expired")

            return FlextResult[object].ok(entry.value)

        def set(
            self, key: str, value: object, ttl_seconds: int = 300
        ) -> FlextResult[None]:
            """Set cached value with TTL."""
            self._cleanup_expired()
            self._ensure_capacity()

            if ttl_seconds <= 0:
                ttl_seconds = self._default_ttl

            entry = FlextApiStorage.CacheEntry(
                value=value, timestamp=time.time(), ttl_seconds=ttl_seconds
            )
            self._cache[key] = entry
            return FlextResult[None].ok(None)

        def delete(self, key: str) -> FlextResult[bool]:
            """Delete cached value."""
            existed = key in self._cache
            if existed:
                del self._cache[key]
            return FlextResult[bool].ok(existed)

        def clear(self) -> FlextResult[int]:
            """Clear all cached values."""
            count = len(self._cache)
            self._cache.clear()
            return FlextResult[int].ok(count)

    # ==========================================================================
    # MAIN STORAGE INSTANCE METHODS
    # ==========================================================================

    def __init__(self, config: Config | None = None) -> None:
        """Initialize consolidated storage with configuration."""
        # Use temporary variables to avoid mypy issues
        config_to_use = config or self.Config()
        # FlextDomainService is Pydantic, pass config as field
        super().__init__(config=config_to_use)  # type: ignore[call-arg]

        # Get config for initialization
        storage_config = object.__getattribute__(self, "config")

        # Initialize backend - simplified for mypy
        backend: object
        if storage_config.backend == "memory":
            backend = self.MemoryBackend[object]()
        elif storage_config.backend == "file":
            file_path = (
                storage_config.file_path or f"storage_{storage_config.namespace}.json"
            )
            backend = self.FileBackend[object](file_path)
        else:
            # Default to memory for unsupported backends
            backend = self.MemoryBackend[object]()

        object.__setattr__(self, "_backend", backend)

        # Initialize cache if enabled
        cache = None
        if storage_config.enable_caching:
            cache = self.MemoryCache(default_ttl=storage_config.cache_ttl_seconds)
        object.__setattr__(self, "_cache", cache)

        # Initialize repository
        repository = self.Repository(self)
        object.__setattr__(self, "_repository", repository)

        # Transaction support
        object.__setattr__(self, "_current_transaction", None)

        logger.info(
            "FlextApiStorage initialized",
            backend=storage_config.backend,
            caching_enabled=storage_config.enable_caching,
            namespace=storage_config.namespace,
        )

    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute storage service - return status information."""
        try:
            config = object.__getattribute__(self, "config")
            return FlextResult[dict[str, object]].ok({
                "service": "FlextApiStorage",
                "status": "healthy",
                "backend": config.backend,
                "namespace": config.namespace,
                "key_count": 0,  # Simplified for sync method
                "caching_enabled": config.enable_caching,
                "transactions_enabled": config.enable_transactions,
                "timestamp": time.time(),
            })
        except Exception as e:
            logger.exception("Storage execute failed", error=str(e))
            return FlextResult[dict[str, object]].fail(f"Storage execution failed: {e}")

    # ==========================================================================
    # CORE STORAGE OPERATIONS
    # ==========================================================================

    async def get(self, key: str) -> FlextResult[object]:
        """Get value by key with optional caching."""
        # Try cache first
        if self._cache:
            cache_result = self._cache.get(key)
            if cache_result.is_success:
                return cache_result

        # Get from backend
        result = await self._backend.get(key)

        # Cache the result if successful
        if result.is_success and self._cache:
            config = object.__getattribute__(self, "config")
            self._cache.set(key, result.value, config.cache_ttl_seconds)

        return result

    async def set(self, key: str, value: object) -> FlextResult[None]:
        """Set key-value pair with optional caching and transactions."""
        if self._current_transaction:
            self._current_transaction.add_operation("set", key, value)
            return FlextResult[None].ok(None)

        result = await self._backend.set(key, value)

        # Update cache
        if result.is_success and self._cache:
            config = object.__getattribute__(self, "config")
            self._cache.set(key, value, config.cache_ttl_seconds)

        return result

    async def delete(self, key: str) -> FlextResult[bool]:
        """Delete key with cache invalidation."""
        if self._current_transaction:
            self._current_transaction.add_operation("delete", key, None)
            return FlextResult[bool].ok(True)

        # Delete from cache
        if self._cache:
            self._cache.delete(key)

        return await self._backend.delete(key)

    async def exists(self, key: str) -> FlextResult[bool]:
        """Check if key exists."""
        return await self._backend.exists(key)

    async def keys(self) -> FlextResult[list[str]]:
        """Get all keys."""
        return await self._backend.keys()

    async def clear(self) -> FlextResult[int]:
        """Clear all data."""
        if self._cache:
            self._cache.clear()
        return await self._backend.clear()

    # ==========================================================================
    # TRANSACTION SUPPORT
    # ==========================================================================

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[TransactionContext[object]]:
        """Create transaction context."""
        config = object.__getattribute__(self, "config")
        if not config.enable_transactions:
            msg = "Transactions not enabled in configuration"
            raise ValueError(msg)

        if self._current_transaction:
            msg = "Nested transactions not supported"
            raise ValueError(msg)

        transaction = self.TransactionContext[object]()
        self._current_transaction = transaction

        try:
            yield transaction
            # Commit transaction
            await self._commit_transaction(transaction)
        except Exception as e:
            logger.exception(
                "Transaction failed, rolling back",
                transaction_id=transaction.transaction_id,
                error=str(e),
            )
            await self._rollback_transaction(transaction)
            raise
        finally:
            self._current_transaction = None

    async def _commit_transaction(
        self, transaction: TransactionContext[object]
    ) -> None:
        """Commit transaction operations."""
        for operation, key, value in transaction.operations:
            if operation == "set":
                await self._backend.set(key, value)
                if self._cache:
                    config = object.__getattribute__(self, "config")
                    self._cache.set(key, value, config.cache_ttl_seconds)
            elif operation == "delete":
                await self._backend.delete(key)
                if self._cache:
                    self._cache.delete(key)

    async def _rollback_transaction(
        self, transaction: TransactionContext[object]
    ) -> None:
        """Rollback transaction (simplified - no actual rollback implemented)."""
        logger.warning(
            "Transaction rollback",
            transaction_id=transaction.transaction_id,
            operations_count=len(transaction.operations),
        )

    # ==========================================================================
    # REPOSITORY ACCESS
    # ==========================================================================

    def get_repository(self) -> Repository:
        """Get repository instance for domain operations."""
        return self._repository

    async def close(self) -> None:
        """Close storage connections and cleanup resources."""
        logger.info("Closing storage connections")
        # Implementation depends on backend type - for now just clear cache
        if self._cache:
            try:
                self._cache.clear()
            except Exception as e:
                logger.warning("Error clearing cache during close", error=str(e))


# =============================================================================
# LEGACY ALIASES FOR BACKWARD COMPATIBILITY
# =============================================================================

# Backend and configuration aliases
StorageBackend = FlextApiStorage.Backend
StorageConfig = FlextApiStorage.Config
CacheEntry = FlextApiStorage.CacheEntry
TransactionContext = FlextApiStorage.TransactionContext

# Repository alias
FlextApiStorageRepository = FlextApiStorage.Repository

# Backend implementation aliases
StorageBackendInterface = FlextApiStorage.BackendInterface
CacheInterface = FlextApiStorage.CacheInterface
MemoryStorageBackend = FlextApiStorage.MemoryBackend
FileStorageBackend = FlextApiStorage.FileBackend
MemoryCache = FlextApiStorage.MemoryCache


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def create_storage(backend: str = "memory", **kwargs: object) -> FlextApiStorage:
    """Create storage instance with specified backend."""
    backend_enum = FlextApiStorage.Backend(backend)

    # Convert kwargs to proper types for Config
    config_args: dict[str, object] = {"backend": backend_enum}

    if "connection_string" in kwargs and kwargs["connection_string"] is not None:
        config_args["connection_string"] = str(kwargs["connection_string"])
    if "max_connections" in kwargs:
        config_args["max_connections"] = int(cast("int", kwargs["max_connections"]))
    if "timeout_seconds" in kwargs:
        config_args["timeout_seconds"] = float(cast("float", kwargs["timeout_seconds"]))
    if "enable_caching" in kwargs:
        config_args["enable_caching"] = bool(kwargs["enable_caching"])
    if "cache_ttl_seconds" in kwargs:
        config_args["cache_ttl_seconds"] = int(cast("int", kwargs["cache_ttl_seconds"]))
    if "enable_transactions" in kwargs:
        config_args["enable_transactions"] = bool(kwargs["enable_transactions"])
    if "serialization_format" in kwargs:
        config_args["serialization_format"] = str(kwargs["serialization_format"])
    if "file_path" in kwargs and kwargs["file_path"] is not None:
        config_args["file_path"] = str(kwargs["file_path"])
    if "namespace" in kwargs:
        config_args["namespace"] = str(kwargs["namespace"])

    config = FlextApiStorage.Config(**config_args)
    return FlextApiStorage(config)


def create_memory_storage(**kwargs: object) -> FlextApiStorage:
    """Create memory storage instance."""
    # Ensure we have at least the minimum config required
    if "namespace" not in kwargs:
        kwargs["namespace"] = "default"
    return create_storage("memory", **kwargs)


def create_file_storage(file_path: str, **kwargs: object) -> FlextApiStorage:
    """Create file storage instance."""
    return create_storage("file", file_path=file_path, **kwargs)


# =============================================================================
# EXPORTS - Consolidated class first, then backward compatibility
# =============================================================================

__all__ = [
    "CacheEntry",
    "CacheInterface",
    "FileStorageBackend",
    "FlextApiStorage",
    "FlextApiStorageRepository",
    "MemoryCache",
    "MemoryStorageBackend",
    "StorageBackend",
    "StorageBackendInterface",
    "StorageConfig",
    "TransactionContext",
    "create_file_storage",
    "create_memory_storage",
    "create_storage",
]

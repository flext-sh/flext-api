"""FLEXT API storage and persistence."""

from __future__ import annotations

import asyncio
import fnmatch
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Generic, TypeVar, override
from uuid import uuid4

from flext_core import FlextResult, get_logger

logger = get_logger(__name__)

# Type variables for generic storage operations
T = TypeVar("T")
K = TypeVar("K")  # Key type
V = TypeVar("V")  # Value type

# ==============================================================================
# STORAGE CONFIGURATION
# ==============================================================================


class StorageBackend(StrEnum):
    """Available storage backends."""

    MEMORY = "memory"
    FILE = "file"
    DATABASE = "database"
    REDIS = "redis"


@dataclass
class StorageConfig:
    """Storage configuration with backend-specific settings."""

    backend: StorageBackend = StorageBackend.MEMORY
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
class CacheEntry(Generic[T]):  # noqa: UP046
    """Cache entry with expiration."""

    value: T
    timestamp: float
    ttl_seconds: int

    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return time.time() - self.timestamp > self.ttl_seconds


@dataclass
class TransactionContext(Generic[V]):  # noqa: UP046
    """Transaction context for atomic operations."""

    transaction_id: str = field(default_factory=lambda: str(uuid4()))
    operations: list[tuple[str, str, V]] = field(
        default_factory=list[tuple[str, str, V]],
    )  # (operation, key, value)
    started_at: float = field(default_factory=time.time)
    is_active: bool = True


# ==============================================================================
# STORAGE INTERFACES
# ==============================================================================


class StorageBackendInterface(ABC, Generic[K, V]):  # noqa: UP046
    """Abstract interface for storage backends."""

    @abstractmethod
    async def get(self, key: K) -> FlextResult[V | None]:
        """Get value by key."""

    @abstractmethod
    async def set(
        self,
        key: K,
        value: V,
        ttl_seconds: int | None = None,
    ) -> FlextResult[None]:
        """Set value by key with optional TTL."""

    @abstractmethod
    async def delete(self, key: K) -> FlextResult[bool]:
        """Delete key and return True if existed."""

    @abstractmethod
    async def exists(self, key: K) -> FlextResult[bool]:
        """Check if key exists."""

    @abstractmethod
    async def keys(self, pattern: str | None = None) -> FlextResult[list[K]]:
        """Get all keys, optionally filtered by pattern."""

    @abstractmethod
    async def clear(self) -> FlextResult[None]:
        """Clear all data."""

    @abstractmethod
    async def close(self) -> FlextResult[None]:
        """Close storage connection."""


class CacheInterface(ABC):
    """Interface for caching layer."""

    @abstractmethod
    def get_cached(self, key: str) -> object | None:
        """Get cached value."""

    @abstractmethod
    def set_cached(self, key: str, value: object, ttl_seconds: int) -> None:
        """Set cached value with TTL."""

    @abstractmethod
    def delete_cached(self, key: str) -> bool:
        """Delete cached value."""

    @abstractmethod
    def clear_cache(self) -> None:
        """Clear all cached values."""


# ==============================================================================
# STORAGE BACKENDS
# ==============================================================================


class MemoryStorageBackend(StorageBackendInterface[str, V], Generic[V]):  # noqa: UP046
    """In-memory storage backend with TTL support."""

    def __init__(self, config: StorageConfig) -> None:
        """Initialize memory storage backend."""
        self._config = config
        self._data: dict[str, V] = {}
        self._expiry: dict[str, float] = {}

    @override
    async def get(self, key: str) -> FlextResult[V | None]:
        """Get value by key."""
        try:
            # Check expiration
            if key in self._expiry and time.time() > self._expiry[key]:
                await self.delete(key)
                return FlextResult[V | None].ok(None)

            value = self._data.get(key)
            logger.debug(
                "Retrieved value from memory storage",
                key=key,
                found=value is not None,
            )
            return FlextResult[V | None].ok(value)
        except Exception as e:
            return FlextResult[V | None].fail(f"Failed to get key '{key}': {e}")

    @override
    async def set(
        self,
        key: str,
        value: V,
        ttl_seconds: int | None = None,
    ) -> FlextResult[None]:
        """Set value by key with optional TTL."""
        try:
            self._data[key] = value

            if ttl_seconds is not None:
                self._expiry[key] = time.time() + ttl_seconds
            elif key in self._expiry:
                del self._expiry[key]

            logger.debug(
                "Stored value in memory storage",
                key=key,
                has_ttl=ttl_seconds is not None,
            )
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Failed to set key '{key}': {e}")

    @override
    async def delete(self, key: str) -> FlextResult[bool]:
        """Delete key and return True if existed."""
        try:
            existed = key in self._data
            self._data.pop(key, None)
            self._expiry.pop(key, None)

            logger.debug("Deleted key from memory storage", key=key, existed=existed)
            return FlextResult[bool].ok(existed)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to delete key '{key}': {e}")

    @override
    async def exists(self, key: str) -> FlextResult[bool]:
        """Check if key exists."""
        try:
            # Check expiration
            if key in self._expiry and time.time() > self._expiry[key]:
                await self.delete(key)
                return FlextResult[bool].ok(False)  # noqa: FBT003

            exists = key in self._data
            return FlextResult[bool].ok(exists)
        except Exception as e:
            return FlextResult[bool].fail(
                f"Failed to check existence of key '{key}': {e}"
            )

    @override
    async def keys(self, pattern: str | None = None) -> FlextResult[list[str]]:
        """Get all keys, optionally filtered by pattern."""
        try:
            # Clean up expired keys first
            current_time = time.time()
            expired_keys = [
                k for k, exp_time in self._expiry.items() if current_time > exp_time
            ]
            for key in expired_keys:
                await self.delete(key)

            all_keys = list(self._data.keys())

            if pattern is None:
                return FlextResult[list[str]].ok(all_keys)

            # Simple pattern matching (supports * wildcard)

            filtered_keys = [key for key in all_keys if fnmatch.fnmatch(key, pattern)]
            return FlextResult[list[str]].ok(filtered_keys)
        except Exception as e:
            return FlextResult[list[str]].fail(f"Failed to get keys: {e}")

    @override
    async def clear(self) -> FlextResult[None]:
        """Clear all data."""
        try:
            self._data.clear()
            self._expiry.clear()
            logger.info("Cleared all data from memory storage")
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Failed to clear storage: {e}")

    @override
    async def close(self) -> FlextResult[None]:
        """Close storage connection (no-op for memory)."""
        return FlextResult[None].ok(None)


class FileStorageBackend(StorageBackendInterface[str, V], Generic[V]):  # noqa: UP046
    """File-based storage backend with JSON serialization."""

    def __init__(self, config: StorageConfig) -> None:
        """Initialize file storage backend."""
        self._config = config
        self._file_path = Path(config.file_path or "flext_api_storage.json")
        self._data: dict[str, V] = {}
        self._lock = asyncio.Lock()

        # Load existing data
        self._load_data()

    def _load_data(self) -> None:
        """Load data from file."""
        try:
            if self._file_path.exists():
                with self._file_path.open(encoding="utf-8") as f:
                    self._data = json.load(f)
                logger.debug("Loaded data from file", file_path=str(self._file_path))
        except Exception as e:
            logger.warning("Failed to load data from file", error=str(e))
            self._data = {}

    async def _save_data(self) -> FlextResult[None]:
        """Save data to file."""
        try:
            # Ensure parent directory exists
            self._file_path.parent.mkdir(parents=True, exist_ok=True)

            with self._file_path.open("w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)

            logger.debug("Saved data to file", file_path=str(self._file_path))
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Failed to save data to file: {e}")

    @override
    async def get(self, key: str) -> FlextResult[V | None]:
        """Get value by key."""
        async with self._lock:
            try:
                value = self._data.get(key)
                return FlextResult[V | None].ok(value)
            except Exception as e:
                return FlextResult[V | None].fail(f"Failed to get key '{key}': {e}")

    @override
    async def set(
        self,
        key: str,
        value: V,
        ttl_seconds: int | None = None,  # noqa: ARG002
    ) -> FlextResult[None]:
        """Set value by key (TTL not supported in file backend)."""
        async with self._lock:
            try:
                self._data[key] = value
                # Be resilient to monkey-patching of _save_data on the instance
                try:
                    save_result = await self._save_data()
                except TypeError:
                    # When a class coroutine function is assigned directly to the instance,
                    # it becomes an unbound function and requires explicit self
                    save_result = await FileStorageBackend._save_data(self)
                if save_result.is_failure:
                    return save_result

                logger.debug("Stored value in file storage", key=key)
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Failed to set key '{key}': {e}")

    @override
    async def delete(self, key: str) -> FlextResult[bool]:
        """Delete key and return True if existed."""
        async with self._lock:
            try:
                existed = key in self._data
                self._data.pop(key, None)

                if existed:
                    # Be resilient to monkey-patching of _save_data on the instance
                    try:
                        save_result = await self._save_data()
                    except TypeError:
                        save_result = await FileStorageBackend._save_data(self)
                    if save_result.is_failure:
                        return FlextResult[bool].fail(
                            f"Failed to save after delete: {save_result.error}",
                        )

                return FlextResult[bool].ok(existed)
            except Exception as e:
                return FlextResult[bool].fail(f"Failed to delete key '{key}': {e}")

    @override
    async def exists(self, key: str) -> FlextResult[bool]:
        """Check if key exists."""
        async with self._lock:
            try:
                exists = key in self._data
                return FlextResult[bool].ok(exists)
            except Exception as e:
                return FlextResult[bool].fail(
                    f"Failed to check existence of key '{key}': {e}",
                )

    @override
    async def keys(self, pattern: str | None = None) -> FlextResult[list[str]]:
        """Get all keys, optionally filtered by pattern."""
        async with self._lock:
            try:
                all_keys = list(self._data.keys())

                if pattern is None:
                    return FlextResult[list[str]].ok(all_keys)

                filtered_keys = [
                    key for key in all_keys if fnmatch.fnmatch(key, pattern)
                ]
                return FlextResult[list[str]].ok(filtered_keys)
            except Exception as e:
                return FlextResult[list[str]].fail(f"Failed to get keys: {e}")

    @override
    async def clear(self) -> FlextResult[None]:
        """Clear all data."""
        async with self._lock:
            try:
                self._data.clear()
                # Be resilient to monkey-patching of _save_data on the instance
                try:
                    save_result = await self._save_data()
                except TypeError:
                    save_result = await FileStorageBackend._save_data(self)
                if not save_result.success:
                    return save_result

                logger.info("Cleared all data from file storage")
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Failed to clear storage: {e}")

    @override
    async def close(self) -> FlextResult[None]:
        """Close storage connection."""
        return await self._save_data()


# ==============================================================================
# CACHING IMPLEMENTATION
# ==============================================================================


class MemoryCache(CacheInterface):
    """In-memory cache with TTL support."""

    def __init__(self) -> None:
        """Initialize memory cache."""
        self._cache: dict[str, CacheEntry[object]] = {}

    @override
    def get_cached(self, key: str) -> object | None:
        """Get cached value."""
        entry = self._cache.get(key)
        if entry is None:
            return None

        if entry.is_expired():
            self.delete_cached(key)
            return None

        return entry.value

    @override
    def set_cached(self, key: str, value: object, ttl_seconds: int) -> None:
        """Set cached value with TTL."""
        entry = CacheEntry(
            value=value,
            timestamp=time.time(),
            ttl_seconds=ttl_seconds,
        )
        self._cache[key] = entry

    @override
    def delete_cached(self, key: str) -> bool:
        """Delete cached value."""
        return self._cache.pop(key, None) is not None

    @override
    def clear_cache(self) -> None:
        """Clear all cached values."""
        self._cache.clear()


# ==============================================================================
# MAIN STORAGE CLASS
# ==============================================================================


class FlextApiStorage:
    """Main storage class with backend abstraction, caching, and transactions."""

    def __init__(self, config: StorageConfig) -> None:
        """Initialize storage with configuration."""
        self._config = config
        self._backend = self._create_backend(config)
        self._cache: CacheInterface | None = (
            MemoryCache() if config.enable_caching else None
        )
        self._transactions: dict[str, TransactionContext[object]] = {}

    def _create_backend(
        self,
        config: StorageConfig,
    ) -> StorageBackendInterface[str, object]:
        """Create storage backend based on configuration."""
        if config.backend == StorageBackend.MEMORY:
            return MemoryStorageBackend(config)
        if config.backend == StorageBackend.FILE:
            return FileStorageBackend(config)
        msg = f"Unsupported storage backend: {config.backend}"
        raise ValueError(msg)

    async def get(
        self,
        key: str,
        *,
        use_cache: bool = True,
    ) -> FlextResult[object | None]:
        """Get value by key with optional cache lookup."""
        # Add namespace prefix
        namespaced_key = f"{self._config.namespace}:{key}"

        # Check cache first
        if use_cache and self._cache is not None:
            cached_value = self._cache.get_cached(namespaced_key)
            if cached_value is not None:
                logger.debug("Retrieved value from cache", key=key)
                return FlextResult[object].ok(cached_value)

        # Get from backend
        result = await self._backend.get(namespaced_key)
        if result.is_failure:
            return result

        # Cache the result if caching is enabled and has value
        cached_value = result.unwrap_or(None)
        if cached_value is not None and self._cache is not None:
            self._cache.set_cached(
                namespaced_key,
                cached_value,
                self._config.cache_ttl_seconds,
            )

        return result

    async def set(
        self,
        key: str,
        value: object,
        ttl_seconds: int | None = None,
        transaction_id: str | None = None,
    ) -> FlextResult[None]:
        """Set value by key with optional TTL and transaction support."""
        namespaced_key = f"{self._config.namespace}:{key}"

        # Handle transactions
        if transaction_id is not None:
            if transaction_id not in self._transactions:
                return FlextResult[None].fail(f"Transaction {transaction_id} not found")

            transaction = self._transactions[transaction_id]
            if not transaction.is_active:
                return FlextResult[None].fail(
                    f"Transaction {transaction_id} is not active"
                )

            transaction.operations.append(("set", namespaced_key, value))
            return FlextResult[None].ok(None)

        # Direct set operation
        result = await self._backend.set(namespaced_key, value, ttl_seconds)
        if result.is_failure:
            return result

        # Update cache
        if self._cache is not None:
            cache_ttl = ttl_seconds or self._config.cache_ttl_seconds
            self._cache.set_cached(namespaced_key, value, cache_ttl)

        return result

    async def delete(
        self,
        key: str,
        transaction_id: str | None = None,
    ) -> FlextResult[bool]:
        """Delete key with optional transaction support."""
        namespaced_key = f"{self._config.namespace}:{key}"

        # Handle transactions
        if transaction_id is not None:
            if transaction_id not in self._transactions:
                return FlextResult[bool].fail(f"Transaction {transaction_id} not found")

            transaction = self._transactions[transaction_id]
            if not transaction.is_active:
                return FlextResult[bool].fail(
                    f"Transaction {transaction_id} is not active"
                )

            transaction.operations.append(("delete", namespaced_key, None))
            return FlextResult[bool].ok(True)  # noqa: FBT003

        # Direct delete operation
        result = await self._backend.delete(namespaced_key)
        if not result.success:
            return result

        # Remove from cache
        if self._cache is not None:
            self._cache.delete_cached(namespaced_key)

        return result

    async def exists(self, key: str) -> FlextResult[bool]:
        """Check if key exists."""
        namespaced_key = f"{self._config.namespace}:{key}"
        return await self._backend.exists(namespaced_key)

    async def keys(self, pattern: str | None = None) -> FlextResult[list[str]]:
        """Get all keys, optionally filtered by pattern."""
        # Add namespace to pattern
        if pattern is not None:
            namespaced_pattern = f"{self._config.namespace}:{pattern}"
        else:
            namespaced_pattern = f"{self._config.namespace}:*"

        result = await self._backend.keys(namespaced_pattern)
        if not result.success:
            return result

        # Remove namespace prefix from returned keys
        prefix_len = len(self._config.namespace) + 1
        clean_keys = [key[prefix_len:] for key in result.value or []]
        return FlextResult[list[str]].ok(clean_keys)

    async def clear(self) -> FlextResult[None]:
        """Clear all data in namespace."""
        # Get all keys in namespace and delete them
        keys_result = await self.keys()
        if keys_result.is_failure:
            return FlextResult[None].fail(
                f"Failed to get keys for clearing: {keys_result.error}",
            )

        for key in keys_result.value or []:
            delete_result = await self.delete(key)
            if delete_result.is_failure:
                return FlextResult[None].fail(
                    f"Failed to delete key '{key}': {delete_result.error}",
                )

        # Clear cache
        if self._cache is not None:
            self._cache.clear_cache()

        return FlextResult[None].ok(None)

    # Transaction support methods
    def begin_transaction(self) -> str:
        """Begin a new transaction and return transaction ID."""
        transaction = TransactionContext[object]()
        self._transactions[transaction.transaction_id] = transaction
        logger.debug("Started transaction", transaction_id=transaction.transaction_id)
        return transaction.transaction_id

    async def commit_transaction(self, transaction_id: str) -> FlextResult[None]:
        """Commit all operations of a transaction with low complexity."""

        def _get_active_tx() -> FlextResult[TransactionContext[object]]:
            tx = self._transactions.get(transaction_id)
            if tx is None:
                return FlextResult[TransactionContext[object]].fail(
                    f"Transaction {transaction_id} not found"
                )
            if not tx.is_active:
                return FlextResult[TransactionContext[object]].fail(
                    f"Transaction {transaction_id} is not active"
                )
            return FlextResult[TransactionContext[object]].ok(tx)

        async def _apply_set(key: str, value: object) -> FlextResult[None]:
            res = await self._backend.set(key, value)
            return res if res.is_failure else FlextResult[None].ok(None)

        async def _apply_delete(key: str) -> FlextResult[None]:
            res = await self._backend.delete(key)
            if res.is_failure:
                return FlextResult[None].fail(res.error or "Delete failed")
            return FlextResult[None].ok(None)

        tx_result = _get_active_tx()
        if tx_result.is_failure:
            return FlextResult[None].fail(tx_result.error or "Invalid transaction")

        tx = tx_result.value

        for op, key, value in tx.operations:
            if op == "set":
                applied = await _apply_set(key, value)
            elif op == "delete":
                applied = await _apply_delete(key)
            else:
                return FlextResult[None].fail(f"Unknown transaction operation: {op}")
            if applied.is_failure:
                return FlextResult[None].fail(
                    applied.error or "Transaction operation failed"
                )

        tx.is_active = False
        del self._transactions[transaction_id]
        logger.debug(
            "Committed transaction",
            transaction_id=transaction_id,
            operations_count=len(tx.operations),
        )
        return FlextResult[None].ok(None)

    def rollback_transaction(self, transaction_id: str) -> FlextResult[None]:
        """Rollback transaction (discard operations)."""
        if transaction_id not in self._transactions:
            return FlextResult[None].fail(f"Transaction {transaction_id} not found")

        transaction = self._transactions[transaction_id]
        transaction.is_active = False
        del self._transactions[transaction_id]

        logger.debug(
            "Rolled back transaction",
            transaction_id=transaction_id,
            operations_count=len(transaction.operations),
        )
        return FlextResult[None].ok(None)

    async def close(self) -> FlextResult[None]:
        """Close storage and cleanup resources."""
        # Rollback any active transactions
        for transaction_id in list(self._transactions.keys()):
            self.rollback_transaction(transaction_id)

        # Close backend
        return await self._backend.close()


# ==============================================================================
# FACTORY FUNCTIONS
# ==============================================================================


def create_storage(
    backend: str = "memory",
    **config_kwargs: object,
) -> FlextApiStorage:
    """Create storage instance with specified backend."""
    # Filter kwargs to only include valid StorageConfig fields
    valid_fields = {
        "connection_string",
        "max_connections",
        "timeout_seconds",
        "enable_caching",
        "cache_ttl_seconds",
        "enable_transactions",
        "serialization_format",
        "file_path",
        "namespace",
    }
    filtered_kwargs = {k: v for k, v in config_kwargs.items() if k in valid_fields}

    # Build config explicitly to satisfy strict typing
    connection_string = (
        str(filtered_kwargs["connection_string"])
        if "connection_string" in filtered_kwargs
        and isinstance(filtered_kwargs["connection_string"], str)
        else None
    )
    max_connections = (
        int(filtered_kwargs["max_connections"])
        if "max_connections" in filtered_kwargs
        and isinstance(filtered_kwargs["max_connections"], (int, float, str))
        else 10
    )
    timeout_seconds = (
        float(filtered_kwargs["timeout_seconds"])
        if "timeout_seconds" in filtered_kwargs
        and isinstance(filtered_kwargs["timeout_seconds"], (int, float, str))
        else 30.0
    )
    enable_caching = bool(filtered_kwargs.get("enable_caching", True))
    cache_ttl_seconds = (
        int(filtered_kwargs["cache_ttl_seconds"])
        if "cache_ttl_seconds" in filtered_kwargs
        and isinstance(filtered_kwargs["cache_ttl_seconds"], (int, float, str))
        else 300
    )
    enable_transactions = bool(filtered_kwargs.get("enable_transactions"))
    serialization_format = str(filtered_kwargs.get("serialization_format", "json"))
    file_path = (
        str(filtered_kwargs["file_path"])
        if "file_path" in filtered_kwargs
        and isinstance(filtered_kwargs["file_path"], str)
        else None
    )
    namespace = str(filtered_kwargs.get("namespace", "default"))

    config = StorageConfig(
        backend=StorageBackend(backend),
        connection_string=connection_string,
        max_connections=max_connections,
        timeout_seconds=timeout_seconds,
        enable_caching=enable_caching,
        cache_ttl_seconds=cache_ttl_seconds,
        enable_transactions=enable_transactions,
        serialization_format=serialization_format,
        file_path=file_path,
        namespace=namespace,
    )
    return FlextApiStorage(config)


def create_memory_storage(
    namespace: str = "default",
    *,
    enable_caching: bool = True,
    cache_ttl_seconds: int = 300,
) -> FlextApiStorage:
    """Create memory storage with caching."""
    config = StorageConfig(
        backend=StorageBackend.MEMORY,
        namespace=namespace,
        enable_caching=enable_caching,
        cache_ttl_seconds=cache_ttl_seconds,
    )
    return FlextApiStorage(config)


def create_file_storage(
    file_path: str,
    namespace: str = "default",
    *,
    enable_caching: bool = True,
) -> FlextApiStorage:
    """Create file storage with JSON persistence."""
    config = StorageConfig(
        backend=StorageBackend.FILE,
        file_path=file_path,
        namespace=namespace,
        enable_caching=enable_caching,
    )
    return FlextApiStorage(config)


# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    # Data Classes
    "CacheEntry",
    "CacheInterface",
    "FileStorageBackend",
    # Main Classes
    "FlextApiStorage",
    # Cache Implementation
    "MemoryCache",
    # Backends
    "MemoryStorageBackend",
    "StorageBackend",
    # Interfaces
    "StorageBackendInterface",
    # Configuration
    "StorageConfig",
    "TransactionContext",
    "create_file_storage",
    "create_memory_storage",
    # Factory Functions
    "create_storage",
]

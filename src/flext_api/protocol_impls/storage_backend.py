"""Storage Backend Protocol Implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import override

from flext_core import FlextLogger, FlextRuntime, r, u

from flext_api import p, t


class StorageBackendImplementation(p.Api.Storage.StorageBackend):
    """Storage backend implementation conforming to StorageBackend."""

    def __init__(self) -> None:
        """Initialize storage backend protocol implementation."""
        self._storage: dict[str, t.ApiJsonValue] = {}
        self.logger = FlextLogger(__name__)

    @override
    def clear(self) -> r[bool]:
        """Clear all stored values."""

        def _clear() -> bool:
            self._storage = {}
            self.logger.debug("Cleared all storage data")
            return True

        return u.try_(
            _clear,
            catch=(ValueError, TypeError, KeyError, ConnectionError),
        ).map_error(lambda e: f"Clear operation failed: {e}")

    @override
    def delete(self, key: str) -> r[bool]:
        """Delete value by key."""
        try:
            if not key:
                return r[bool].fail("Storage key cannot be empty")
            if key in self._storage:
                storage_data = dict(self._storage)
                del storage_data[key]
                self._storage = storage_data
                self.logger.debug("Deleted data with key: %s", key)
                return r[bool].ok(value=True)
            return r[bool].fail(f"Key not found: {key}")
        except (ValueError, TypeError, KeyError, ConnectionError) as e:
            return r[bool].fail(f"Delete operation failed: {e}")

    @override
    def exists(self, key: str) -> r[bool]:
        """Check if key exists."""
        return u.try_(
            lambda: str(key) in self._storage,
            catch=(ValueError, TypeError, KeyError, ConnectionError),
        ).map_error(lambda e: f"Exists check failed: {e}")

    @override
    def get(self, key: str) -> r[t.ApiJsonValue]:
        """Retrieve value by key."""
        try:
            if not key:
                return r[t.ApiJsonValue].fail("Storage key cannot be empty")
            if key in self._storage:
                value = self._storage[key]
                self.logger.debug("Retrieved data with key: %s", key)
                return r[t.ApiJsonValue].ok(value)
            return r[t.ApiJsonValue].fail(f"Key not found: {key}")
        except (ValueError, TypeError, KeyError, ConnectionError) as e:
            return r[t.ApiJsonValue].fail(f"Retrieval operation failed: {e}")

    @override
    def keys(self) -> r[list[str]]:
        """Get all keys."""
        return u.try_(
            lambda: list(self._storage),
            catch=(ValueError, TypeError, KeyError, ConnectionError),
        ).map_error(lambda e: f"Keys operation failed: {e}")

    @override
    def set(
        self,
        key: str,
        value: t.ApiJsonValue,
        timeout: int | None = None,
    ) -> r[bool]:
        """Store value with optional timeout."""
        if not key:
            return r[bool].fail("Storage key cannot be empty")

        def _set() -> bool:
            _ = timeout
            storage_data = dict(self._storage)
            storage_data[str(key)] = FlextRuntime.normalize_to_container(value)
            self._storage = storage_data
            self.logger.debug("Stored data with key: %s", key)
            return True

        return u.try_(
            _set,
            catch=(ValueError, TypeError, KeyError, ConnectionError),
        ).map_error(lambda e: f"Storage operation failed: {e}")

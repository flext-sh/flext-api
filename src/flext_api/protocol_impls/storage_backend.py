"""Storage Backend Protocol Implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import MutableMapping
from typing import override

from flext_api import p, r, t, u


class FlextApiStorageBackendImplementation(p.Api.Storage.StorageBackend):
    """Storage backend implementation conforming to StorageBackend."""

    def __init__(self) -> None:
        """Initialize storage backend protocol implementation."""
        self._storage: MutableMapping[str, t.ApiJsonValue] = {}
        self.logger = u.fetch_logger(__name__)

    @override
    def clear(self) -> p.Result[bool]:
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
    def delete(self, key: str) -> p.Result[bool]:
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
    def exists(self, key: str) -> p.Result[bool]:
        """Check if key exists."""
        return u.try_(
            lambda: key in self._storage,
            catch=(ValueError, TypeError, KeyError, ConnectionError),
        ).map_error(lambda e: f"Exists check failed: {e}")

    @override
    def get(self, key: str) -> p.Result[t.ApiJsonValue]:
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
    def keys(self) -> p.Result[t.StrSequence]:
        """Get all keys."""
        try:
            keys_list: t.StrSequence = list(self._storage)
            return r[t.StrSequence].ok(keys_list)
        except (ValueError, TypeError, KeyError, ConnectionError) as e:
            return r[t.StrSequence].fail(f"Keys operation failed: {e}")

    @override
    def set(
        self,
        key: str,
        value: t.ApiJsonValue,
        timeout: int | None = None,
    ) -> p.Result[bool]:
        """Store value with optional timeout."""
        if not key:
            return r[bool].fail("Storage key cannot be empty")

        def _set() -> bool:
            _ = timeout
            storage_data = dict(self._storage)
            storage_data[key] = value
            self._storage = storage_data
            self.logger.debug("Stored data with key: %s", key)
            return True

        return u.try_(
            _set,
            catch=(ValueError, TypeError, KeyError, ConnectionError),
        ).map_error(lambda e: f"Storage operation failed: {e}")


__all__: list[str] = ["FlextApiStorageBackendImplementation"]

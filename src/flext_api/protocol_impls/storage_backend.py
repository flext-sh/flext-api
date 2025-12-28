"""Storage Backend Protocol Implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import cast

from flext_core import FlextLogger, r

from flext_api.protocols import p
from flext_api.typings import t


class StorageBackendImplementation(p.Api.Storage.StorageBackendProtocol):
    """Storage backend implementation conforming to StorageBackendProtocol."""

    def __init__(self) -> None:
        """Initialize storage backend protocol implementation."""
        self._storage: dict[str, t.GeneralValueType] = {}
        self.logger = FlextLogger(__name__)

    def get(self, key: str) -> r[object]:
        """Retrieve value by key."""
        try:
            if not key:
                return r[object].fail("Storage key cannot be empty")

            if key in self._storage:
                value = self._storage[key]
                self.logger.debug("Retrieved data with key: %s", key)
                return r[object].ok(value)
            return r[object].fail(f"Key not found: {key}")

        except Exception as e:
            return r[object].fail(f"Retrieval operation failed: {e}")

    def set(
        self,
        key: str,
        value: object,
        timeout: int | None = None,
    ) -> r[bool]:
        """Store value with optional timeout."""
        try:
            if not key:
                return r[bool].fail("Storage key cannot be empty")

            # Acknowledge timeout parameter (not implemented in this simple backend)
            _ = timeout
            self._storage[str(key)] = cast("t.GeneralValueType", value)
            self.logger.debug("Stored data with key: %s", key)
            return r[bool].ok(True)

        except Exception as e:
            return r[bool].fail(f"Storage operation failed: {e}")

    def delete(self, key: str) -> r[bool]:
        """Delete value by key."""
        try:
            if not key:
                return r[bool].fail("Storage key cannot be empty")

            if key in self._storage:
                del self._storage[key]
                self.logger.debug("Deleted data with key: %s", key)
                return r[bool].ok(True)
            return r[bool].fail(f"Key not found: {key}")

        except Exception as e:
            return r[bool].fail(f"Delete operation failed: {e}")

    def exists(self, key: str) -> r[bool]:
        """Check if key exists."""
        try:
            exists = str(key) in self._storage
            return r[bool].ok(exists)
        except Exception as e:
            return r[bool].fail(f"Exists check failed: {e}")

    def clear(self) -> r[bool]:
        """Clear all stored values."""
        try:
            self._storage.clear()
            self.logger.debug("Cleared all storage data")
            return r[bool].ok(True)
        except Exception as e:
            return r[bool].fail(f"Clear operation failed: {e}")

    def keys(self) -> r[list[str]]:
        """Get all keys."""
        try:
            storage_keys: list[str] = list(self._storage)
            return r[list[str]].ok(storage_keys)
        except Exception as e:
            return r[list[str]].fail(f"Keys operation failed: {e}")

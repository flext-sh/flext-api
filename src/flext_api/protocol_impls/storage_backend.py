"""Storage Backend Protocol Implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextLogger, FlextResult

from flext_api.protocols import FlextApiProtocols
from flext_api.typings import FlextApiTypes


class StorageBackendImplementation(FlextApiProtocols.StorageBackendProtocol):
    """Storage backend implementation conforming to StorageBackendProtocol."""

    def __init__(self) -> None:
        """Initialize storage backend protocol implementation."""
        self._storage: dict[str, FlextApiTypes.JsonValue] = {}
        self._logger = FlextLogger(__name__)

    def get(
        self, key: str, default: FlextApiTypes.JsonValue = None
    ) -> FlextResult[FlextApiTypes.JsonValue]:
        """Retrieve value by key."""
        try:
            if not key:
                return FlextResult[FlextApiTypes.JsonValue].fail(
                    "Storage key cannot be empty"
                )

            if key in self._storage:
                value = self._storage[key]
                self._logger.debug(f"Retrieved data with key: {key}")
                return FlextResult[FlextApiTypes.JsonValue].ok(value)
            if default is not None:
                return FlextResult[FlextApiTypes.JsonValue].ok(default)
            return FlextResult[FlextApiTypes.JsonValue].fail(f"Key not found: {key}")

        except Exception as e:
            return FlextResult[FlextApiTypes.JsonValue].fail(
                f"Retrieval operation failed: {e}"
            )

    def set(
        self,
        key: str,
        value: object,
        _timeout: int | None = None,
    ) -> FlextResult[None]:
        """Store value with optional timeout."""
        try:
            if not key:
                return FlextResult[None].fail("Storage key cannot be empty")

            self._storage[str(key)] = value
            self._logger.debug(f"Stored data with key: {key}")
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Storage operation failed: {e}")

    def delete(self, key: str) -> FlextResult[None]:
        """Delete value by key."""
        try:
            if not key:
                return FlextResult[None].fail("Storage key cannot be empty")

            if key in self._storage:
                del self._storage[key]
                self._logger.debug(f"Deleted data with key: {key}")
                return FlextResult[None].ok(None)
            return FlextResult[None].fail(f"Key not found: {key}")

        except Exception as e:
            return FlextResult[None].fail(f"Delete operation failed: {e}")

    def exists(self, key: str) -> FlextResult[bool]:
        """Check if key exists."""
        try:
            exists = str(key) in self._storage
            return FlextResult[bool].ok(exists)
        except Exception as e:
            return FlextResult[bool].fail(f"Exists check failed: {e}")

    def clear(self) -> FlextResult[None]:
        """Clear all stored values."""
        try:
            self._storage.clear()
            self._logger.debug("Cleared all storage data")
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Clear operation failed: {e}")

    def keys(self) -> FlextResult[list[str]]:
        """Get all keys."""
        try:
            storage_keys: list[str] = list(self._storage)
            return FlextResult[list[str]].ok(storage_keys)
        except Exception as e:
            return FlextResult[list[str]].fail(f"Keys operation failed: {e}")

"""Storage Backend Protocol Implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextCore

from flext_api.protocols import FlextApiProtocols
from flext_api.typings import FlextApiTypes


class StorageBackendImplementation(FlextApiProtocols.StorageBackendProtocol):
    """Storage backend implementation conforming to StorageBackendProtocol."""

    def __init__(self) -> None:
        """Initialize storage backend protocol implementation."""
        self._storage: dict[str, FlextApiTypes.JsonValue] = {}
        self.logger = FlextCore.Logger(__name__)

    def get(
        self, key: str, default: FlextApiTypes.JsonValue = None
    ) -> FlextCore.Result[FlextApiTypes.JsonValue]:
        """Retrieve value by key."""
        try:
            if not key:
                return FlextCore.Result[FlextApiTypes.JsonValue].fail(
                    "Storage key cannot be empty"
                )

            if key in self._storage:
                value = self._storage[key]
                self.logger.debug(f"Retrieved data with key: {key}")
                return FlextCore.Result[FlextApiTypes.JsonValue].ok(value)
            if default is not None:
                return FlextCore.Result[FlextApiTypes.JsonValue].ok(default)
            return FlextCore.Result[FlextApiTypes.JsonValue].fail(
                f"Key not found: {key}"
            )

        except Exception as e:
            return FlextCore.Result[FlextApiTypes.JsonValue].fail(
                f"Retrieval operation failed: {e}"
            )

    def set(
        self,
        key: str,
        value: object,
        _timeout: int | None = None,
    ) -> FlextCore.Result[None]:
        """Store value with optional timeout."""
        try:
            if not key:
                return FlextCore.Result[None].fail("Storage key cannot be empty")

            self._storage[str(key)] = value
            self.logger.debug(f"Stored data with key: {key}")
            return FlextCore.Result[None].ok(None)

        except Exception as e:
            return FlextCore.Result[None].fail(f"Storage operation failed: {e}")

    def delete(self, key: str) -> FlextCore.Result[None]:
        """Delete value by key."""
        try:
            if not key:
                return FlextCore.Result[None].fail("Storage key cannot be empty")

            if key in self._storage:
                del self._storage[key]
                self.logger.debug(f"Deleted data with key: {key}")
                return FlextCore.Result[None].ok(None)
            return FlextCore.Result[None].fail(f"Key not found: {key}")

        except Exception as e:
            return FlextCore.Result[None].fail(f"Delete operation failed: {e}")

    def exists(self, key: str) -> FlextCore.Result[bool]:
        """Check if key exists."""
        try:
            exists = str(key) in self._storage
            return FlextCore.Result[bool].ok(exists)
        except Exception as e:
            return FlextCore.Result[bool].fail(f"Exists check failed: {e}")

    def clear(self) -> FlextCore.Result[None]:
        """Clear all stored values."""
        try:
            self._storage.clear()
            self.logger.debug("Cleared all storage data")
            return FlextCore.Result[None].ok(None)
        except Exception as e:
            return FlextCore.Result[None].fail(f"Clear operation failed: {e}")

    def keys(self) -> FlextCore.Result[FlextCore.Types.StringList]:
        """Get all keys."""
        try:
            storage_keys: FlextCore.Types.StringList = list(self._storage)
            return FlextCore.Result[FlextCore.Types.StringList].ok(storage_keys)
        except Exception as e:
            return FlextCore.Result[FlextCore.Types.StringList].fail(
                f"Keys operation failed: {e}"
            )

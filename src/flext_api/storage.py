"""FLEXT API storage abstraction layer."""

from __future__ import annotations


class FlextAPIStorage:
    """Simple storage abstraction for FLEXT API."""

    def __init__(self) -> None:
        """Initialize storage instance."""
        self._data: dict[str, object] = {}

    def get(self, key: str) -> object | None:
        """Get value by key."""
        return self._data.get(key)

    def set(self, key: str, value: object) -> None:
        """Set value by key."""
        self._data[key] = value

    def delete(self, key: str) -> bool:
        """Delete key and return True if existed."""
        return self._data.pop(key, None) is not None

"""Compatibility storage module for legacy tests.

Provides a minimal in-memory storage class compatible with tests.
"""

from __future__ import annotations


class FlextAPIStorage:
    """Simple in-memory key/value storage for tests.

    Provides minimal get/set/delete operations.
    """

    def __init__(self) -> None:
      """Initialize empty storage."""
      self._store: dict[str, object] = {}

    def get(self, key: str) -> object | None:
      """Get a value by key."""
      return self._store.get(key)

    def set(self, key: str, value: object) -> None:
      """Set a key to a value."""
      self._store[key] = value

    def delete(self, key: str) -> bool:
      """Delete a key if present and return True if it existed."""
      if key in self._store:
          del self._store[key]
          return True
      return False


__all__ = ["FlextAPIStorage"]

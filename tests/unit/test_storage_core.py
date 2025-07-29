"""Tests for storage module."""

from __future__ import annotations

from flext_api.storage import FlextAPIStorage


class TestFlextAPIStorage:
    """Test cases for storage functionality."""

    def test_storage_creation(self) -> None:
        """Test creating storage instance."""
        storage = FlextAPIStorage()
        assert storage is not None

    def test_get_nonexistent_key(self) -> None:
        """Test getting non-existent key returns None."""
        storage = FlextAPIStorage()
        result = storage.get("nonexistent")
        assert result is None

    def test_set_and_get(self) -> None:
        """Test setting and getting value."""
        storage = FlextAPIStorage()
        storage.set("key1", "value1")

        result = storage.get("key1")
        if result != "value1":
            raise AssertionError(f"Expected {'value1'}, got {result}")

    def test_delete_existing_key(self) -> None:
        """Test deleting existing key."""
        storage = FlextAPIStorage()
        storage.set("key1", "value1")

        result = storage.delete("key1")
        if not (result):
            raise AssertionError(f"Expected True, got {result}")

        # Key should be gone
        assert storage.get("key1") is None

    def test_delete_nonexistent_key(self) -> None:
        """Test deleting non-existent key."""
        storage = FlextAPIStorage()
        result = storage.delete("nonexistent")
        if result:
            raise AssertionError(f"Expected False, got {result}")

    def test_overwrite_key(self) -> None:
        """Test overwriting existing key."""
        storage = FlextAPIStorage()
        storage.set("key1", "value1")
        storage.set("key1", "value2")

        result = storage.get("key1")
        if result != "value2":
            raise AssertionError(f"Expected {'value2'}, got {result}")

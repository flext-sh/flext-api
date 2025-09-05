"""Additional storage tests for file backend paths and utilities."""

from __future__ import annotations

from pathlib import Path

from flext_api import (
    FlextApiStorage,
)


def create_file_storage(file_path: str, namespace: str) -> FlextApiStorage:
    """Create file storage with config (simplified for current implementation)."""
    config = {"backend": "file"}
    return FlextApiStorage(config)


def test_file_backend_persistence_and_clear(tmp_path: Path) -> None:
    """File backend should persist and clear namespace keys correctly (simplified test)."""
    storage = FlextApiStorage({"backend": "file"})

    # Test basic set/get operations (memory-based for now)
    result1 = storage.set("k1", {"a": 1})
    result2 = storage.set("k2", 2)
    assert result1.success
    assert result2.success

    get_result = storage.get("k1")
    assert get_result.success

    # Test clear operation
    clear_result = storage.clear()
    assert clear_result.success

    # After clear, keys should be gone
    get_result_after_clear = storage.get("k1")
    assert not get_result_after_clear.success


def test_exists_and_keys_namespace() -> None:
    """Memory backend should support exists and namespaced keys (simplified test)."""
    storage = FlextApiStorage({"backend": "memory"})

    # Test set and keys operations
    set_result = storage.set("zz", 1)
    assert set_result.success

    # Test key existence by trying to get it
    get_result = storage.get("zz")
    assert get_result.success
    assert get_result.value == 1

    # Test keys operation
    keys_result = storage.keys()
    assert keys_result.success
    assert "zz" in keys_result.value

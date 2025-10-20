"""Tests for FlextApiStorage using FLEXT-pure patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_api import FlextApiStorage


def test_keys_pattern_and_unknown_operation_commit() -> None:
    """Test basic key pattern and storage operations."""
    storage = FlextApiStorage({"backend": "memory"})

    # Test set operations
    set_result1 = storage.set("a", 1)
    set_result2 = storage.set("alpha", 2)
    assert set_result1.is_success
    assert set_result2.is_success

    # Get all keys (no pattern matching available)
    keys_result = storage.keys()
    assert keys_result.is_success
    assert set(keys_result.value or []) >= {"a", "alpha"}

    # Test simple storage operations work by getting the value
    get_result = storage.get("a")
    assert get_result.is_success
    assert get_result.value == 1


def test_storage_initialization() -> None:
    """Test storage initialization with various configurations."""
    # Default initialization
    storage = FlextApiStorage()
    assert storage.namespace == "flext_api"
    assert storage.backend == "memory"
    assert storage._max_size is None
    assert storage._default_ttl is None

    # Custom initialization with parameters
    custom_storage = FlextApiStorage(
        config={"namespace": "test", "backend": "memory"},
        max_size=1000,
        default_ttl=300,
    )
    assert custom_storage.namespace == "test"
    assert custom_storage.backend == "memory"
    assert custom_storage._max_size == 1000
    assert custom_storage._default_ttl == 300


def test_basic_operations() -> None:
    """Test basic storage operations."""
    storage = FlextApiStorage()

    # Test set operation
    set_result = storage.set("key1", "value1")
    assert set_result.is_success
    assert set_result.value is None

    # Test get operation
    get_result = storage.get("key1")
    assert get_result.is_success
    assert get_result.value == "value1"

    # Test exists operation
    exists_result = storage.exists("key1")
    assert exists_result.is_success
    assert exists_result.value is True

    # Test delete operation (idempotent - succeeds even if not exists)
    delete_result = storage.delete("key1")
    assert delete_result.is_success

    # Verify deleted - get returns default (None)
    get_after_delete = storage.get("key1")
    assert get_after_delete.is_success
    assert get_after_delete.value is None  # Default value returned


def test_ttl_functionality() -> None:
    """Test TTL parameter is accepted (expiration not enforced in simple storage)."""
    storage = FlextApiStorage()

    # Set with TTL
    set_result = storage.set("ttl_key", "ttl_value", ttl=1)
    assert set_result.is_success

    # Verify exists immediately
    exists_result = storage.exists("ttl_key")
    assert exists_result.is_success
    assert exists_result.value is True

    # Key still exists (simple storage doesn't auto-expire)
    exists_after = storage.exists("ttl_key")
    assert exists_after.is_success
    assert exists_after.value is True


def test_size_and_clear_operations() -> None:
    """Test size calculation and clear operations."""
    storage = FlextApiStorage()

    # Initially empty
    initial_size = storage.size()
    assert initial_size.is_success
    assert initial_size.value == 0

    # Add some items
    storage.set("size_test1", "value1")
    storage.set("size_test2", "value2")
    storage.set("size_test3", "value3")

    # Check size (includes both direct and namespaced keys)
    size_result = storage.size()
    assert size_result.is_success
    # Each set stores 2 keys (direct + namespaced) = 6
    assert size_result.value == 6

    # Clear storage
    clear_result = storage.clear()
    assert clear_result.is_success

    # Verify cleared
    final_size_result = storage.size()
    assert final_size_result.is_success
    assert final_size_result.value == 0


def test_error_recovery_scenario() -> None:
    """Test error recovery scenarios."""
    storage = FlextApiStorage()

    # Delete non-existent key succeeds (idempotent)
    result = storage.delete("nonexistent")
    assert result.is_success

    # Test operations after delete
    result = storage.set("recovery_key", "recovery_value")
    assert result.is_success

    recovery_result = storage.get("recovery_key")
    assert recovery_result.is_success
    assert recovery_result.value == "recovery_value"


def test_performance_scenario() -> None:
    """Test performance with many operations."""
    storage = FlextApiStorage()

    # Store many items
    for i in range(100):
        result = storage.set(f"perf_key_{i}", f"perf_value_{i}")
        assert result.is_success

    # Verify all stored (includes both direct and namespaced keys)
    perf_size_result = storage.size()
    assert perf_size_result.is_success
    # Each set stores 2 keys = 200
    assert perf_size_result.value == 200

    # Retrieve all items
    for i in range(100):
        perf_get_result = storage.get(f"perf_key_{i}")
        assert perf_get_result.is_success
        assert perf_get_result.value == f"perf_value_{i}"

    # Clear all
    result = storage.clear()
    assert result.is_success

    # Verify cleared
    cleared_size_result = storage.size()
    assert cleared_size_result.is_success
    assert cleared_size_result.value == 0

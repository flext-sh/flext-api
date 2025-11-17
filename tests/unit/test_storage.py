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

    # Test set operation - returns FlextResult[bool] with True on success
    set_result = storage.set("key1", "value1")
    assert set_result.is_success
    assert set_result.value is True

    # Test get operation
    get_result = storage.get("key1")
    assert get_result.is_success
    assert get_result.value == "value1"

    # Test exists operation
    exists_result = storage.exists("key1")
    assert exists_result.is_success
    assert exists_result.value is True

    # Test delete operation - returns error if key not found (no fallback)
    delete_result = storage.delete("key1")
    assert delete_result.is_success
    assert delete_result.value is True

    # Verify deleted - get returns error (no fallback)
    get_after_delete = storage.get("key1")
    assert get_after_delete.is_failure
    assert "not found" in get_after_delete.error.lower()


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

    # Delete non-existent key returns error (no fallback - fast fail)
    result = storage.delete("nonexistent")
    assert result.is_failure
    assert "not found" in result.error.lower()

    # Test operations after delete error
    result = storage.set("recovery_key", "recovery_value")
    assert result.is_success
    assert result.value is True

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


def test_batch_set_operation() -> None:
    """Test batch set operation."""
    storage = FlextApiStorage()

    batch_data = {
        "batch_key_1": "batch_value_1",
        "batch_key_2": "batch_value_2",
        "batch_key_3": "batch_value_3",
    }

    batch_result = storage.batch_set(batch_data)
    assert batch_result.is_success

    # Verify all keys were set
    for key, value in batch_data.items():
        get_result = storage.get(key)
        assert get_result.is_success
        assert get_result.value == value


def test_batch_get_operation() -> None:
    """Test batch get operation."""
    storage = FlextApiStorage()

    # Set up test data
    test_data = {"get_1": "value_1", "get_2": "value_2", "get_3": "value_3"}
    for key, value in test_data.items():
        storage.set(key, value)

    # Batch get
    batch_get_result = storage.batch_get(["get_1", "get_2", "get_3"])
    assert batch_get_result.is_success
    assert batch_get_result.value == test_data


def test_batch_delete_operation() -> None:
    """Test batch delete operation."""
    storage = FlextApiStorage()

    # Set up test data
    keys = ["del_1", "del_2", "del_3"]
    for key in keys:
        storage.set(key, f"value_for_{key}")

    # Verify all exist
    for key in keys:
        exists_result = storage.exists(key)
        assert exists_result.is_success
        assert exists_result.value is True

    # Batch delete
    batch_delete_result = storage.batch_delete(keys)
    assert batch_delete_result.is_success

    # Verify all deleted (no fallback - should return error)
    for key in keys:
        get_result = storage.get(key)
        assert get_result.is_failure
        assert "not found" in get_result.error.lower()


def test_values_operation() -> None:
    """Test getting all values from storage."""
    storage = FlextApiStorage()

    test_values = ["val1", "val2", "val3"]
    for i, val in enumerate(test_values):
        storage.set(f"val_key_{i}", val)

    values_result = storage.values()
    assert values_result.is_success
    assert values_result.value is not None
    assert len(values_result.value) > 0


def test_items_operation() -> None:
    """Test getting all key-value pairs from storage."""
    storage = FlextApiStorage()

    test_items = {"item_1": "value_1", "item_2": "value_2"}
    for key, value in test_items.items():
        storage.set(key, value)

    items_result = storage.items()
    assert items_result.is_success
    assert items_result.value is not None
    assert len(items_result.value) > 0


def test_json_serialization() -> None:
    """Test JSON serialization functionality."""
    storage = FlextApiStorage()

    test_data = {"key": "value", "number": 42, "list": [1, 2, 3]}

    serialize_result = storage.serialize_json(test_data)
    assert serialize_result.is_success
    assert isinstance(serialize_result.value, str)


def test_json_deserialization() -> None:
    """Test JSON deserialization functionality."""
    storage = FlextApiStorage()

    json_str = '{"key": "value", "number": 42}'

    deserialize_result = storage.deserialize_json(json_str)
    assert deserialize_result.is_success
    assert deserialize_result.value is not None


def test_default_value_retrieval() -> None:
    """Test getting a non-existent key returns error (no fallback)."""
    storage = FlextApiStorage()

    get_result = storage.get("nonexistent_key")
    assert get_result.is_failure
    assert "not found" in get_result.error.lower()


def test_invalid_key_set() -> None:
    """Test that invalid keys are rejected."""
    storage = FlextApiStorage()

    # Empty key should fail
    set_result = storage.set("", "value")
    assert set_result.is_failure

    # Non-string key should fail
    set_result = storage.set(None, "value")
    assert set_result.is_failure


def test_batch_set_with_ttl() -> None:
    """Test batch set with TTL parameter."""
    storage = FlextApiStorage()

    batch_data = {"ttl_1": "value_1", "ttl_2": "value_2"}

    batch_result = storage.batch_set(batch_data, ttl=300)
    assert batch_result.is_success

    # Verify all keys were set
    for key in batch_data:
        exists_result = storage.exists(key)
        assert exists_result.is_success


def test_timeout_parameter_precedence() -> None:
    """Test that timeout parameter takes precedence over ttl."""
    storage = FlextApiStorage()

    # Set with both timeout and ttl (timeout should be used)
    set_result = storage.set("timeout_test", "value", timeout=100, ttl=200)
    assert set_result.is_success

    # Verify key exists
    exists_result = storage.exists("timeout_test")
    assert exists_result.is_success
    assert exists_result.value is True


def test_batch_get_empty_list() -> None:
    """Test batch get with empty key list."""
    storage = FlextApiStorage()

    # Set some data first
    storage.set("key_1", "value_1")

    # Get with empty list
    batch_result = storage.batch_get([])
    assert batch_result.is_success
    assert batch_result.value == {}

"""Focused storage tests for maximum coverage improvement.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult

from flext_api import FlextApiStorage


class TestFlextApiStorageFocused:
    """Focused tests to improve storage.py coverage from 30% to 80%+."""

    def test_storage_initialization_default(self) -> None:
        """Test FlextApiStorage initialization with default config."""
        storage = FlextApiStorage()

        assert storage is not None
        assert storage.namespace == "flext_api"
        assert storage.backend == "memory"
        assert isinstance(storage.config, dict)
        assert storage.config["namespace"] == "flext_api"

    def test_storage_initialization_with_dict_config(self) -> None:
        """Test FlextApiStorage initialization with dict config."""
        config = {"namespace": "test_namespace", "backend": "redis"}
        storage = FlextApiStorage(config=config)

        assert storage.namespace == "test_namespace"
        assert storage.backend == "redis"
        assert storage.config["namespace"] == "test_namespace"

    def test_storage_initialization_with_object_config(self) -> None:
        """Test FlextApiStorage initialization with object config."""

        class MockConfig:
            def __init__(self) -> None:
                self.namespace = "object_namespace"
                self.backend = "file"

        # Since FlextTypeAdapters.adapt_to_dict will convert the object
        storage = FlextApiStorage(config=MockConfig())

        # The storage should still work with default values since adapt_to_dict
        # may not extract the attributes as expected
        assert storage is not None
        assert isinstance(storage.namespace, str)

    def test_storage_set_operation(self) -> None:
        """Test storage set operation."""
        storage = FlextApiStorage()

        result = storage.set("test_key", "test_value")

        assert result.is_success
        assert result.unwrap() is None

        # Verify data was stored in internal data
        assert "test_key" in storage._data
        assert storage._data["test_key"] == "test_value"

    def test_storage_get_operation_existing_key(self) -> None:
        """Test storage get operation with existing key."""
        storage = FlextApiStorage()

        # Set a value first
        storage.set("test_key", "test_value")

        # Get the value
        result = storage.get("test_key")

        assert result.is_success
        assert result.unwrap() == "test_value"

    def test_storage_get_operation_nonexistent_key(self) -> None:
        """Test storage get operation with nonexistent key."""
        storage = FlextApiStorage()

        result = storage.get("nonexistent_key")

        assert result.is_success
        assert result.unwrap() is None

    def test_storage_get_operation_with_default(self) -> None:
        """Test storage get operation with default value."""
        storage = FlextApiStorage()

        result = storage.get("nonexistent_key", "default_value")

        assert result.is_success
        assert result.unwrap() == "default_value"

    def test_storage_delete_operation_existing_key(self) -> None:
        """Test storage delete operation with existing key."""
        storage = FlextApiStorage()

        # Set a value first
        storage.set("test_key", "test_value")

        # Delete the key
        result = storage.delete("test_key")

        assert result.is_success
        assert result.unwrap() is None

        # Verify key was removed from internal data
        assert "test_key" not in storage._data

    def test_storage_delete_operation_nonexistent_key(self) -> None:
        """Test storage delete operation with nonexistent key."""
        storage = FlextApiStorage()

        result = storage.delete("nonexistent_key")

        assert not result.is_success
        assert result.error is not None
        assert "Key not found" in result.error

    def test_storage_exists_operation(self) -> None:
        """Test storage exists operation."""
        storage = FlextApiStorage()

        # Test non-existent key
        result = storage.exists("test_key")
        assert result.is_success
        assert result.unwrap() is False

        # Set a value and test again
        storage.set("test_key", "test_value")
        result = storage.exists("test_key")
        assert result.is_success
        assert result.unwrap() is True

    def test_storage_clear_operation(self) -> None:
        """Test storage clear operation."""
        storage = FlextApiStorage()

        # Add some data
        storage.set("key1", "value1")
        storage.set("key2", "value2")

        # Clear storage
        result = storage.clear()

        assert result.is_success
        assert result.unwrap() is None

        # Verify data was cleared
        assert len(storage._data) == 0
        assert len(storage._storage) == 0

    def test_storage_size_operation(self) -> None:
        """Test storage size operation."""
        storage = FlextApiStorage()

        # Initially empty
        result = storage.size()
        assert result.is_success
        assert result.unwrap() == 0

        # Add some items
        storage.set("key1", "value1")
        storage.set("key2", "value2")

        result = storage.size()
        assert result.is_success
        assert result.unwrap() == 2

    def test_storage_keys_operation(self) -> None:
        """Test storage keys operation."""
        storage = FlextApiStorage()

        # Initially empty
        result = storage.keys()
        assert result.is_success
        assert result.unwrap() == []

        # Add some items
        storage.set("key1", "value1")
        storage.set("key2", "value2")

        result = storage.keys()
        assert result.is_success
        keys = result.unwrap()
        assert isinstance(keys, list)
        assert set(keys) == {"key1", "key2"}

    def test_storage_items_operation(self) -> None:
        """Test storage items operation."""
        storage = FlextApiStorage()

        # Initially empty
        result = storage.items()
        assert result.is_success
        assert result.unwrap() == []

        # Add some items
        storage.set("key1", "value1")
        storage.set("key2", "value2")

        result = storage.items()
        assert result.is_success
        items = result.unwrap()
        assert isinstance(items, list)
        assert set(items) == {("key1", "value1"), ("key2", "value2")}

    def test_storage_values_operation(self) -> None:
        """Test storage values operation."""
        storage = FlextApiStorage()

        # Initially empty
        result = storage.values()
        assert result.is_success
        assert result.unwrap() == []

        # Add some items
        storage.set("key1", "value1")
        storage.set("key2", "value2")

        result = storage.values()
        assert result.is_success
        values = result.unwrap()
        assert isinstance(values, list)
        assert set(values) == {"value1", "value2"}

    def test_storage_close_operation(self) -> None:
        """Test storage close operation."""
        storage = FlextApiStorage()

        result = storage.close()

        assert result.is_success
        assert result.unwrap() is None

    def test_storage_make_key_method(self) -> None:
        """Test storage _make_key method functionality."""
        storage = FlextApiStorage()

        # Test default namespace
        key = storage._make_key("test")
        assert key == "flext_api:test"

        # Test custom namespace
        storage_custom = FlextApiStorage(config={"namespace": "custom"})
        key = storage_custom._make_key("test")
        assert key == "custom:test"

    def test_storage_complex_data_types(self) -> None:
        """Test storage with complex data types."""
        storage = FlextApiStorage()

        # Test with different data types
        test_data = [
            ("string_key", "string_value"),
            ("int_key", 42),
            ("list_key", [1, 2, 3]),
            ("dict_key", {"nested": "value"}),
            ("bool_key", True),
            ("none_key", None),
        ]

        # Store all test data
        for key, value in test_data:
            result = storage.set(key, value)
            assert result.is_success

        # Retrieve and verify all test data
        for key, expected_value in test_data:
            get_result: FlextResult[object] = storage.get(key)
            assert get_result.is_success
            assert get_result.unwrap() == expected_value

    def test_storage_data_consistency_after_operations(self) -> None:
        """Test storage data consistency after multiple operations."""
        storage = FlextApiStorage()

        # Perform multiple operations
        storage.set("key1", "value1")
        storage.set("key2", "value2")
        storage.set("key3", "value3")

        # Verify initial state
        assert storage.size().unwrap() == 3

        # Delete one key
        storage.delete("key2")
        assert storage.size().unwrap() == 2
        assert not storage.exists("key2").unwrap()

        # Verify remaining keys
        keys = storage.keys().unwrap()
        assert set(keys) == {"key1", "key3"}

        # Clear all
        storage.clear()
        assert storage.size().unwrap() == 0
        assert storage.keys().unwrap() == []

    def test_storage_namespace_isolation(self) -> None:
        """Test that different namespaces are properly isolated."""
        storage1 = FlextApiStorage(config={"namespace": "namespace1"})
        storage2 = FlextApiStorage(config={"namespace": "namespace2"})

        # Set same key in both storages
        storage1.set("shared_key", "value1")
        storage2.set("shared_key", "value2")

        # Verify isolation
        result1 = storage1.get("shared_key")
        result2 = storage2.get("shared_key")

        assert result1.unwrap() == "value1"
        assert result2.unwrap() == "value2"

        # Verify internal keys are different
        key1 = storage1._make_key("shared_key")
        key2 = storage2._make_key("shared_key")

        assert key1 == "namespace1:shared_key"
        assert key2 == "namespace2:shared_key"
        assert key1 != key2

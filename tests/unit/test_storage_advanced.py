"""Advanced tests for FlextApiStorage to improve coverage.

Tests for storage functionality, different backends, and edge cases.
Focuses on storage operations, configuration, and error handling.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsMatchers
from pydantic import BaseModel

from flext_api import FlextApiStorage


class StorageConfig(BaseModel):
    """Test storage configuration model."""

    backend: str = "memory"
    namespace: str = "test"
    enable_caching: bool = True
    cache_ttl_seconds: int = 600


class TestFlextApiStorageAdvanced:
    """Advanced tests for FlextApiStorage to improve coverage."""

    def test_storage_init_with_dict_config(self) -> None:
        """Test storage initialization with dict configuration."""
        config = {
            "backend": "memory",
            "namespace": "test_namespace",
            "enable_caching": True,
            "cache_ttl_seconds": 300
        }

        storage = FlextApiStorage(config)
        assert storage.backend == "memory"
        assert storage.namespace == "test_namespace"
        assert storage._cache_enabled is True
        assert storage._cache_ttl == 300

    def test_storage_init_with_model_config(self) -> None:
        """Test storage initialization with Pydantic model configuration."""
        config = StorageConfig(
            backend="file",
            namespace="model_namespace",
            enable_caching=False,
            cache_ttl_seconds=900
        )

        storage = FlextApiStorage(config)
        assert storage.backend == "file"
        assert storage.namespace == "model_namespace"
        assert storage._cache_enabled is False
        assert storage._cache_ttl == 900

    def test_storage_init_with_none_config(self) -> None:
        """Test storage initialization with None configuration."""
        storage = FlextApiStorage(None)
        assert storage.backend == "memory"  # default
        assert storage.namespace == "default"  # default
        assert storage._cache_enabled is False  # default
        assert storage._cache_ttl == 300  # default

    def test_storage_set_basic(self) -> None:
        """Test basic set operation."""
        storage = FlextApiStorage()

        result = storage.set("key1", "value1")
        FlextTestsMatchers.assert_result_success(result)

        # Verify data was stored
        assert "key1" in storage._data
        assert storage._data["key1"] == "value1"

    def test_storage_set_different_types(self) -> None:
        """Test set operation with different data types."""
        storage = FlextApiStorage()

        test_data = [
            ("string", "hello world"),
            ("number", 42),
            ("float", 3.14),
            ("boolean", True),
            ("list", [1, 2, 3]),
            ("dict", {"nested": "value"}),
            ("none", None),
        ]

        for key, value in test_data:
            result = storage.set(key, value)
            FlextTestsMatchers.assert_result_success(result)
            assert storage._data[key] == value

    def test_storage_set_overwrite(self) -> None:
        """Test set operation overwrites existing values."""
        storage = FlextApiStorage()

        # Set initial value
        result1 = storage.set("key", "initial")
        FlextTestsMatchers.assert_result_success(result1)
        assert storage._data["key"] == "initial"

        # Overwrite with new value
        result2 = storage.set("key", "overwritten")
        FlextTestsMatchers.assert_result_success(result2)
        assert storage._data["key"] == "overwritten"

    def test_storage_get_existing(self) -> None:
        """Test get operation for existing keys."""
        storage = FlextApiStorage()
        storage.set("key1", "value1")
        storage.set("key2", 42)

        result1 = storage.get("key1")
        FlextTestsMatchers.assert_result_success(result1)
        assert result1.value == "value1"

        result2 = storage.get("key2")
        FlextTestsMatchers.assert_result_success(result2)
        assert result2.value == 42

    def test_storage_get_nonexistent(self) -> None:
        """Test get operation for non-existent keys."""
        storage = FlextApiStorage()

        result = storage.get("nonexistent")
        FlextTestsMatchers.assert_result_failure(result)
        assert "Key not found" in result.error

    def test_storage_get_with_default(self) -> None:
        """Test get operation with default value."""
        storage = FlextApiStorage()

        result = storage.get("nonexistent", default="default_value")
        FlextTestsMatchers.assert_result_success(result)
        assert result.value == "default_value"

    def test_storage_delete_existing(self) -> None:
        """Test delete operation for existing keys."""
        storage = FlextApiStorage()
        storage.set("key1", "value1")
        storage.set("key2", "value2")

        # Verify keys exist
        assert "key1" in storage._data
        assert "key2" in storage._data

        # Delete one key
        result = storage.delete("key1")
        FlextTestsMatchers.assert_result_success(result)

        # Verify deletion
        assert "key1" not in storage._data
        assert "key2" in storage._data

    def test_storage_delete_nonexistent(self) -> None:
        """Test delete operation for non-existent keys."""
        storage = FlextApiStorage()

        result = storage.delete("nonexistent")
        FlextTestsMatchers.assert_result_failure(result)
        assert "Key not found" in result.error

    def test_storage_exists(self) -> None:
        """Test exists operation."""
        storage = FlextApiStorage()
        storage.set("key1", "value1")

        # Test existing key
        result1 = storage.exists("key1")
        FlextTestsMatchers.assert_result_success(result1)
        assert result1.value is True

        # Test non-existent key
        result2 = storage.exists("nonexistent")
        FlextTestsMatchers.assert_result_success(result2)
        assert result2.value is False

    def test_storage_keys(self) -> None:
        """Test keys operation."""
        storage = FlextApiStorage()

        # Empty storage
        result1 = storage.keys()
        FlextTestsMatchers.assert_result_success(result1)
        assert result1.value == []

        # Add some keys
        storage.set("key1", "value1")
        storage.set("key2", "value2")
        storage.set("key3", "value3")

        result2 = storage.keys()
        FlextTestsMatchers.assert_result_success(result2)
        keys = result2.value
        assert len(keys) == 3
        assert "key1" in keys
        assert "key2" in keys
        assert "key3" in keys

    def test_storage_values(self) -> None:
        """Test values operation."""
        storage = FlextApiStorage()

        # Empty storage
        result1 = storage.values()
        FlextTestsMatchers.assert_result_success(result1)
        assert result1.value == []

        # Add some values
        storage.set("key1", "value1")
        storage.set("key2", 42)
        storage.set("key3", [1, 2, 3])

        result2 = storage.values()
        FlextTestsMatchers.assert_result_success(result2)
        values = result2.value
        assert len(values) == 3
        assert "value1" in values
        assert 42 in values
        assert [1, 2, 3] in values

    def test_storage_items(self) -> None:
        """Test items operation."""
        storage = FlextApiStorage()

        # Empty storage
        result1 = storage.items()
        FlextTestsMatchers.assert_result_success(result1)
        assert result1.value == []

        # Add some items
        storage.set("key1", "value1")
        storage.set("key2", 42)

        result2 = storage.items()
        FlextTestsMatchers.assert_result_success(result2)
        items = result2.value
        assert len(items) == 2
        assert ("key1", "value1") in items
        assert ("key2", 42) in items

    def test_storage_clear(self) -> None:
        """Test clear operation."""
        storage = FlextApiStorage()

        # Add some data
        storage.set("key1", "value1")
        storage.set("key2", "value2")
        assert len(storage._data) == 2

        # Clear storage
        result = storage.clear()
        FlextTestsMatchers.assert_result_success(result)
        assert len(storage._data) == 0

    def test_storage_size(self) -> None:
        """Test size operation."""
        storage = FlextApiStorage()

        # Empty storage
        result1 = storage.size()
        FlextTestsMatchers.assert_result_success(result1)
        assert result1.value == 0

        # Add some data
        storage.set("key1", "value1")
        storage.set("key2", "value2")

        result2 = storage.size()
        FlextTestsMatchers.assert_result_success(result2)
        assert result2.value == 2

    def test_storage_configuration_access(self) -> None:
        """Test storage configuration properties."""
        config = {
            "backend": "redis",
            "namespace": "production",
            "enable_caching": True,
            "cache_ttl_seconds": 1200
        }

        storage = FlextApiStorage(config)

        assert storage.backend == "redis"
        assert storage.namespace == "production"
        assert storage._cache_enabled is True
        assert storage._cache_ttl == 1200

    def test_storage_edge_cases(self) -> None:
        """Test storage edge cases."""
        storage = FlextApiStorage()

        # Test with empty string key
        result1 = storage.set("", "empty_key_value")
        FlextTestsMatchers.assert_result_success(result1)

        result2 = storage.get("")
        FlextTestsMatchers.assert_result_success(result2)
        assert result2.value == "empty_key_value"

        # Test with special characters in key
        special_key = "key-with-special_chars.123"
        result3 = storage.set(special_key, "special_value")
        FlextTestsMatchers.assert_result_success(result3)

        result4 = storage.get(special_key)
        FlextTestsMatchers.assert_result_success(result4)
        assert result4.value == "special_value"

    def test_storage_large_data(self) -> None:
        """Test storage with large data structures."""
        storage = FlextApiStorage()

        # Large list
        large_list = list(range(1000))
        result1 = storage.set("large_list", large_list)
        FlextTestsMatchers.assert_result_success(result1)

        result2 = storage.get("large_list")
        FlextTestsMatchers.assert_result_success(result2)
        assert result2.value == large_list

        # Large dict
        large_dict = {f"key_{i}": f"value_{i}" for i in range(100)}
        result3 = storage.set("large_dict", large_dict)
        FlextTestsMatchers.assert_result_success(result3)

        result4 = storage.get("large_dict")
        FlextTestsMatchers.assert_result_success(result4)
        assert result4.value == large_dict

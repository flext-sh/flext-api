"""Tests for flext_api.storage module - REAL classes only.

Tests using only REAL classes:
- FlextApiStorage

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time

from flext_api import FlextApiStorage
from tests.conftest import assert_flext_result_failure, assert_flext_result_success


class TestFlextAPIStorage:
    """Test FlextApiStorage REAL class functionality."""

    def test_storage_creation_basic(self) -> None:
        """Test basic storage creation."""
        storage = FlextApiStorage()

        assert storage.storage_name == "FlextApiStorage"
        assert storage.default_ttl > 0
        assert storage.max_size > 0

    def test_storage_creation_custom(self) -> None:
        """Test storage creation with custom parameters."""
        storage = FlextApiStorage(
            storage_name="CustomStorage", default_ttl=600, max_size=500
        )

        assert storage.storage_name == "CustomStorage"
        assert storage.default_ttl == 600
        assert storage.max_size == 500

    def test_storage_execute_method(self) -> None:
        """Test storage execute method (required by FlextDomainService)."""
        storage = FlextApiStorage(max_size=100, default_ttl=300)

        result = storage.execute()
        assert_flext_result_success(result)

        data = result.value
        assert isinstance(data, dict)
        assert data["service"] == "FlextApiStorage"
        assert data["max_size"] == 100
        assert data["default_ttl"] == 300
        assert "cache_size" in data

    def test_set_and_get_success(self) -> None:
        """Test successful set and get operations."""
        storage = FlextApiStorage()

        # Set a value
        set_result = storage.set("test_key", {"data": "test_value"})
        assert_flext_result_success(set_result)

        # Get the value
        get_result = storage.get("test_key")
        assert_flext_result_success(get_result)

        assert get_result.value == {"data": "test_value"}

    def test_set_empty_key_failure(self) -> None:
        """Test set with empty key fails."""
        storage = FlextApiStorage()

        result = storage.set("", "value")
        assert_flext_result_failure(result, "Key cannot be empty")

    def test_get_empty_key_failure(self) -> None:
        """Test get with empty key fails."""
        storage = FlextApiStorage()

        result = storage.get("")
        assert_flext_result_failure(result, "Key cannot be empty")

    def test_get_nonexistent_key_failure(self) -> None:
        """Test get with non-existent key fails."""
        storage = FlextApiStorage()

        result = storage.get("nonexistent")
        assert_flext_result_failure(result, "Key not found")

    def test_delete_success(self) -> None:
        """Test successful delete operation."""
        storage = FlextApiStorage()

        # Set a value first
        storage.set("delete_key", "delete_value")

        # Delete it
        delete_result = storage.delete("delete_key")
        assert_flext_result_success(delete_result)

        # Verify it's gone
        get_result = storage.get("delete_key")
        assert_flext_result_failure(get_result, "Key not found")

    def test_delete_empty_key_failure(self) -> None:
        """Test delete with empty key fails."""
        storage = FlextApiStorage()

        result = storage.delete("")
        assert_flext_result_failure(result, "Key cannot be empty")

    def test_delete_nonexistent_key_failure(self) -> None:
        """Test delete with non-existent key fails."""
        storage = FlextApiStorage()

        result = storage.delete("nonexistent")
        assert_flext_result_failure(result, "Key not found")

    def test_clear_cache(self) -> None:
        """Test clearing the cache."""
        storage = FlextApiStorage()

        # Add some values
        storage.set("key1", "value1")
        storage.set("key2", "value2")

        # Clear cache
        clear_result = storage.clear()
        assert_flext_result_success(clear_result)

        # Verify cache is empty
        size_result = storage.size()
        assert_flext_result_success(size_result)
        assert size_result.value == 0

    def test_keys_operation(self) -> None:
        """Test getting all keys."""
        storage = FlextApiStorage()

        # Initially empty
        keys_result = storage.keys()
        assert_flext_result_success(keys_result)
        assert keys_result.value == []

        # Add some values
        storage.set("key1", "value1")
        storage.set("key2", "value2")

        # Get keys
        keys_result = storage.keys()
        assert_flext_result_success(keys_result)

        keys = keys_result.value
        assert isinstance(keys, list)
        assert len(keys) == 2
        assert "key1" in keys
        assert "key2" in keys

    def test_size_operation(self) -> None:
        """Test getting cache size."""
        storage = FlextApiStorage()

        # Initially empty
        size_result = storage.size()
        assert_flext_result_success(size_result)
        assert size_result.value == 0

        # Add values
        storage.set("key1", "value1")
        storage.set("key2", "value2")

        # Check size
        size_result = storage.size()
        assert_flext_result_success(size_result)
        assert size_result.value == 2

    def test_ttl_functionality(self) -> None:
        """Test TTL (time-to-live) functionality."""
        storage = FlextApiStorage()

        # Set with very short TTL
        set_result = storage.set("ttl_key", "ttl_value", ttl=1)
        assert_flext_result_success(set_result)

        # Should be available immediately
        get_result = storage.get("ttl_key")
        assert_flext_result_success(get_result)

        # Wait for expiry
        time.sleep(1.1)

        # Should be expired
        get_result = storage.get("ttl_key")
        assert_flext_result_failure(get_result, "Key expired")

    def test_max_size_limit(self) -> None:
        """Test cache size limit enforcement."""
        storage = FlextApiStorage(max_size=2)

        # Fill to capacity
        assert_flext_result_success(storage.set("key1", "value1"))
        assert_flext_result_success(storage.set("key2", "value2"))

        # Should fail to add more
        result = storage.set("key3", "value3")
        assert_flext_result_failure(result, "Cache size limit reached")

    def test_serialize_data(self) -> None:
        """Test data serialization."""
        storage = FlextApiStorage()

        test_data = {"name": "test", "value": 123, "active": True}

        result = storage.serialize_data(test_data)
        assert_flext_result_success(result)

        json_str = result.value
        assert isinstance(json_str, str)
        assert '"name":"test"' in json_str
        assert '"value":123' in json_str
        assert '"active":true' in json_str

    def test_deserialize_data(self) -> None:
        """Test data deserialization."""
        storage = FlextApiStorage()

        json_str = '{"name":"test","value":123,"active":true}'

        result = storage.deserialize_data(json_str)
        assert_flext_result_success(result)

        data = result.value
        assert isinstance(data, dict)
        assert data["name"] == "test"
        assert data["value"] == 123
        assert data["active"] is True

    def test_deserialize_empty_string_failure(self) -> None:
        """Test deserialization with empty string fails."""
        storage = FlextApiStorage()

        result = storage.deserialize_data("")
        assert_flext_result_failure(result, "JSON string cannot be empty")

    def test_deserialize_invalid_json_failure(self) -> None:
        """Test deserialization with invalid JSON fails."""
        storage = FlextApiStorage()

        result = storage.deserialize_data("{invalid json}")
        assert_flext_result_failure(result, "Failed to deserialize")

    def test_storage_type_validation(self) -> None:
        """Test storage is proper type."""
        storage = FlextApiStorage()

        # Should be instance of FlextApiStorage
        assert isinstance(storage, FlextApiStorage)

        # Should have expected type name
        assert type(storage).__name__ == "FlextApiStorage"

    def test_storage_multiple_instances_independence(self) -> None:
        """Test multiple storage instances are independent."""
        storage1 = FlextApiStorage(storage_name="Storage1")
        storage2 = FlextApiStorage(storage_name="Storage2")

        assert storage1 is not storage2
        assert storage1.storage_name != storage2.storage_name

        # Set in storage1
        storage1.set("key", "value1")

        # Should not exist in storage2
        result = storage2.get("key")
        assert_flext_result_failure(result, "Key not found")

    def test_storage_string_representation(self) -> None:
        """Test storage has string representation."""
        storage = FlextApiStorage()

        # Should be convertible to string
        storage_str = str(storage)
        assert isinstance(storage_str, str)
        assert len(storage_str) > 0

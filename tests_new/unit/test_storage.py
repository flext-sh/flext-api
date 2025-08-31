"""Tests for flext_api.storage module - REAL classes only.

Tests using only REAL classes:
- FlextApiStorage

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api import FlextApiStorage


class TestFlextApiStorage:
    """Test FlextApiStorage REAL class functionality."""

    def test_storage_creation_defaults(self) -> None:
        """Test FlextApiStorage creation with defaults."""
        storage = FlextApiStorage()

        assert storage.storage_name == "FlextApiStorage"
        assert storage.default_ttl > 0
        assert storage.max_size > 0

    def test_storage_creation_custom(self) -> None:
        """Test FlextApiStorage creation with custom values."""
        storage = FlextApiStorage(
            storage_name="TestStorage",
            default_ttl=600,
            max_size=50
        )

        assert storage.storage_name == "TestStorage"
        assert storage.default_ttl == 600
        assert storage.max_size == 50

    def test_storage_execute(self) -> None:
        """Test storage execute method."""
        storage = FlextApiStorage(storage_name="TestStorage", max_size=100)

        result = storage.execute()
        assert result.success

        data = result.data
        assert data["service"] == "TestStorage"
        assert data["max_size"] == 100
        assert "cache_size" in data
        assert "default_ttl" in data

    def test_storage_set_get(self) -> None:
        """Test basic storage set and get operations."""
        storage = FlextApiStorage()

        # Set a value
        set_result = storage.set("test_key", {"name": "Test Value"})
        assert set_result.success

        # Get the value
        get_result = storage.get("test_key")
        assert get_result.success
        assert get_result.data["name"] == "Test Value"

    def test_storage_set_with_ttl(self) -> None:
        """Test storage set with TTL."""
        storage = FlextApiStorage()

        # Set with specific TTL
        set_result = storage.set("ttl_key", "ttl_value", ttl=300)
        assert set_result.success

        # Should be able to get it immediately
        get_result = storage.get("ttl_key")
        assert get_result.success
        assert get_result.data == "ttl_value"

    def test_storage_get_nonexistent_key(self) -> None:
        """Test getting non-existent key."""
        storage = FlextApiStorage()

        result = storage.get("nonexistent_key")
        assert not result.success
        assert "not found" in result.error.lower()

    def test_storage_set_empty_key(self) -> None:
        """Test setting empty key fails."""
        storage = FlextApiStorage()

        result = storage.set("", "some_value")
        assert not result.success
        assert "empty" in result.error.lower()

    def test_storage_get_empty_key(self) -> None:
        """Test getting empty key fails."""
        storage = FlextApiStorage()

        result = storage.get("")
        assert not result.success
        assert "empty" in result.error.lower()

    def test_storage_delete(self) -> None:
        """Test storage delete operation."""
        storage = FlextApiStorage()

        # Set a value first
        storage.set("delete_key", "delete_value")

        # Delete it
        delete_result = storage.delete("delete_key")
        assert delete_result.success

        # Should not be able to get it anymore
        get_result = storage.get("delete_key")
        assert not get_result.success

    def test_storage_delete_nonexistent_key(self) -> None:
        """Test deleting non-existent key."""
        storage = FlextApiStorage()

        result = storage.delete("nonexistent_key")
        assert not result.success
        assert "not found" in result.error.lower()

    def test_storage_delete_empty_key(self) -> None:
        """Test deleting empty key fails."""
        storage = FlextApiStorage()

        result = storage.delete("")
        assert not result.success
        assert "empty" in result.error.lower()

    def test_storage_clear(self) -> None:
        """Test storage clear operation."""
        storage = FlextApiStorage()

        # Set multiple values
        storage.set("key1", "value1")
        storage.set("key2", "value2")
        storage.set("key3", "value3")

        # Clear all
        clear_result = storage.clear()
        assert clear_result.success

        # All keys should be gone
        assert not storage.get("key1").success
        assert not storage.get("key2").success
        assert not storage.get("key3").success

    def test_storage_keys(self) -> None:
        """Test storage keys operation."""
        storage = FlextApiStorage()

        # Set some values
        storage.set("key1", "value1")
        storage.set("key2", "value2")

        # Get keys
        keys_result = storage.keys()
        assert keys_result.success

        keys_list = keys_result.data
        assert "key1" in keys_list
        assert "key2" in keys_list
        assert len(keys_list) == 2

    def test_storage_size(self) -> None:
        """Test storage size operation."""
        storage = FlextApiStorage()

        # Initially should be empty
        size_result = storage.size()
        assert size_result.success
        assert size_result.data == 0

        # Add some values
        storage.set("key1", "value1")
        storage.set("key2", "value2")

        # Size should increase
        size_result = storage.size()
        assert size_result.success
        assert size_result.data == 2

    def test_storage_max_size_limit(self) -> None:
        """Test storage max size limit."""
        storage = FlextApiStorage(max_size=2)

        # Fill to capacity
        assert storage.set("key1", "value1").success
        assert storage.set("key2", "value2").success

        # Exceeding capacity should fail
        result = storage.set("key3", "value3")
        assert not result.success
        assert "limit" in result.error.lower()

    def test_storage_serialize_data(self) -> None:
        """Test data serialization."""
        storage = FlextApiStorage()

        data = {"name": "Test", "value": 123}
        result = storage.serialize_data(data)

        assert result.success
        json_str = result.data
        assert isinstance(json_str, str)
        assert "Test" in json_str
        assert "123" in json_str

    def test_storage_deserialize_data(self) -> None:
        """Test data deserialization."""
        storage = FlextApiStorage()

        json_str = '{"name":"Test","value":123}'
        result = storage.deserialize_data(json_str)

        assert result.success
        data = result.data
        assert data["name"] == "Test"
        assert data["value"] == 123

    def test_storage_serialize_deserialize_roundtrip(self) -> None:
        """Test serialize/deserialize roundtrip."""
        storage = FlextApiStorage()

        original_data = {"name": "Test", "items": [1, 2, 3], "active": True}

        # Serialize
        serialize_result = storage.serialize_data(original_data)
        assert serialize_result.success

        # Deserialize
        deserialize_result = storage.deserialize_data(serialize_result.data)
        assert deserialize_result.success

        # Should match original
        restored_data = deserialize_result.data
        assert restored_data["name"] == original_data["name"]
        assert restored_data["items"] == original_data["items"]
        assert restored_data["active"] == original_data["active"]

    def test_storage_deserialize_empty_string(self) -> None:
        """Test deserializing empty string fails."""
        storage = FlextApiStorage()

        result = storage.deserialize_data("")
        assert not result.success
        assert "empty" in result.error.lower()

    def test_storage_deserialize_invalid_json(self) -> None:
        """Test deserializing invalid JSON fails."""
        storage = FlextApiStorage()

        result = storage.deserialize_data("invalid json")
        assert not result.success
        assert "deserialize" in result.error.lower()

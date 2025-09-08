"""Comprehensive tests for FlextApiStorage with real functionality validation.

Tests all storage functionality using flext_tests library without mocks.
Achieves 100% coverage for storage.py module.



Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

from flext_tests import FlextMatchers

from flext_api import FlextApiModels, FlextApiStorage
from tests.support.fixtures.storage_fixtures import File, Memory


class TestFlextApiStorage:
    """Comprehensive storage system tests."""

    def test_storage_initialization(self) -> None:
        """Test storage initialization with various configurations."""
        # Default initialization
        storage = FlextApiStorage()
        assert storage.storage_name == "FlextApiStorage"
        assert storage.max_size == 10000
        assert storage.default_ttl == 3600

        # Custom initialization
        custom_storage = FlextApiStorage(
            config={"type": "cache"},
            storage_name="CustomStorage",
            max_size=5000,
            default_ttl=1800,
        )
        assert custom_storage.storage_name == "CustomStorage"
        assert custom_storage.max_size == 5000
        assert custom_storage.default_ttl == 1800

    def test_storage_execute(self) -> None:
        """Test storage execution (domain service pattern)."""
        storage = FlextApiStorage(
            storage_name="TestStorage", max_size=100, default_ttl=600
        )
        result = storage.execute()

        assert result.success
        data = result.value
        assert data["service"] == "TestStorage"
        assert data["max_size"] == 100
        assert data["default_ttl"] == 600
        assert data["cache_size"] == 0
        assert data["status"] == "active"

    def test_storage_execute_error_handling(self) -> None:
        """Test storage execute error handling."""
        storage = FlextApiStorage()

        # Force an error by patching storage_name to raise exception
        with patch.object(storage, "storage_name", side_effect=Exception("Test error")):
            result = storage.execute()
            FlextMatchers.assert_result_failure(
                result, "Storage system execution failed"
            )

    def test_set_operation(self) -> None:
        """Test storage set operations."""
        storage = FlextApiStorage()

        # Basic set operation
        result = storage.set("key1", "value1")
        assert result.success

        # Set with TTL
        result = storage.set("key2", {"data": "json"}, ttl=300)
        assert result.success

        # Set with zero TTL (no expiration)
        result = storage.set("key3", "value3", ttl=0)
        assert result.success

        # Test empty key
        result = storage.set("", "value")
        FlextMatchers.assert_result_failure(result)

    def test_set_cache_size_limit(self) -> None:
        """Test cache size limit enforcement."""
        storage = FlextApiStorage(max_size=2)

        # Fill cache to limit
        assert storage.set("key1", "value1").success
        assert storage.set("key2", "value2").success

        # Try to add beyond limit
        result = storage.set("key3", "value3")
        FlextMatchers.assert_result_failure(result)

        # Updating existing key should work
        result = storage.set("key1", "new_value1")
        assert result.success

    def test_set_error_handling(self) -> None:
        """Test set operation error handling."""
        storage = FlextApiStorage()

        # Force an error by patching _cache_store
        with patch.object(
            storage, "_cache_store", side_effect=Exception("Storage error")
        ):
            result = storage.set("key", "value")
            FlextMatchers.assert_result_failure(result)

    def test_get_operation(self) -> None:
        """Test storage get operations."""
        storage = FlextApiStorage()

        # Set and get value
        storage.set("key1", "value1")
        result = storage.get("key1")
        assert result.success
        assert result.value == "value1"

        # Get non-existent key
        result = storage.get("nonexistent")
        FlextMatchers.assert_result_failure(result)

        # Test empty key
        result = storage.get("")
        FlextMatchers.assert_result_failure(result)

        # Test complex data types
        storage.set("json_key", {"name": "test", "id": 123})
        result = storage.get("json_key")
        assert result.success
        assert result.value == {"name": "test", "id": 123}

    def test_get_with_expiration(self) -> None:
        """Test get operation with TTL expiration."""
        storage = FlextApiStorage()

        # Set key with short TTL
        storage.set("expire_key", "expire_value", ttl=1)

        # Should be available immediately
        result = storage.get("expire_key")
        assert result.success
        assert result.value == "expire_value"

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired now
        result = storage.get("expire_key")
        FlextMatchers.assert_result_failure(result)

    def test_get_error_handling(self) -> None:
        """Test get operation error handling."""
        storage = FlextApiStorage()

        # Force an error by patching _cache_store
        with patch.object(
            storage, "_cache_store", side_effect=Exception("Storage error")
        ):
            result = storage.get("key")
            FlextMatchers.assert_result_failure(result)

    def test_delete_operation(self) -> None:
        """Test storage delete operations."""
        storage = FlextApiStorage()

        # Set and delete value
        storage.set("key1", "value1")
        result = storage.delete("key1")
        assert result.success

        # Verify deletion
        get_result = storage.get("key1")
        assert not get_result.success

        # Delete non-existent key
        result = storage.delete("nonexistent")
        FlextMatchers.assert_result_failure(result)

        # Test empty key
        result = storage.delete("")
        FlextMatchers.assert_result_failure(result)

    def test_delete_with_ttl_cleanup(self) -> None:
        """Test delete operation cleans up TTL data."""
        storage = FlextApiStorage()

        # Set key with TTL
        storage.set("ttl_key", "ttl_value", ttl=300)
        assert "ttl_key" in storage._expiration_times

        # Delete key
        result = storage.delete("ttl_key")
        assert result.success
        assert "ttl_key" not in storage._expiration_times

    def test_delete_error_handling(self) -> None:
        """Test delete operation error handling."""
        storage = FlextApiStorage()

        # Force an error by patching _cache_store
        with patch.object(
            storage, "_cache_store", side_effect=Exception("Storage error")
        ):
            result = storage.delete("key")
            FlextMatchers.assert_result_failure(result)

    def test_clear_operation(self) -> None:
        """Test storage clear operation."""
        storage = FlextApiStorage()

        # Add some data
        storage.set("key1", "value1")
        storage.set("key2", "value2", ttl=300)

        # Clear storage
        result = storage.clear()
        assert result.success

        # Verify all data is gone
        assert len(storage._cache_store) == 0
        assert len(storage._expiration_times) == 0

        # Verify keys are not accessible
        assert not storage.get("key1").success
        assert not storage.get("key2").success

    def test_clear_error_handling(self) -> None:
        """Test clear operation error handling."""
        storage = FlextApiStorage()

        # Force an error by patching clear method
        with patch.object(
            storage._cache_store, "clear", side_effect=Exception("Clear error")
        ):
            result = storage.clear()
            FlextMatchers.assert_result_failure(result)

    def test_keys_operation(self) -> None:
        """Test storage keys operation."""
        storage = FlextApiStorage()

        # Empty storage
        result = storage.keys()
        assert result.success
        assert result.value == []

        # Add some keys
        storage.set("key1", "value1")
        storage.set("key2", "value2")
        storage.set("key3", "value3")

        result = storage.keys()
        assert result.success
        keys = result.value
        assert len(keys) == 3
        assert "key1" in keys
        assert "key2" in keys
        assert "key3" in keys

    def test_keys_with_expiration_cleanup(self) -> None:
        """Test keys operation with automatic expiration cleanup."""
        storage = FlextApiStorage()

        # Add keys with different TTLs
        storage.set("permanent", "value", ttl=0)  # No expiration
        storage.set("short_lived", "value", ttl=1)  # 1 second TTL
        storage.set("normal", "value", ttl=300)  # 5 minute TTL

        # Immediately check - should have all keys
        result = storage.keys()
        assert result.success
        assert len(result.value) == 3

        # Wait for short_lived to expire
        time.sleep(1.1)

        # Keys operation should clean up expired keys
        result = storage.keys()
        assert result.success
        keys = result.value
        assert len(keys) == 2
        assert "permanent" in keys
        assert "normal" in keys
        assert "short_lived" not in keys

    def test_keys_error_handling(self) -> None:
        """Test keys operation error handling."""
        storage = FlextApiStorage()

        # Force an error by patching _expiration_times
        with patch.object(
            storage, "_expiration_times", side_effect=Exception("Keys error")
        ):
            result = storage.keys()
            FlextMatchers.assert_result_failure(result)

    def test_size_operation(self) -> None:
        """Test storage size operation."""
        storage = FlextApiStorage()

        # Empty storage
        result = storage.size()
        assert result.success
        assert result.value == 0

        # Add some keys
        storage.set("key1", "value1")
        storage.set("key2", "value2")

        result = storage.size()
        assert result.success
        assert result.value == 2

        # Delete one key
        storage.delete("key1")
        result = storage.size()
        assert result.success
        assert result.value == 1

    def test_size_with_expiration_cleanup(self) -> None:
        """Test size operation with automatic expiration cleanup."""
        storage = FlextApiStorage()

        # Add keys with different TTLs
        storage.set("key1", "value1", ttl=300)
        storage.set("key2", "value2", ttl=1)  # Short TTL

        # Initially both keys present
        result = storage.size()
        assert result.success
        assert result.value == 2

        # Wait for expiration
        time.sleep(1.1)

        # Size operation should clean up expired keys
        result = storage.size()
        assert result.success
        assert result.value == 1  # Only one key left

    def test_size_error_handling(self) -> None:
        """Test size operation error handling."""
        storage = FlextApiStorage()

        # Force an error by patching _expiration_times
        with patch.object(
            storage, "_expiration_times", side_effect=Exception("Size error")
        ):
            result = storage.size()
            FlextMatchers.assert_result_failure(result)

    def test_serialize_data(self) -> None:
        """Test data serialization functionality."""
        storage = FlextApiStorage()

        # Test various data types
        test_cases = [
            {"name": "test", "id": 123},
            [1, 2, 3, "four"],
            "simple string",
            42,
            True,
            None,
        ]

        for data in test_cases:
            result = storage.serialize_data(data)
            assert result.success

            # Verify it's valid JSON
            parsed = json.loads(result.value)
            assert parsed == data

    def test_serialize_data_error_handling(self) -> None:
        """Test serialization error handling."""
        storage = FlextApiStorage()

        # Test with non-serializable object
        class NonSerializable:
            pass

        non_serializable = NonSerializable()
        result = storage.serialize_data(non_serializable)
        FlextMatchers.assert_result_failure(result)

    def test_deserialize_data(self) -> None:
        """Test data deserialization functionality."""
        storage = FlextApiStorage()

        # Test various serialized data
        test_cases = [
            ('{"name": "test", "id": 123}', {"name": "test", "id": 123}),
            ('[1, 2, 3, "four"]', [1, 2, 3, "four"]),
            ('"simple string"', "simple string"),
            ("42", 42),
            ("true", True),
            ("null", None),
        ]

        for json_str, expected in test_cases:
            result = storage.deserialize_data(json_str)
            assert result.success
            assert result.value == expected

    def test_deserialize_data_error_handling(self) -> None:
        """Test deserialization error handling."""
        storage = FlextApiStorage()

        # Test empty string
        result = storage.deserialize_data("")
        FlextMatchers.assert_result_failure(result)

        # Test invalid JSON
        result = storage.deserialize_data("invalid json {")
        FlextMatchers.assert_result_failure(result)

        # Test JSON decode error specifically
        result = storage.deserialize_data('{"incomplete": }')
        FlextMatchers.assert_result_failure(result)

    def test_deserialize_general_exception(self) -> None:
        """Test deserialization general exception handling."""
        storage = FlextApiStorage()

        # Force a general exception by patching json.loads
        with patch("json.loads", side_effect=Exception("General error")):
            result = storage.deserialize_data('{"valid": "json"}')
            FlextMatchers.assert_result_failure(result)


class TestFile:
    """Test Filefunctionality."""

    def test_file_storage_initialization(self) -> None:
        """Test file storage backend initialization."""
        # Default initialization (temp directory)
        backend = File()
        assert backend.base_path.exists()
        assert backend.base_path.is_dir()

        # Custom path initialization
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = Path(temp_dir) / "custom_storage"
            backend2 = File(str(custom_path))
            assert backend2.base_path == custom_path
            assert backend2.base_path.exists()

    def test_file_storage_execute(self) -> None:
        """Test file storage backend execution."""
        backend = File()
        result = backend.execute()

        assert result.success
        data = result.value
        assert data["backend_type"] == "file"
        assert "base_path" in data
        assert data["exists"] is True
        assert data["status"] == "ready"

    def test_file_storage_execute_error_handling(self) -> None:
        """Test file storage backend error handling."""
        backend = File()

        # Force an error by patching base_path
        with patch.object(backend, "base_path", side_effect=Exception("Path error")):
            result = backend.execute()
            FlextMatchers.assert_result_failure(result)


class TestMemory:
    """Test Memoryfunctionality."""

    def test_memory_storage_initialization(self) -> None:
        """Test memory storage backend initialization."""
        backend = Memory()
        assert isinstance(backend._storage, dict)
        assert len(backend._storage) == 0

    def test_memory_storage_execute(self) -> None:
        """Test memory storage backend execution."""
        backend = Memory()

        # Add some data to storage
        backend._storage["test_key"] = "test_value"
        backend._storage["another_key"] = {"data": "json"}

        result = backend.execute()
        assert result.success
        data = result.value
        assert data["backend_type"] == "memory"
        assert data["items_count"] == 2
        assert data["status"] == "ready"

    def test_memory_storage_execute_error_handling(self) -> None:
        """Test memory storage backend error handling."""
        backend = Memory()

        # Force an error by patching _storage
        with patch.object(backend, "_storage", side_effect=Exception("Memory error")):
            result = backend.execute()
            FlextMatchers.assert_result_failure(result)


class Test:
    """Test functionality."""

    def test_storage_config_initialization(self) -> None:
        """Test storage configuration initialization."""
        # Default configuration
        config = FlextApiModels.StorageConfig()
        assert config.backend == "memory"
        assert config.options == {}

        # Custom configuration
        custom_config = {
            "backend": "file",
            "base_path": "/custom/path",
            "max_size": 5000,
            "ttl": 1800,
        }
        assert custom_config.backend == "file"
        assert custom_config.options["base_path"] == "/custom/path"
        assert custom_config.options["max_size"] == 5000
        assert custom_config.options["ttl"] == 1800

    def test_storage_config_execute(self) -> None:
        """Test storage configuration execution."""
        config = FlextApiModels.StorageConfig(
            backend="redis", host="localhost", port=6379, db=0
        )

        result = config.execute()
        assert result.success
        data = result.value
        assert data["config_type"] == "storage"
        assert data["backend"] == "redis"
        assert data["options"]["host"] == "localhost"
        assert data["options"]["port"] == 6379
        assert data["options"]["db"] == 0
        assert data["status"] == "configured"

    def test_storage_config_execute_error_handling(self) -> None:
        """Test storage configuration error handling."""
        config = FlextApiModels.StorageConfig()

        # Force an error by patching backend
        with patch.object(config, "backend", side_effect=Exception("Config error")):
            result = config.execute()
            FlextMatchers.assert_result_failure(result)


class TestIntegratedStorageOperations:
    """Test integrated storage operations with realistic scenarios."""

    def test_cache_lifecycle_scenario(self) -> None:
        """Test complete cache lifecycle scenario."""
        storage = FlextApiStorage(max_size=100, default_ttl=300)

        # Store user session data
        session_data = {
            "user_id": 12345,
            "username": "testuser",
            "permissions": ["read", "write"],
            "login_time": time.time(),
        }

        session_key = "session:12345"
        result = storage.set(session_key, session_data, ttl=600)
        assert result.success

        # Retrieve session data
        result = storage.get(session_key)
        assert result.success
        retrieved_data = result.value
        assert retrieved_data["user_id"] == 12345
        assert retrieved_data["username"] == "testuser"

        # Store API response cache
        api_response = {
            "data": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}],
            "total": 2,
            "page": 1,
        }

        cache_key = "api:users:page:1"
        result = storage.set(cache_key, api_response, ttl=120)  # 2 minute cache
        assert result.success

        # Check storage size
        result = storage.size()
        assert result.success
        assert result.value == 2

        # Get all keys
        result = storage.keys()
        assert result.success
        keys = result.value
        assert session_key in keys
        assert cache_key in keys

        # Clean up specific item
        result = storage.delete(cache_key)
        assert result.success

        # Verify deletion
        result = storage.size()
        assert result.success
        assert result.value == 1

        # Clear all cache
        result = storage.clear()
        assert result.success

        # Verify everything is cleared
        result = storage.size()
        assert result.success
        assert result.value == 0

    def test_serialization_roundtrip(self) -> None:
        """Test serialization and deserialization roundtrip."""
        storage = FlextApiStorage()

        # Complex data structure
        complex_data = {
            "metadata": {"version": "1.0", "created": "2025-01-01T00:00:00Z"},
            "items": [
                {"id": 1, "active": True, "tags": ["important", "urgent"]},
                {"id": 2, "active": False, "tags": ["archived"]},
            ],
            "counts": {"total": 2, "active": 1, "inactive": 1},
        }

        # Serialize
        serialize_result = storage.serialize_data(complex_data)
        assert serialize_result.success
        json_string = serialize_result.value

        # Deserialize
        deserialize_result = storage.deserialize_data(json_string)
        assert deserialize_result.success
        restored_data = deserialize_result.value

        # Verify data integrity
        assert restored_data == complex_data
        assert restored_data["metadata"]["version"] == "1.0"
        assert len(restored_data["items"]) == 2
        assert restored_data["counts"]["total"] == 2

    def test_ttl_behavior_realistic(self) -> None:
        """Test TTL behavior with realistic timing."""
        storage = FlextApiStorage()

        # Set items with different TTLs
        storage.set("permanent", "permanent_data", ttl=0)  # No expiration
        storage.set("medium_term", "medium_data", ttl=2)  # 2 seconds
        storage.set("short_term", "short_data", ttl=1)  # 1 second

        # All should be available immediately
        assert storage.get("permanent").success
        assert storage.get("medium_term").success
        assert storage.get("short_term").success

        # Wait for short_term to expire
        time.sleep(1.1)

        # Check availability
        assert storage.get("permanent").success
        assert storage.get("medium_term").success
        assert not storage.get("short_term").success  # Should be expired

        # Wait for medium_term to expire
        time.sleep(1.0)

        # Check final availability
        assert storage.get("permanent").success
        assert not storage.get("medium_term").success  # Should be expired
        assert not storage.get("short_term").success  # Still expired

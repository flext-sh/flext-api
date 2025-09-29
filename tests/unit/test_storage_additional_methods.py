"""Tests for FlextApiStorage additional methods to improve coverage."""

import json
from typing import cast

from flext_api import FlextApiStorage


class TestFlextApiStorageAdditionalMethods:
    """Tests for FlextApiStorage additional methods to improve coverage."""

    def test_json_storage_serialize_success(self) -> None:
        """Test JSON storage serialization success."""
        storage = FlextApiStorage()
        json_storage = storage.JsonStorage()

        test_data = {"key": "value", "number": 123, "list": [1, 2, 3]}

        result = json_storage.serialize(test_data)

        assert result.is_success
        assert isinstance(result.data, str)

        # Verify the serialized data can be parsed back
        parsed_data = json.loads(result.data)
        assert parsed_data == test_data

    def test_json_storage_serialize_failure(self) -> None:
        """Test JSON storage serialization failure."""
        storage = FlextApiStorage()
        json_storage = storage.JsonStorage()

        # Test with non-serializable data (circular reference)
        circular_data = {}
        circular_data["self"] = circular_data

        result = json_storage.serialize(circular_data)

        assert result.is_failure
        assert result.error is not None and "JSON serialization failed" in result.error

    def test_json_storage_deserialize_success(self) -> None:
        """Test JSON storage deserialization success."""
        storage = FlextApiStorage()
        json_storage = storage.JsonStorage()

        test_json = '{"key": "value", "number": 123, "list": [1, 2, 3]}'

        result = json_storage.deserialize(test_json)

        assert result.is_success
        assert isinstance(result.data, dict)
        data = result.data
        assert data["key"] == "value"
        assert data["number"] == 123
        assert data["list"] == [1, 2, 3]

    def test_json_storage_deserialize_failure(self) -> None:
        """Test JSON storage deserialization failure."""
        storage = FlextApiStorage()
        json_storage = storage.JsonStorage()

        invalid_json = '{"key": "value", "number": 123, "list": [1, 2, 3'  # Missing closing bracket

        result = json_storage.deserialize(invalid_json)

        assert result.is_failure
        assert (
            result.error is not None and "JSON deserialization failed" in result.error
        )

    def test_json_storage_deserialize_empty_string(self) -> None:
        """Test JSON storage deserialization with empty string."""
        storage = FlextApiStorage()
        json_storage = storage.JsonStorage()

        result = json_storage.deserialize("")

        assert result.is_failure
        assert (
            result.error is not None and "JSON deserialization failed" in result.error
        )

    def test_cache_operations_get_cache_stats(self) -> None:
        """Test cache operations get cache stats."""
        storage = FlextApiStorage()
        cache_ops = storage.CacheOperations()

        result = cache_ops.get_cache_stats()

        assert result.is_success
        assert isinstance(result.data, dict)
        assert "size" in cast("dict", result.data)
        assert "backend" in cast("dict", result.data)
        assert cast("dict", result.data)["backend"] == "memory"

    def test_cache_operations_cleanup_expired(self) -> None:
        """Test cache operations cleanup expired."""
        storage = FlextApiStorage()
        cache_ops = storage.CacheOperations()

        result = cache_ops.cleanup_expired()

        assert result.is_success
        assert isinstance(result.data, int)
        assert result.data >= 0

    def test_storage_with_json_data(self) -> None:
        """Test storage with JSON data operations."""
        storage = FlextApiStorage()

        # Test storing JSON data
        json_data = {"name": "test", "value": 42, "nested": {"key": "value"}}

        result = storage.set("json_key", json_data)
        assert result.is_success

        # Test retrieving JSON data
        retrieved = storage.get("json_key")
        assert retrieved.is_success
        assert retrieved.data == json_data

    def test_storage_with_complex_data_types(self) -> None:
        """Test storage with complex data types."""
        storage = FlextApiStorage()

        # Test with various data types
        test_cases = [
            ("string_key", "simple string"),
            ("int_key", 12345),
            ("float_key", 123.45),
            ("bool_key", True),
            ("list_key", [1, 2, 3, "test"]),
            ("dict_key", {"nested": {"key": "value"}}),
            ("none_key", None),
        ]

        for key, value in test_cases:
            # Store the value
            result = storage.set(key, value)
            assert result.is_success, f"Failed to store {key}"

            # Retrieve the value
            retrieved = storage.get(key)
            assert retrieved.is_success, f"Failed to retrieve {key}"
            assert retrieved.data == value, f"Value mismatch for {key}"

    def test_storage_error_handling_edge_cases(self) -> None:
        """Test storage error handling for edge cases."""
        storage = FlextApiStorage()

        # Test with empty key (should fail validation)
        result = storage.set("", "value")
        assert result.is_failure
        assert result.error is not None and "Invalid key" in result.error

        # Test with None key (should fail validation)
        result = storage.set(None, "value")
        assert result.is_failure
        assert result.error is not None and "Invalid key" in result.error

    def test_storage_batch_operations_comprehensive(self) -> None:
        """Test comprehensive batch operations."""
        storage = FlextApiStorage()

        # Test batch set with multiple items
        batch_data = {
            "batch_key_1": "value_1",
            "batch_key_2": "value_2",
            "batch_key_3": "value_3",
        }

        result = storage.batch_set(cast("dict[str, object]", batch_data))
        assert result.is_success

        # Test batch get
        keys = list(batch_data.keys())
        retrieved = storage.batch_get(keys)
        assert retrieved.is_success
        assert isinstance(retrieved.data, dict)

        # Test batch delete
        delete_result = storage.batch_delete(keys)
        assert delete_result.is_success

        # Verify items are deleted
        for key in keys:
            exists_result = storage.exists(key)
            assert exists_result.is_success
            assert not exists_result.data

    def test_storage_info_and_metrics(self) -> None:
        """Test storage info and metrics methods."""
        storage = FlextApiStorage()

        # Add some test data
        storage.set("info_key_1", "value_1")
        storage.set("info_key_2", "value_2")

        # Test info method
        info_result = storage.info()
        assert info_result.is_success
        assert isinstance(info_result.data, dict)
        assert "size" in info_result.data

        # Test metrics method
        metrics_result = storage.metrics()
        assert metrics_result.is_success
        assert isinstance(metrics_result.data, dict)
        assert "keys_count" in metrics_result.data
        assert "storage_size" in metrics_result.data

    def test_storage_health_check(self) -> None:
        """Test storage health check."""
        storage = FlextApiStorage()

        health_result = storage.health_check()
        assert health_result.is_success
        assert isinstance(health_result.data, dict)
        assert "status" in health_result.data
        assert "timestamp" in health_result.data

    def test_storage_keys_items_values(self) -> None:
        """Test storage keys, items, and values methods."""
        storage = FlextApiStorage()

        # Add test data
        test_data = {
            "keys_test_1": "value_1",
            "keys_test_2": "value_2",
            "keys_test_3": "value_3",
        }

        for key, value in test_data.items():
            storage.set(key, value)

        # Test keys method
        keys_result = storage.keys()
        assert keys_result.is_success
        assert isinstance(keys_result.data, list)
        for key in test_data:
            assert key in keys_result.data

        # Test items method
        items_result = storage.items()
        assert items_result.is_success
        assert isinstance(items_result.data, list)

        # Test values method
        values_result = storage.values()
        assert values_result.is_success
        assert isinstance(values_result.data, list)

    def test_storage_namespace_isolation(self) -> None:
        """Test storage namespace isolation."""
        storage1 = FlextApiStorage(namespace="namespace1")
        storage2 = FlextApiStorage(namespace="namespace2")

        # Store data in different namespaces
        storage1.set("shared_key", "namespace1_value")
        storage2.set("shared_key", "namespace2_value")

        # Verify isolation
        result1 = storage1.get("shared_key")
        result2 = storage2.get("shared_key")

        assert result1.is_success
        assert result2.is_success
        assert result1.data == "namespace1_value"
        assert result2.data == "namespace2_value"

    def test_storage_ttl_functionality(self) -> None:
        """Test storage TTL functionality."""
        storage = FlextApiStorage()

        # Test setting with TTL
        result = storage.set("ttl_key", "ttl_value", ttl=1)  # 1 second TTL
        assert result.is_success

        # Verify data exists
        exists_result = storage.exists("ttl_key")
        assert exists_result.is_success
        assert exists_result.data

        # Note: In a real implementation, we would wait for TTL to expire
        # For now, just test that the method accepts TTL parameter

    def test_storage_concurrent_access_simulation(self) -> None:
        """Test storage concurrent access simulation."""
        storage = FlextApiStorage()

        # Simulate concurrent operations
        operations = []

        # Add multiple items
        for i in range(10):
            result = storage.set(f"concurrent_key_{i}", f"value_{i}")
            operations.append(result)

        # Verify all operations succeeded
        for result in operations:
            assert result.is_success

        # Verify all items exist
        for i in range(10):
            exists_result = storage.exists(f"concurrent_key_{i}")
            assert exists_result.is_success
            assert exists_result.data

    def test_storage_method_existence(self) -> None:
        """Test that storage has all expected methods."""
        storage = FlextApiStorage()

        expected_methods = [
            "set",
            "get",
            "delete",
            "exists",
            "size",
            "clear",
            "batch_set",
            "batch_get",
            "batch_delete",
            "info",
            "health_check",
            "metrics",
            "keys",
            "items",
            "values",
        ]

        for method in expected_methods:
            assert hasattr(storage, method), f"Storage missing method: {method}"
            assert callable(getattr(storage, method)), (
                f"Storage method {method} is not callable"
            )

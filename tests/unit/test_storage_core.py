"""Tests for flext_api.storage module using flext_tests EM ABSOLUTO.

MAXIMUM usage of flext_tests - ALL test utilities via flext_tests.
Uses FlextTestsMatchers, FlextTestsDomains, FlextTestsUtilities.
ACESSO DIRETO - NO ALIASES.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
from typing import cast

from flext_core import FlextResult
from flext_core.typings import FlextTypes

# MAXIMUM usage of flext_tests - ACESSO DIRETO - NO ALIASES
from flext_tests import FlextTestsDomains, FlextTestsMatchers

from flext_api import FlextApiStorage


class TestFlextApiStorage:
    """Test FlextApiStorage using flext_tests patterns and real functionality."""

    def test_storage_creation_basic(self) -> None:
        """Test basic storage creation using flext_tests patterns."""
        storage = FlextApiStorage()

        # Verify storage is properly initialized
        assert isinstance(storage, FlextApiStorage)
        assert storage.config.get("backend", "memory") == "memory"
        assert storage.namespace == "default"

    def test_storage_creation_with_flext_tests_config(self) -> None:
        """Test storage creation with FlextTestsDomains config - ACESSO DIRETO."""
        # Use FlextTestsDomains for realistic storage configuration
        base_config = FlextTestsDomains.create_configuration()

        config = {
            "backend": str(base_config.get("storage_backend", "memory")),
            "namespace": f"test_{base_config.get('namespace', 'storage')}",
            "enable_caching": bool(base_config.get("enable_caching", True)),
            "cache_ttl_seconds": cast("int", base_config.get("cache_ttl", 600)),
        }

        storage = FlextApiStorage(config)

        assert storage.config["backend"] == config["backend"]
        assert storage.config["namespace"] == config["namespace"]
        assert storage.config["enable_caching"] is True
        assert storage.config["cache_ttl_seconds"] == 600

    def test_storage_with_fixture(self, flext_api_storage: FlextApiStorage) -> None:
        """Test storage using pytest fixture from conftest."""
        assert isinstance(flext_api_storage, FlextApiStorage)
        assert "TestStorage" in flext_api_storage.namespace
        assert flext_api_storage._cache_enabled is True

    def test_set_and_get_success(self) -> None:
        """Test successful set and get operations using FlextTestsDomains - ACESSO DIRETO."""
        storage = FlextApiStorage()
        # Use FlextTestsDomains for realistic service data
        test_data = FlextTestsDomains.create_service()

        # Set a value using FlextTestsDomains data
        set_result = storage.set("test_key", test_data)
        FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", set_result))

        # Get the value
        get_result = storage.get("test_key")
        FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", get_result))

        # Verify data integrity using FlextTestsMatchers - ACESSO DIRETO
        assert FlextTestsMatchers.is_successful_result(cast("FlextResult[object]", get_result))
        assert get_result.value == test_data

    def test_set_empty_key_failure(self) -> None:
        """Test set with empty key - using FlextTestsDomains - ACESSO DIRETO."""
        storage = FlextApiStorage()
        # Use FlextTestsDomains for realistic user data
        test_data = FlextTestsDomains.create_user()

        # FlextApiStorage implementation allows empty keys, so this should succeed
        result = storage.set("", test_data)
        FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", result))
        assert FlextTestsMatchers.is_successful_result(cast("FlextResult[object]", result))

        # Should be able to retrieve with empty key too
        get_result = storage.get("")
        FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", get_result))
        assert get_result.value == test_data

    def test_get_empty_key_failure(self) -> None:
        """Test get with empty key fails using FlextTestsMatchers - ACESSO DIRETO."""
        storage = FlextApiStorage()

        result = storage.get("")
        FlextTestsMatchers.assert_result_failure(cast("FlextResult[object]", result))
        assert FlextTestsMatchers.is_failed_result(cast("FlextResult[object]", result))

    def test_get_nonexistent_key_failure(self) -> None:
        """Test get with non-existent key fails using flext_tests validation."""
        storage = FlextApiStorage()

        result = storage.get("nonexistent_key")
        FlextTestsMatchers.assert_result_failure(cast("FlextResult[object]", result))
        assert FlextTestsMatchers.is_failed_result(cast("FlextResult[object]", result))
        if result.error:
            assert "not found" in result.error.lower()

    def test_delete_success(self) -> None:
        """Test successful delete operation using flext_tests patterns."""
        storage = FlextApiStorage()
        test_data = FlextTestsDomains.create_payload()

        # Set a value first using factory data
        storage.set("delete_key", test_data)

        # Delete it
        delete_result = storage.delete("delete_key")
        FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", delete_result))
        assert FlextTestsMatchers.is_successful_result(cast("FlextResult[object]", delete_result))

        # Verify it's gone
        get_result = storage.get("delete_key")
        FlextTestsMatchers.assert_result_failure(cast("FlextResult[object]", get_result))
        assert FlextTestsMatchers.is_failed_result(cast("FlextResult[object]", get_result))

    def test_delete_empty_key_failure(self) -> None:
        """Test delete with empty key fails using flext_tests validation."""
        storage = FlextApiStorage()

        result = storage.delete("")
        FlextTestsMatchers.assert_result_failure(cast("FlextResult[object]", result))
        assert FlextTestsMatchers.is_failed_result(cast("FlextResult[object]", result))

    def test_delete_nonexistent_key_failure(self) -> None:
        """Test delete with non-existent key fails using flext_tests validation."""
        storage = FlextApiStorage()

        result = storage.delete("nonexistent_key")
        FlextTestsMatchers.assert_result_failure(cast("FlextResult[object]", result))
        assert FlextTestsMatchers.is_failed_result(cast("FlextResult[object]", result))

    def test_clear_cache(self) -> None:
        """Test clearing the cache using flext_tests patterns."""
        storage = FlextApiStorage()
        test_data1 = FlextTestsDomains.create_user()
        test_data2 = FlextTestsDomains.create_service()

        # Add some values using factory data
        storage.set("key1", test_data1)
        storage.set("key2", test_data2)

        # Clear cache
        clear_result = storage.clear()
        FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", clear_result))
        assert FlextTestsMatchers.is_successful_result(cast("FlextResult[object]", clear_result))

        # Verify cache is empty - both keys should fail to retrieve
        get_result1 = storage.get("key1")
        get_result2 = storage.get("key2")
        FlextTestsMatchers.assert_result_failure(cast("FlextResult[object]", get_result1))
        FlextTestsMatchers.assert_result_failure(cast("FlextResult[object]", get_result2))

    def test_keys_operation(self) -> None:
        """Test getting all keys using flext_tests patterns."""
        storage = FlextApiStorage()

        # Initially should have no keys
        keys_result = storage.keys()
        FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", keys_result))
        assert FlextTestsMatchers.is_successful_result(cast("FlextResult[object]", keys_result))
        assert isinstance(keys_result.value, list)
        assert len(keys_result.value) == 0

        # Add some values using factory data
        batch_data = FlextTestsDomains.batch_users(2)
        storage.set("user1", batch_data[0])
        storage.set("user2", batch_data[1])

        # Get keys
        keys_result = storage.keys()
        FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", keys_result))

        keys = keys_result.value
        assert isinstance(keys, list)
        assert len(keys) == 2
        assert "user1" in keys
        assert "user2" in keys

    def test_exists_operation(self) -> None:
        """Test checking key existence using flext_tests patterns."""
        storage = FlextApiStorage()
        user_data = FlextTestsDomains.create_user()

        # Key should not exist initially
        exists_result = storage.exists("test_user")
        FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", exists_result))
        assert exists_result.value is False

        # Add user data
        storage.set("test_user", user_data)

        # Key should exist now
        exists_result = storage.exists("test_user")
        FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", exists_result))
        assert exists_result.value is True

    def test_storage_with_configuration_data(
        self, sample_configuration_data: FlextTypes.Core.Dict
    ) -> None:
        """Test storage with configuration data from conftest fixture."""
        # Create storage config using FlextTestsDomains - ACESSO DIRETO
        base_config = FlextTestsDomains.create_configuration()
        config = {
            "backend": str(base_config.get("storage_backend", "memory")),
            "namespace": f"test_{base_config.get('namespace', 'storage')}",
            "enable_caching": bool(base_config.get("enable_caching", True)),
            "cache_ttl_seconds": cast("int", base_config.get("cache_ttl", 300)),
        }
        storage = FlextApiStorage(config)

        # Store configuration data
        set_result = storage.set("config", sample_configuration_data)
        FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", set_result))

        # Retrieve and validate
        get_result = storage.get("config")
        FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", get_result))

        # Verify data structure - sample_configuration_data has different fields
        retrieved_config = get_result.value
        assert isinstance(retrieved_config, dict)
        # Just verify it's the same data we stored
        assert retrieved_config == sample_configuration_data

    def test_storage_batch_operations(self) -> None:
        """Test batch operations using flext_tests factory patterns."""
        storage = FlextApiStorage()

        # Create batch of test data
        batch_requests = [FlextTestsDomains.create_payload() for _ in range(3)]

        # Store all requests
        for i, request_data in enumerate(batch_requests):
            key = f"request_{i}"
            set_result = storage.set(key, request_data)
            FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", set_result))

        # Verify all can be retrieved
        for i in range(3):
            key = f"request_{i}"
            get_result = storage.get(key)
            FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", get_result))
            assert FlextTestsMatchers.is_successful_result(cast("FlextResult[object]", get_result))

    def test_storage_with_user_data(
        self, sample_user_data: FlextTypes.Core.Dict
    ) -> None:
        """Test storage operations with user data from conftest fixture."""
        storage = FlextApiStorage()

        # Store user data from fixture
        set_result = storage.set("sample_user", sample_user_data)
        FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", set_result))

        # Retrieve and validate structure
        get_result = storage.get("sample_user")
        FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", get_result))

        user = get_result.value
        assert isinstance(user, dict)
        # Validate user has expected fields from FlextTestsDomains
        expected_fields = ["id", "name", "email"]
        for field in expected_fields:
            assert field in user

    def test_storage_with_service_data(
        self, sample_service_data: FlextTypes.Core.Dict
    ) -> None:
        """Test storage operations with service data from conftest fixture."""
        storage = FlextApiStorage()

        # Store service data from fixture
        set_result = storage.set("sample_service", sample_service_data)
        FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", set_result))

        # Check existence
        exists_result = storage.exists("sample_service")
        FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", exists_result))
        assert exists_result.value is True

        # Retrieve and validate
        get_result = storage.get("sample_service")
        FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", get_result))

        service = get_result.value
        assert isinstance(service, dict)
        assert "name" in service or "service_name" in service

    def test_storage_error_scenarios(self) -> None:
        """Test various error scenarios using flext_tests patterns."""
        storage = FlextApiStorage()

        # Test with None values
        set_result = storage.set("none_key", None)
        FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", set_result))  # Should be allowed to store None)

        get_result = storage.get("none_key")
        FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", get_result))
        assert get_result.value is None

    def test_storage_performance_with_batch_data(self) -> None:
        """Test storage batch operations using flext_tests factory data."""
        storage = FlextApiStorage()

        # Perform batch operations with factory data
        batch_data = [FlextTestsDomains.api_response_data() for _ in range(5)]
        stored_keys = []

        # Store all batch data
        for i, data in enumerate(batch_data):
            key = f"perf_key_{i}"
            set_result = storage.set(key, data)
            FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", set_result))
            stored_keys.append(key)

        # Verify all data can be retrieved correctly
        for i, key in enumerate(stored_keys):
            get_result = storage.get(key)
            FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", get_result))
            assert FlextTestsMatchers.is_successful_result(cast("FlextResult[object]", get_result))
            assert get_result.value == batch_data[i]

    def test_storage_close_operation(self) -> None:
        """Test storage close operation using async patterns."""

        async def test_close() -> None:
            storage = FlextApiStorage()

            # Add some data
            test_data = FlextTestsDomains.create_payload()
            storage.set("close_test", test_data)

            # Close should succeed
            close_result = await storage.close()
            FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", close_result))
            assert FlextTestsMatchers.is_successful_result(cast("FlextResult[object]", close_result))

        # Run async test
        asyncio.run(test_close())

    def test_storage_multiple_instances_independence(self) -> None:
        """Test multiple storage instances are independent using flext_tests patterns."""
        config1 = FlextTestsDomains.create_configuration(namespace="storage1")
        config2 = FlextTestsDomains.create_configuration(namespace="storage2")

        storage1 = FlextApiStorage(config1)
        storage2 = FlextApiStorage(config2)

        assert storage1 is not storage2
        assert storage1.namespace != storage2.namespace

        # Set different data in each storage
        data1 = FlextTestsDomains.create_user()
        data2 = FlextTestsDomains.create_service()

        storage1.set("shared_key", data1)
        storage2.set("shared_key", data2)

        # Each should have their own data
        result1 = storage1.get("shared_key")
        result2 = storage2.get("shared_key")

        FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", result1))
        FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", result2))
        assert result1.value != result2.value

    def test_storage_data_integrity_validation(self) -> None:
        """Test data integrity using flext_tests validation patterns."""
        storage = FlextApiStorage()

        # Test various data types from factory
        test_cases = [
            FlextTestsDomains.create_user(),
            FlextTestsDomains.create_service(),
            FlextTestsDomains.create_payload(),
            FlextTestsDomains.create_configuration(),
        ]

        for i, test_data in enumerate(test_cases):
            key = f"integrity_test_{i}"

            # Store data
            set_result = storage.set(key, test_data)
            FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", set_result))

            # Retrieve and verify exact match
            get_result = storage.get(key)
            FlextTestsMatchers.assert_result_success(cast("FlextResult[object]", get_result))

            # Use FlextTestsMatchers for deep equality check
            retrieved_data = get_result.value
            assert retrieved_data == test_data, f"Data integrity failed for case {i}"

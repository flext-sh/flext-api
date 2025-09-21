"""Comprehensive unit tests for FlextContainer targeting 100% coverage.

This module provides comprehensive tests for FlextContainer module to achieve
100% unit test coverage using flext_tests standardization patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsMatchers

from flext_core import FlextContainer, FlextResult


class TestFlextContainer100PercentCoverage:
    """Comprehensive FlextContainer tests targeting 100% coverage."""

    def test_service_key_creation_and_validation(self) -> None:
        """Test FlextContainer.ServiceKey creation and validation."""
        # Test valid service key
        valid_key: FlextContainer.ServiceKey[str] = FlextContainer.ServiceKey(
            "valid_service",
        )
        FlextTestsMatchers.assert_result_success(
            FlextResult[FlextContainer.ServiceKey[str]].ok(valid_key),
        )
        assert valid_key.name == "valid_service"

        # Test empty service key validation
        empty_key: FlextContainer.ServiceKey[str] = FlextContainer.ServiceKey("")
        assert not empty_key.name

        # Test service key with special characters
        special_key: FlextContainer.ServiceKey[str] = FlextContainer.ServiceKey(
            "service.with.dots",
        )
        assert special_key.name == "service.with.dots"

        # Test service key equality
        key1: FlextContainer.ServiceKey[str] = FlextContainer.ServiceKey("test")
        key2: FlextContainer.ServiceKey[str] = FlextContainer.ServiceKey("test")
        key3: FlextContainer.ServiceKey[str] = FlextContainer.ServiceKey("different")

        assert key1 == key2
        assert key1 != key3
        assert hash(key1) == hash(key2)
        assert hash(key1) != hash(key3)

    def test_container_service_registration_operations(self) -> None:
        """Test FlextContainer service registration operations."""
        container = FlextContainer.get_global()

        # Test service registration
        test_service = {"name": "test_service", "port": 8080}
        register_result = container.register("test_service", test_service)
        assert register_result.is_success

        # Test service retrieval
        get_result = container.get("test_service")
        assert get_result.is_success
        assert get_result.unwrap() == test_service

        # Test service existence check
        has_result = container.has("test_service")
        assert has_result is True

        # Test service count
        count_result = container.get_service_count()
        assert count_result >= 1

        # Clean up
        container.unregister("test_service")

    def test_container_factory_registration(self) -> None:
        """Test FlextContainer factory registration."""
        container = FlextContainer.get_global()

        # Test factory function
        def test_factory() -> dict[str, object]:
            return {"name": "factory_service", "created": True}

        # Test factory registration
        factory_result = container.register_factory("factory_service", test_factory)
        assert factory_result.is_success

        # Test factory service retrieval
        get_result = container.get("factory_service")
        assert get_result.is_success
        service = get_result.unwrap()
        assert isinstance(service, dict)
        assert service["name"] == "factory_service"
        assert service["created"] is True

        # Clean up
        container.unregister("factory_service")

    def test_container_service_listing_operations(self) -> None:
        """Test FlextContainer service listing operations."""
        container = FlextContainer.get_global()

        # Register test services
        container.register("list_test_1", {"id": 1})
        container.register("list_test_2", {"id": 2})

        # Test service names listing
        service_names = container.get_service_names()
        assert "list_test_1" in service_names
        assert "list_test_2" in service_names

        # Test services listing
        services_result = container.list_services()
        assert isinstance(services_result, dict)

        # Clean up
        container.unregister("list_test_1")
        container.unregister("list_test_2")

    def test_container_basic_operations_comprehensive(self) -> None:
        """Test FlextContainer basic operations comprehensively."""
        container = FlextContainer.get_global()

        # Test typed service operations
        typed_key: FlextContainer.ServiceKey[dict] = FlextContainer.ServiceKey(
            "typed_service"
        )
        test_data = {"typed": True, "value": 42}

        register_result = container.register(typed_key.name, test_data)
        assert register_result.is_success

        # Test container info with service name (after registration)
        info_result = container.get_info("typed_service")
        assert info_result.is_success
        info_data = info_result.unwrap()
        assert isinstance(info_data, dict)

        get_typed_result = container.get_typed(typed_key.name, dict)
        assert get_typed_result.is_success
        assert get_typed_result.unwrap() == test_data

        # Clean up
        container.unregister(typed_key.name)

    def test_container_advanced_operations(self) -> None:
        """Test FlextContainer advanced operations."""
        container = FlextContainer.get_global()

        # Test batch registration
        services = {
            "batch_service_1": {"value": 1},
            "batch_service_2": {"value": 2},
            "batch_service_3": {"value": 3},
        }

        batch_result = container.batch_register(services)
        assert batch_result.is_success

        # Verify all services were registered
        for service_name in services:
            has_result = container.has(service_name)
            assert has_result is True

        # Test get_or_create functionality with existing service (no factory needed)
        get_or_create_result = container.get_or_create("batch_service_1")
        assert get_or_create_result.is_success
        assert get_or_create_result.unwrap()["value"] == 1

        # Clean up
        for service_name in services:
            container.unregister(service_name)

    def test_container_error_handling(self) -> None:
        """Test FlextContainer error handling scenarios."""
        container = FlextContainer.get_global()

        # Test getting non-existent service
        get_result = container.get("non_existent_service")
        assert get_result.is_failure

        # Test unregistering non-existent service
        unregister_result = container.unregister("non_existent_service")
        assert unregister_result.is_failure

        # Test has operation for non-existent service
        has_result = container.has("non_existent_service")
        assert has_result is False

    def test_container_global_operations(self) -> None:
        """Test FlextContainer global operations."""
        # Test global container access
        container1 = FlextContainer.get_global()
        container2 = FlextContainer.get_global()

        # Should be the same instance (singleton)
        assert container1 is container2

        # Test global registration
        register_result = FlextContainer.register_global(
            "global_test", {"global": True}
        )
        assert register_result.is_success

        # Test global typed access
        global_typed_result = FlextContainer.get_global_typed("global_test", dict)
        assert global_typed_result.is_success

        # Clean up
        container1.unregister("global_test")

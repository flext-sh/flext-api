"""Comprehensive container coverage tests using flext_tests patterns.

Tests critical FlextContainer functionality with edge cases, error handling,
and performance scenarios to achieve 100% coverage using standardized patterns.
"""

import math
from typing import Any

from flext_core import FlextContainer
from flext_tests import FlextTestsMatchers


class TestFlextContainerComprehensiveCoverage:
    """Comprehensive coverage tests for FlextContainer using flext_tests patterns."""

    def test_service_registration_edge_cases(
        self, clean_container: FlextContainer
    ) -> None:
        """Test service registration edge cases for coverage."""
        container = clean_container

        # Test registration with None service
        result = container.register("test_service", None)
        FlextTestsMatchers.assert_result_success(result)  # Container accepts None

        # Test registration with empty string name
        result = container.register("", "service")
        FlextTestsMatchers.assert_result_failure(result)

        # Test registration with whitespace-only name
        result = container.register("   ", "service")
        FlextTestsMatchers.assert_result_failure(result)

    def test_service_retrieval_edge_cases(
        self, clean_container: FlextContainer
    ) -> None:
        """Test service retrieval edge cases for coverage."""
        container = clean_container

        # Test getting non-existent service
        result = container.get("non_existent")
        FlextTestsMatchers.assert_result_failure(result)

        # Test getting with empty string name
        result = container.get("")
        FlextTestsMatchers.assert_result_failure(result)

        # Register and retrieve valid service
        container.register("valid_service", {"data": "test"})
        result = container.get("valid_service")
        FlextTestsMatchers.assert_result_success(result)
        assert result.value == {"data": "test"}

    def test_factory_registration_comprehensive(
        self, clean_container: FlextContainer
    ) -> None:
        """Test factory registration with comprehensive scenarios."""
        container = clean_container

        # Test factory registration
        def create_service() -> dict[str, str]:
            return {"type": "factory_created", "id": "123"}

        result = container.register_factory("factory_service", create_service)
        FlextTestsMatchers.assert_result_success(result)

        # Test factory execution
        service_result = container.get("factory_service")
        FlextTestsMatchers.assert_result_success(service_result)
        assert service_result.value["type"] == "factory_created"

        # Test factory with exception
        def failing_factory() -> dict[str, str]:
            error_msg = "Factory failed"
            raise ValueError(error_msg)

        result = container.register_factory("failing_factory", failing_factory)
        FlextTestsMatchers.assert_result_success(result)

        # Getting from failing factory should handle exception
        failed_result = container.get("failing_factory")
        FlextTestsMatchers.assert_result_failure(failed_result)

    def test_service_unregistration_comprehensive(
        self, clean_container: FlextContainer
    ) -> None:
        """Test service unregistration edge cases."""
        container = clean_container

        # Test unregistering non-existent service
        result = container.unregister("non_existent")
        FlextTestsMatchers.assert_result_failure(result)

        # Test unregistering existing service
        container.register("temp_service", {"temp": "data"})
        result = container.unregister("temp_service")
        FlextTestsMatchers.assert_result_success(result)

        # Verify service is gone
        get_result = container.get("temp_service")
        FlextTestsMatchers.assert_result_failure(get_result)

    def test_container_clear_comprehensive(
        self, clean_container: FlextContainer
    ) -> None:
        """Test container clear functionality."""
        container = clean_container

        # Register multiple services
        for i in range(5):
            container.register(f"service_{i}", {"index": i})

        assert container.get_service_count() == 5

        # Clear container
        container.clear()

        # Verify all services are gone
        assert container.get_service_count() == 0
        for i in range(5):
            result = container.get(f"service_{i}")
            FlextTestsMatchers.assert_result_failure(result)

    def test_service_listing_comprehensive(
        self, clean_container: FlextContainer
    ) -> None:
        """Test service listing functionality."""
        container = clean_container

        # Test empty container
        assert container.get_service_count() == 0
        assert container.get_service_names() == []

        # Register services
        services = {"service_a": "data_a", "service_b": "data_b", "service_c": "data_c"}
        for name, data in services.items():
            container.register(name, data)

        # Test service count and names
        assert container.get_service_count() == 3
        names = container.get_service_names()
        assert len(names) == 3
        assert all(name in names for name in services)

    def test_container_has_method_comprehensive(
        self, clean_container: FlextContainer
    ) -> None:
        """Test container has() method comprehensively."""
        container = clean_container

        # Test non-existent service
        assert not container.has("non_existent")

        # Register service and test
        container.register("existing_service", {"data": "test"})
        assert container.has("existing_service")

        # Unregister and test again
        container.unregister("existing_service")
        assert not container.has("existing_service")

    def test_singleton_registration_comprehensive(
        self, clean_container: FlextContainer
    ) -> None:
        """Test singleton patterns and global container management."""
        container = clean_container

        # Test service registration and retrieval
        test_service = {"singleton": True, "id": "global_test"}
        result = container.register("singleton_service", test_service)
        FlextTestsMatchers.assert_result_success(result)

        # Verify retrieval
        get_result = container.get("singleton_service")
        FlextTestsMatchers.assert_result_success(get_result)
        assert get_result.value == test_service

    def test_container_error_handling_comprehensive(
        self, clean_container: FlextContainer
    ) -> None:
        """Test comprehensive error handling scenarios."""
        container = clean_container

        # Test invalid service names
        invalid_names = ["", "   ", "\t", "\n"]
        for invalid_name in invalid_names:
            result = container.register(invalid_name, "data")
            FlextTestsMatchers.assert_result_failure(result)

            get_result = container.get(invalid_name)
            FlextTestsMatchers.assert_result_failure(get_result)

        # Test valid edge case names
        edge_names = ["123", "_service", "service-name", "service.name"]
        for edge_name in edge_names:
            result = container.register(edge_name, f"data_{edge_name}")
            # Some names might be valid, test both outcomes
            if result.success:
                get_result = container.get(edge_name)
                FlextTestsMatchers.assert_result_success(get_result)

    def test_container_memory_management(self, clean_container: FlextContainer) -> None:
        """Test container memory management with large datasets."""
        container = clean_container

        # Register large service data
        large_data = {"data": "x" * 10000, "numbers": list(range(1000))}
        result = container.register("large_service", large_data)
        FlextTestsMatchers.assert_result_success(result)

        # Verify retrieval
        get_result = container.get("large_service")
        FlextTestsMatchers.assert_result_success(get_result)
        assert len(get_result.value["data"]) == 10000

        # Unregister to test cleanup
        container.unregister("large_service")

        # Verify cleanup
        result = container.get("large_service")
        FlextTestsMatchers.assert_result_failure(result)

    def test_container_type_safety_comprehensive(
        self, clean_container: FlextContainer
    ) -> None:
        """Test container type safety and value preservation."""
        container = clean_container

        # Test various data types
        test_data = {
            "string": "test_string",
            "integer": 42,
            "float": math.pi,
            "boolean": True,
            "none": None,
            "list": [1, 2, 3],
            "dict": {"nested": "data"},
        }

        for key, value in test_data.items():
            # Register with type-specific key
            service_name = f"typed_{key}"
            result = container.register(service_name, value)
            FlextTestsMatchers.assert_result_success(result)

            # Retrieve and verify type preservation
            get_result = container.get(service_name)
            FlextTestsMatchers.assert_result_success(get_result)
            assert get_result.value == value
            assert isinstance(get_result.value, type(value))

    def test_container_global_instance_management(
        self, clean_container: FlextContainer
    ) -> None:
        """Test global container instance management."""
        # Test global container access
        global_container = FlextContainer.get_global()
        assert isinstance(global_container, FlextContainer)

        # Test that multiple calls return same instance
        global_container2 = FlextContainer.get_global()
        assert global_container is global_container2

        # Test clean_container is different from global
        assert clean_container is not global_container

    def test_container_performance_edge_cases(
        self, clean_container: FlextContainer
    ) -> None:
        """Test container performance with edge cases."""
        container = clean_container

        # Test rapid registration/unregistration
        for i in range(100):
            service_name = f"perf_service_{i}"
            result = container.register(service_name, {"index": i})
            FlextTestsMatchers.assert_result_success(result)

        assert container.get_service_count() == 100

        # Test rapid retrieval
        for i in range(50):
            result = container.get(f"perf_service_{i}")
            FlextTestsMatchers.assert_result_success(result)
            assert result.value["index"] == i

        # Test rapid unregistration
        for i in range(50, 100):
            result = container.unregister(f"perf_service_{i}")
            FlextTestsMatchers.assert_result_success(result)

        assert container.get_service_count() == 50

    def test_container_dependency_injection_patterns(
        self, clean_container: FlextContainer
    ) -> None:
        """Test dependency injection patterns and service composition."""
        container = clean_container

        # Register dependent services
        database_service = {"type": "database", "connection": "test_db"}
        logger_service = {"type": "logger", "level": "info"}

        container.register("database", database_service)
        container.register("logger", logger_service)

        # Create composite service that depends on others
        def create_composite_service() -> dict[str, Any]:
            db_result = container.get("database")
            logger_result = container.get("logger")

            if not db_result.success or not logger_result.success:
                error_msg = "Dependencies not available"
                raise ValueError(error_msg)

            return {
                "type": "composite",
                "database": db_result.value,
                "logger": logger_result.value,
                "initialized": True,
            }

        # Register composite service factory
        result = container.register_factory("composite", create_composite_service)
        FlextTestsMatchers.assert_result_success(result)

        # Test composite service creation
        composite_result = container.get("composite")
        FlextTestsMatchers.assert_result_success(composite_result)

        composite_data = composite_result.value
        assert composite_data["type"] == "composite"
        assert composite_data["initialized"] is True
        assert composite_data["database"]["type"] == "database"
        assert composite_data["logger"]["type"] == "logger"

"""Tests for FlextDomainService functionality - REAL tests without mocks.

Tests the actual FlextDomainService from flext-core that replaced the old
base_service.py implementation. Focus on domain service execution patterns.
"""

from __future__ import annotations

from typing import override

from flext_core import FlextDomainService, FlextResult


class HealthyTestService(FlextDomainService[dict[str, object]]):
    """Test service that always succeeds."""

    @override
    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute the domain service operation."""
        return FlextResult[dict[str, object]].ok(
            {"status": "healthy", "message": "All systems operational"}
        )


class FailingStartService(FlextDomainService[None]):
    """Test service that fails to start."""

    @override
    def execute(self) -> FlextResult[None]:
        """Execute implementation that fails."""
        return FlextResult[None].fail("Start operation failed")


class FailingHealthService(FlextDomainService[None]):
    """Test service with failing health checks."""

    @override
    def execute(self) -> FlextResult[None]:
        """Execute implementation that fails for health checks."""
        return FlextResult[None].fail("Service execution failed")


class CustomDetailsService(FlextDomainService[dict[str, object]]):
    """Service with complex health details."""

    @override
    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute with complex health details."""
        return FlextResult[dict[str, object]].ok({
            "service_id": "custom-123",
            "uptime": 3600,
            "connections": 42,
            "memory_usage": "256MB",
            "last_check": "2024-01-01T12:00:00Z"
        })


class TestBaseServiceMissingCoverage:
    """Test domain service functionality with real FlextDomainService."""

    def test_service_execution_failure_path(self) -> None:
        """Test service execution failure path - covers error handling."""
        service = FailingStartService()

        result = service.execute()

        # Should fail with specific error
        assert not result.success
        assert result.error is not None
        assert "Start operation failed" in result.error

    def test_service_execution_failure_paths(self) -> None:
        """Test service execution failure paths - covers error handling."""
        service = FailingHealthService()

        # Test execution failure
        result = service.execute()

        # Should fail with specific error
        assert not result.success
        assert "Service execution failed" in result.error

    def test_service_successful_execution(self) -> None:
        """Test successful service execution."""
        service = HealthyTestService()

        # Execute service
        result = service.execute()
        assert result.success
        assert result.value is not None
        assert isinstance(result.value, dict)
        assert result.value["status"] == "healthy"

    def test_service_validation(self) -> None:
        """Test service validation functionality."""
        service = HealthyTestService()

        # Test business rules validation
        validation_result = service.validate_business_rules()
        assert validation_result.success

        # Test is_valid method
        assert service.is_valid()

        # Test config validation
        config_result = service.validate_config()
        assert config_result.success

    def test_service_execution_with_custom_data(self) -> None:
        """Test service execution with custom data."""
        service = CustomDetailsService()

        result = service.execute()
        assert result.success

        data = result.value
        assert "service_id" in data
        assert data["service_id"] == "custom-123"
        assert "uptime" in data
        assert data["uptime"] == 3600

    def test_service_lifecycle_complete(self) -> None:
        """Test complete service lifecycle with domain operations."""
        service = HealthyTestService()

        # Validation
        assert service.is_valid()

        # Execute
        result = service.execute()
        assert result.success

        # Verify result structure
        data = result.value
        assert isinstance(data, dict)
        assert "status" in data
        assert "message" in data

    def test_error_handling_robustness(self) -> None:
        """Test service error handling robustness."""
        # Test with service that fails
        failing_service = FailingStartService()

        result = failing_service.execute()
        assert not result.success
        assert result.error is not None

        # Should still be valid service instance
        assert failing_service.is_valid()

    def test_health_check_structure(self) -> None:
        """Test service execution result structure."""
        service = HealthyTestService()

        result = service.execute()

        assert result.success
        assert result.value is not None
        assert isinstance(result.value, dict)

        data = result.value
        # Standard response fields
        assert "status" in data
        assert "message" in data

    def test_service_state_consistency(self) -> None:
        """Test service state consistency across operations."""
        service = HealthyTestService()

        # Multiple executions should be consistent (stateless)
        for _ in range(3):
            result = service.execute()
            assert result.success
            assert result.value["status"] == "healthy"


class TestComplexHealthScenarios:
    """Test complex domain service scenarios."""

    def test_complex_health_details_structure(self) -> None:
        """Test complex health details data structure."""
        service = CustomDetailsService()

        result = service.execute()
        assert result.success

        data = result.value
        assert "service_id" in data
        assert "uptime" in data
        assert "connections" in data
        assert "memory_usage" in data
        assert "last_check" in data

    def test_concurrent_health_checks(self) -> None:
        """Test multiple service operations."""
        services = [
            HealthyTestService(),
            CustomDetailsService(),
        ]

        for service in services:
            result = service.execute()
            assert result.success
            assert isinstance(result.value, dict)

"""Tests for base_service.py missing coverage - REAL tests without mocks.

Focus on error handling paths and edge cases not covered by existing tests.
"""

from __future__ import annotations

import asyncio
from typing import override

import pytest
from flext_core import FlextResult

from flext_api.base_service import FlextApiBaseService


class HealthyTestService(FlextApiBaseService):
    """Test service that always succeeds."""

    service_name: str = "healthy-test-service"

    @override
    async def _do_start(self) -> FlextResult[None]:
        """Start implementation that succeeds."""
        return FlextResult[None].ok(None)

    @override
    async def _do_stop(self) -> FlextResult[None]:
        """Stop implementation that succeeds."""
        return FlextResult[None].ok(None)

    @override
    async def _get_health_details(self) -> FlextResult[dict[str, object]]:
        """Health details that succeed."""
        return FlextResult[dict[str, object]].ok(
            {"status": "healthy", "message": "All systems operational"}
        )


class FailingStartService(FlextApiBaseService):
    """Test service that fails to start."""

    service_name: str = "failing-start-service"

    @override
    async def _do_start(self) -> FlextResult[None]:
        """Start implementation that fails."""
        return FlextResult[None].fail("Start operation failed")

    @override
    async def _do_stop(self) -> FlextResult[None]:
        """Stop implementation that succeeds."""
        return FlextResult[None].ok(None)

    @override
    async def _get_health_details(self) -> FlextResult[dict[str, object]]:
        """Health details that succeed."""
        return FlextResult[dict[str, object]].ok(
            {"status": "not_started", "message": "Service failed to start"}
        )


class FailingHealthService(FlextApiBaseService):
    """Test service with failing health checks."""

    service_name: str = "failing-health-service"

    @override
    async def _do_start(self) -> FlextResult[None]:
        """Start implementation that succeeds."""
        return FlextResult[None].ok(None)

    @override
    async def _do_stop(self) -> FlextResult[None]:
        """Stop implementation that succeeds."""
        return FlextResult[None].ok(None)

    @override
    async def _get_health_details(self) -> FlextResult[dict[str, object]]:
        """Health details that fail."""
        return FlextResult[dict[str, object]].fail("Health check operation failed")


class TestBaseServiceMissingCoverage:
    """Test base service missing coverage paths."""

    @pytest.mark.asyncio
    async def test_service_start_failure_path(self) -> None:
        """Test service start failure path - covers error handling lines."""
        service = FailingStartService()

        result = await service.start_async()

        # Should fail with specific error
        assert not result.success
        assert result.error is not None
        assert "Start operation failed" in result.error

    @pytest.mark.asyncio
    async def test_service_health_check_failure_paths(self) -> None:
        """Test health check failure paths - covers health detail error lines."""
        service = FailingHealthService()
        await service.start_async()

        # Test health check failure - this service has health details that fail
        health_result = await service.health_check_async()

        # When health details fail, the health check itself may fail
        assert not health_result.success
        assert "Health check operation failed" in health_result.error

    @pytest.mark.asyncio
    async def test_service_concurrent_operations(self) -> None:
        """Test concurrent operations - covers concurrency paths."""
        service = HealthyTestService()

        # Start service
        start_result = await service.start_async()
        assert start_result.success

        # Try multiple concurrent health checks
        tasks = [
            service.health_check_async(),
            service.health_check_async(),
            service.health_check_async(),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should succeed
        for result in results:
            assert not isinstance(result, Exception)
            assert result.success

        # Stop service
        stop_result = await service.stop_async()
        assert stop_result.success

    @pytest.mark.asyncio
    async def test_health_check_structure(self) -> None:
        """Test health check response structure - covers aggregation lines."""
        service = HealthyTestService()
        await service.start_async()

        health_result = await service.health_check_async()
        assert health_result.success

        health_data = health_result.value

        # Verify basic structure (structure may vary based on implementation)
        assert "status" in health_data
        # Don't assume specific fields exist, just verify it's a valid health response
        assert health_data["status"] in {"healthy", "degraded"}

        await service.stop_async()

    @pytest.mark.asyncio
    async def test_service_lifecycle_complete(self) -> None:
        """Test complete service lifecycle - covers various lifecycle lines."""
        service = HealthyTestService()

        # Start service
        start_result = await service.start_async()
        assert start_result.success

        # Health check
        health_result = await service.health_check_async()
        assert health_result.success

        # Stop service
        stop_result = await service.stop_async()
        assert stop_result.success

    @pytest.mark.asyncio
    async def test_error_handling_robustness(self) -> None:
        """Test service error handling robustness."""
        # Test with service that fails to start
        failing_service = FailingStartService()

        start_result = await failing_service.start_async()
        assert not start_result.success

        # Health check should still work
        health_result = await failing_service.health_check_async()
        assert health_result.success

        # Stop should work even if start failed
        stop_result = await failing_service.stop_async()
        assert stop_result.success

    @pytest.mark.asyncio
    async def test_health_details_custom_data(self) -> None:
        """Test health details with custom data structures."""
        service = HealthyTestService()
        await service.start_async()

        health_result = await service.health_check_async()
        assert health_result.success

        health_data = health_result.value
        assert health_data["status"] in {"healthy", "degraded"}

        await service.stop_async()

    @pytest.mark.asyncio
    async def test_service_state_consistency(self) -> None:
        """Test service state consistency across operations."""
        service = HealthyTestService()

        # Multiple start/stop cycles
        for _ in range(3):
            start_result = await service.start_async()
            assert start_result.success

            health_result = await service.health_check_async()
            assert health_result.success

            stop_result = await service.stop_async()
            assert stop_result.success


class CustomDetailsService(FlextApiBaseService):
    """Service with complex health details."""

    service_name: str = "custom-details-service"

    @override
    async def _do_start(self) -> FlextResult[None]:
        return FlextResult[None].ok(None)

    @override
    async def _do_stop(self) -> FlextResult[None]:
        return FlextResult[None].ok(None)

    @override
    async def _get_health_details(self) -> FlextResult[dict[str, object]]:
        """Return complex health details."""
        return FlextResult[dict[str, object]].ok(
            {
                "custom_metric": 42,
                "service_info": "custom implementation",
                "nested": {"level1": {"level2": "deep"}},
                "list_data": [1, 2, 3],
                "flag": True,
            }
        )


class TestComplexHealthScenarios:
    """Test complex health check scenarios."""

    @pytest.mark.asyncio
    async def test_complex_health_details_structure(self) -> None:
        """Test complex health details structure handling."""
        service = CustomDetailsService()
        await service.start_async()

        health_result = await service.health_check_async()
        assert health_result.success

        await service.stop_async()

    @pytest.mark.asyncio
    async def test_concurrent_health_checks(self) -> None:
        """Test concurrent health checks."""
        service = HealthyTestService()
        await service.start_async()

        # Run multiple health checks concurrently
        tasks = [service.health_check_async() for _ in range(5)]
        results = await asyncio.gather(*tasks)

        # All should succeed
        for result in results:
            assert result.success

        await service.stop_async()

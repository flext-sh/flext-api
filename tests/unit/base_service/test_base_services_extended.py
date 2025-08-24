"""Extended tests for base service abstractions in flext_api using flext-core patterns."""

from __future__ import annotations

import pytest
from flext_core import FlextResult

from flext_api import FlextApiBaseService


class DummyService(FlextApiBaseService):
    """Minimal concrete service for lifecycle tests using flext-core patterns."""

    def __init__(self) -> None:
        super().__init__()
        # Store service name as a simple attribute (not in Pydantic data)
        object.__setattr__(self, "_service_name", "dummy")

    @property
    def service_name(self) -> str:
        """Get service name."""
        return self._service_name

    async def _do_start(self) -> FlextResult[None]:
        return FlextResult[None].ok(None)

    async def _do_stop(self) -> FlextResult[None]:
        return FlextResult[None].ok(None)

    async def process_data(self, data: dict[str, object]) -> FlextResult[dict[str, object]]:
        """Mock processing method for testing."""
        return FlextResult[dict[str, object]].ok({
            "processed": True,
            "input": data,
        })


@pytest.mark.asyncio
async def test_base_service_lifecycle() -> None:
    """Test basic service lifecycle operations."""
    service = DummyService()

    # Test start
    start_result = await service.start_async()
    assert start_result.success

    # Test health check
    health_result = await service.health_check_async()
    assert health_result.success
    assert health_result.value is not None
    assert "status" in health_result.value

    # Test stop
    stop_result = await service.stop_async()
    assert stop_result.success


@pytest.mark.asyncio
async def test_base_service_data_processing() -> None:
    """Test service data processing functionality."""
    service = DummyService()

    # Test data processing
    test_data = {"key": "value", "number": 42}
    result = await service.process_data(test_data)

    assert result.success
    assert result.value is not None
    assert result.value["processed"] is True
    assert result.value["input"] == test_data


def test_base_service_initialization() -> None:
    """Test service initialization and properties."""
    service = DummyService()

    assert service.service_name == "dummy"
    assert hasattr(service, "is_running")
    assert service.is_running is False  # Service starts as stopped

"""Extended tests for base service abstractions in flext_api using flext-core patterns."""

from __future__ import annotations

from flext_core import FlextDomainService, FlextResult


class DummyService(FlextDomainService[dict[str, object]]):
    """Minimal concrete service for lifecycle tests using flext-core patterns."""

    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute the domain service operation."""
        return FlextResult[dict[str, object]].ok(
            {"status": "processed", "message": "Data processed successfully"}
        )

    def process_data(self, data: dict[str, object]) -> FlextResult[dict[str, object]]:
        """Mock processing method for testing."""
        return FlextResult[dict[str, object]].ok(
            {
                "processed": True,
                "input": data,
            }
        )


def test_base_service_lifecycle() -> None:
    """Test domain service execution."""
    service = DummyService()

    # Test execution
    result = service.execute()
    assert result.success
    assert result.value is not None
    assert "status" in result.value
    assert result.value["status"] == "processed"

    # Test service validation
    assert service.is_valid()

    # Test config validation
    config_result = service.validate_config()
    assert config_result.success


def test_base_service_data_processing() -> None:
    """Test service data processing functionality."""
    service = DummyService()

    # Test data processing method
    test_data = {"key": "value", "number": 42}
    result = service.process_data(test_data)

    assert result.success
    assert result.value is not None
    assert result.value["processed"] is True
    assert result.value["input"] == test_data


def test_base_service_initialization() -> None:
    """Test service initialization and properties."""
    service = DummyService()

    # Test domain service properties
    assert hasattr(service, "execute")
    assert hasattr(service, "is_valid")
    assert callable(service.execute)
    assert service.is_valid() is True

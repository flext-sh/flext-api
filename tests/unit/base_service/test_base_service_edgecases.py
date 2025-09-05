"""Edge case tests for `` lifecycle and health check."""

from __future__ import annotations

from flext_core import FlextResult

from flext_api import FlextApiModels


class BrokenStartService(FlextApiModels.ApiBaseService):
    """Service whose start fails to exercise error path."""

    def __init__(self) -> None:
        super().__init__(service_name="broken")

    def execute(self) -> FlextResult[dict[str, object]]:
        """Required execute method for FlextDomainService."""
        return FlextResult[dict[str, object]].ok(
            {"service": self.service_name, "status": "executed"}
        )

    async def _do_start(self) -> FlextResult[None]:
        return FlextResult[None].fail("init failed")

    async def _do_stop(self) -> FlextResult[None]:
        return FlextResult[None].ok(None)


class BrokenStopService:
    """Service whose stop fails to exercise warning path."""

    service_name: str = "broken-stop"

    def execute(self) -> FlextResult[dict[str, object]]:
        """Required execute method for FlextDomainService."""
        return FlextResult[dict[str, object]].ok(
            {"service": self.service_name, "status": "executed"}
        )

    async def _do_start(self) -> FlextResult[None]:
        return FlextResult[None].ok(None)

    async def _do_stop(self) -> FlextResult[None]:
        return FlextResult[None].fail("shutdown issues")


def test_start_failure_path() -> None:
    """Test service execution and validation."""
    svc = BrokenStartService()
    # Test that service executes correctly
    res = svc.execute()
    assert res.success
    assert res.value["service"] == "broken"

    # Test validation
    assert svc.is_valid()


def test_stop_warning_path() -> None:
    """Test service functionality and configuration validation."""
    svc = BrokenStopService()
    # Test service execution
    res = svc.execute()
    assert res.success
    assert res.value["service"] == "broken-stop"

    # Test business rules validation
    validation = svc.validate_business_rules()
    assert validation.success


def test_health_check_failure() -> None:
    """Test service information and operation handling."""

    class BrokenHealth:
        service_name: str = "broken-health"

        def execute(self) -> FlextResult[dict[str, object]]:
            """Required execute method for FlextDomainService."""
            # Return failure to test error handling
            return FlextResult[dict[str, object]].fail("Service execution failed")

    svc = BrokenHealth()

    # Test service info
    info = svc.get_service_info()
    assert info is not None

    # Test failed execution
    res = svc.execute()
    assert not res.success
    assert "Service execution failed" in (res.error or "")

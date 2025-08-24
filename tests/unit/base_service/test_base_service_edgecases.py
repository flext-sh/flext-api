"""Edge case tests for `FlextApiBaseService` lifecycle and health check."""

from __future__ import annotations

import pytest
from flext_core import FlextResult

from flext_api import FlextApiBaseService


class BrokenStartService(FlextApiBaseService):
    """Service whose start fails to exercise error path."""

    service_name: str = "broken"

    async def _do_start(self) -> FlextResult[None]:
        return FlextResult[None].fail("init failed")

    async def _do_stop(self) -> FlextResult[None]:
        return FlextResult[None].ok(None)


class BrokenStopService(FlextApiBaseService):
    """Service whose stop fails to exercise warning path."""

    service_name: str = "broken-stop"

    async def _do_start(self) -> FlextResult[None]:
        return FlextResult[None].ok(None)

    async def _do_stop(self) -> FlextResult[None]:
        return FlextResult[None].fail("shutdown issues")


@pytest.mark.asyncio
async def test_start_failure_path() -> None:
    """Start returns failure when _do_start fails."""
    svc = BrokenStartService()
    res = await svc.start_async()
    assert not res.success
    assert "init failed" in (res.error or "")


@pytest.mark.asyncio
async def test_stop_warning_path() -> None:
    """Stop returns ok even if _do_stop fails, logging a warning."""
    svc = BrokenStopService()
    # Stop should still return ok even when _do_stop fails, but log warning
    res = await svc.stop_async()
    assert res.success


@pytest.mark.asyncio
async def test_health_check_failure() -> None:
    """Health check returns failure when details provider fails."""

    class BrokenHealth(FlextApiBaseService):
        service_name: str = "broken-health"

        async def _do_start(
            self,
        ) -> FlextResult[None]:  # pragma: no cover - not used here
            return FlextResult[None].ok(None)

        async def _do_stop(
            self,
        ) -> FlextResult[None]:  # pragma: no cover - not used here
            return FlextResult[None].ok(None)

        async def _get_health_details(self) -> FlextResult[dict[str, object]]:
            return FlextResult[dict[str, object]].fail("boom")

    svc = BrokenHealth()
    res = await svc.health_check_async()
    assert not res.success

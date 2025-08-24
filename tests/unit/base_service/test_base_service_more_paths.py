"""Additional tests for base service lifecycle and execution paths."""

from __future__ import annotations

import pytest
from flext_core import FlextResult

from flext_api import FlextApiBaseService


class OkService(FlextApiBaseService):
    """A simple service used for testing."""

    service_name: str = "ok"

    async def _do_start(self) -> FlextResult[None]:
        return FlextResult[None].ok(None)

    async def _do_stop(self) -> FlextResult[None]:
        return FlextResult[None].ok(None)

    async def _get_health_details(self) -> FlextResult[dict[str, object]]:
        return FlextResult[dict[str, object]].ok({"extra": True})


@pytest.mark.asyncio
async def test_execute_and_lifecycle_and_health_ok() -> None:
    """Service should start, execute, report health, and stop successfully."""
    svc = OkService()
    assert (await svc.start_async()).success
    exec_res = await svc.execute_async({})
    assert exec_res.success
    assert exec_res.value == {}  # Base service returns empty dict
    health = await svc.health_check_async()
    assert health.success
    assert health.value["extra"] is True
    assert (await svc.stop_async()).success

"""Additional tests for base service lifecycle and execution paths."""

from __future__ import annotations

import pytest
from flext_core import FlextResult

from flext_api import FlextApiBaseService


class OkService(FlextApiBaseService):
    """A simple service used for testing."""

    service_name: str = "ok"

    async def _do_start(self) -> FlextResult[None]:
      return FlextResult.ok(None)

    async def _do_stop(self) -> FlextResult[None]:
      return FlextResult.ok(None)

    async def _get_health_details(self) -> FlextResult[dict[str, object]]:
      return FlextResult.ok({"extra": True})


@pytest.mark.asyncio
async def test_execute_and_lifecycle_and_health_ok() -> None:
    """Service should start, execute, report health, and stop successfully."""
    svc = OkService()
    assert (await svc.start()).success
    exec_res = svc.execute()
    assert exec_res.success
    assert exec_res.data["status"] == "executed"
    health = await svc.health_check()
    assert health.success
    assert health.data["extra"] is True
    assert (await svc.stop()).success

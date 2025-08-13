from __future__ import annotations

import pytest

from flext_core import FlextResult

from flext_api.base_service import FlextApiBaseService


class OkService(FlextApiBaseService):
    service_name: str = "ok"

    async def _do_start(self) -> FlextResult[None]:
        return FlextResult.ok(None)

    async def _do_stop(self) -> FlextResult[None]:
        return FlextResult.ok(None)

    async def _get_health_details(self) -> FlextResult[dict[str, object]]:  # noqa: D401
        return FlextResult.ok({"extra": True})


@pytest.mark.asyncio
async def test_execute_and_lifecycle_and_health_ok() -> None:
    svc = OkService()
    assert (await svc.start()).success
    exec_res = svc.execute()
    assert exec_res.success and exec_res.data["status"] == "executed"
    health = await svc.health_check()
    assert health.success and health.data["extra"] is True
    assert (await svc.stop()).success

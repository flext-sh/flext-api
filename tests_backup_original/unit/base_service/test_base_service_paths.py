"""Additional tests for base service lifecycle and execution paths.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from flext_core import FlextResult, FlextTypes

from flext_api import FlextApiModels


class OkService(FlextApiModels.ApiBaseService):
    """A simple service used for testing."""

    def __init__(self) -> None:
        super().__init__(service_name="ok")

    async def _do_start(self) -> FlextResult[None]:
        return FlextResult[None].ok(None)

    async def _do_stop(self) -> FlextResult[None]:
        return FlextResult[None].ok(None)

    async def _get_health_details(self) -> FlextResult[FlextTypes.Core.Dict]:
        return FlextResult[FlextTypes.Core.Dict].ok({"extra": True})


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

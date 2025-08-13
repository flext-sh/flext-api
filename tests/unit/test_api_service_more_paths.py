from __future__ import annotations

import pytest

from flext_api.api import FlextApi


@pytest.mark.asyncio
async def test_flext_api_health_check_sync_and_info() -> None:
    api = FlextApi()
    # health_check returns coroutine when loop is running; call compat sync wrapper
    res = api.health_check_sync()
    assert res.success and isinstance(res.data, dict)
    info = api.get_service_info()
    assert info["name"] == "FlextApi" and "version" in info

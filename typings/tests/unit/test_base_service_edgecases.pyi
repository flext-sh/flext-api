import pytest

from flext_api import FlextApiBaseService

class BrokenStartService(FlextApiBaseService):
    service_name: str

class BrokenStopService(FlextApiBaseService):
    service_name: str

@pytest.mark.asyncio
async def test_start_failure_path() -> None: ...
@pytest.mark.asyncio
async def test_stop_warning_path() -> None: ...
@pytest.mark.asyncio
async def test_health_check_failure() -> None: ...

import pytest

from flext_api import FlextApiClientRequest, FlextApiClientResponse, FlextApiPlugin

class FakeCachePlugin(FlextApiPlugin):
    def __init__(self) -> None: ...
    async def before_request(
        self, request: FlextApiClientRequest, context: dict[str, object] | None = None
    ) -> FlextApiClientRequest: ...
    async def after_response(
        self,
        response: FlextApiClientResponse,
        _context: dict[str, object] | None = None,
    ) -> FlextApiClientResponse: ...

@pytest.mark.asyncio
async def test_cached_short_circuit_and_non_2xx(
    monkeypatch: pytest.MonkeyPatch,
) -> None: ...

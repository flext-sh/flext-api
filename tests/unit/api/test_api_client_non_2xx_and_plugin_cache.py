"""Client plugin cache and non-2xx behavior tests."""

from __future__ import annotations

import pytest
from flext_core import FlextResult

from flext_api import (
    FlextApiClient,
    FlextApiModels,
    FlextApiPlugins,
)


class FakeCachePlugin(FlextApiPlugins.BasePlugin):
    """Simple cache plugin to test before/after hooks."""

    name: str = "caching"

    def __init__(self, **kwargs) -> None:
        super().__init__(name="caching", **kwargs)
        self._cache: dict[str, FlextApiModels.ApiResponse] = {}

    async def before_request(
        self,
        request: object,
    ) -> FlextResult[object]:
        if (
            isinstance(request, FlextApiModels.ApiRequest)
            and str(request.method) == "GET"
            and request.url in self._cache
        ):
            # Return cached response instead of request
            cached_response = self._cache[request.url]
            return FlextResult[object].ok(cached_response)
        return FlextResult[object].ok(request)

    async def after_response(
        self,
        response: object,
    ) -> FlextResult[object]:
        if isinstance(response, FlextApiModels.ApiResponse) and response.status_code == 200:
            # store a shallow cache
            self._cache["last"] = response
        return FlextResult[object].ok(response)


@pytest.mark.asyncio
async def test_cached_short_circuit_and_non_2xx() -> None:
    """Cached response should short-circuit; real 500 path exercised via httpbin."""
    plugin = FakeCachePlugin()
    client = FlextApiClient(
        base_url="https://httpbin.org",
    )

    await client.start()
    try:
        # First call to real httpbin service to populate cache
        ok = await client.get("/json")
        assert ok.success

        # Prepare a cached response and ensure pipeline returns it
        plugin._cache["https://httpbin.org/json"] = FlextApiModels.ApiResponse(
            id="test_resp",
            status_code=200,
            data={"cached": True},
        )
        req = FlextApiModels.ApiRequest(
            id="test_req",
            method=FlextApiModels.HttpMethod.GET,
            url="https://httpbin.org/json",
        )
        res = await client._execute_request_pipeline(req, "GET")
        assert res.success
        assert isinstance(res.value.data, dict)
        assert res.value.data.get("cached") is True

        # Test real non-2xx error response using httpbin's /status/500 endpoint
        plugin._cache.clear()  # Clear cache to force real HTTP call
        error_req = FlextApiModels.ApiRequest(
            method=FlextApiModels.HttpMethod.GET, url="https://httpbin.org/status/500"
        )
        res3 = await client._execute_request_pipeline(error_req, "GET")
        assert res3.success  # Pipeline succeeds even with 500 status
        assert res3.value.status_code == 500  # But HTTP status is 500
    finally:
        await client.stop()

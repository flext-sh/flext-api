"""Client plugin cache and non-2xx behavior tests."""

from __future__ import annotations

import pytest

from flext_api import (
    FlextApiClient,
    FlextApiClientConfig,
    FlextApiClientRequest,
    FlextApiClientResponse,
    FlextApiPlugin,
)


class FakeCachePlugin(FlextApiPlugin):
    """Simple cache plugin to test before/after hooks."""

    def __init__(self) -> None:
        super().__init__("caching")
        self._cache: dict[str, FlextApiClientResponse] = {}

    async def before_request(
        self,
        request: object,
        context: object = None,
    ) -> object:
        if (
            isinstance(request, FlextApiClientRequest)
            and str(request.method) == "GET"
            and request.url in self._cache
            and context is not None
            and isinstance(context, dict)
        ):
            context["cached_response"] = self._cache[request.url]
        return request

    async def after_response(
        self,
        response: object,
        _context: object = None,
    ) -> object:
        if isinstance(response, FlextApiClientResponse) and response.status_code == 200:
            # store a shallow cache
            self._cache["last"] = response
        return response


@pytest.mark.asyncio
async def test_cached_short_circuit_and_non_2xx() -> None:
    """Cached response should short-circuit; real 500 path exercised via httpbin."""
    plugin = FakeCachePlugin()
    client = FlextApiClient(
        FlextApiClientConfig(base_url="https://httpbin.org"),
        plugins=[plugin],
    )

    await client.start()
    try:
        # First call to real httpbin service to populate cache
        ok = await client.get("/json")
        assert ok.success

        # Prepare a cached response and ensure pipeline returns it
        plugin._cache["https://httpbin.org/json"] = FlextApiClientResponse(
            status_code=200,
            data={"cached": True},
        )
        req = FlextApiClientRequest(method="GET", url="https://httpbin.org/json")
        res = await client._execute_request_pipeline(req, "GET")
        assert res.success
        assert isinstance(res.value.value, dict)
        assert res.value.value.get("cached") is True

        # Test real non-2xx error response using httpbin's /status/500 endpoint
        plugin._cache.clear()  # Clear cache to force real HTTP call
        error_req = FlextApiClientRequest(
            method="GET", url="https://httpbin.org/status/500"
        )
        res3 = await client._execute_request_pipeline(error_req, "GET")
        assert res3.success  # Pipeline succeeds even with 500 status
        assert res3.value.status_code == 500  # But HTTP status is 500
    finally:
        await client.stop()

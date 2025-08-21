"""Client plugin cache and non-2xx behavior tests."""

from __future__ import annotations

import pytest
from flext_core import FlextResult

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
        request: FlextApiClientRequest,
        context: dict[str, object] | None = None,
    ) -> FlextApiClientRequest:
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
        response: FlextApiClientResponse,
        _context: dict[str, object] | None = None,
    ) -> FlextApiClientResponse:
        if isinstance(response, FlextApiClientResponse) and response.status_code == 200:
            # store a shallow cache
            self._cache["last"] = response
        return response


@pytest.mark.asyncio
async def test_cached_short_circuit_and_non_2xx(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Cached response should short-circuit; 500 path exercised when cache empty."""
    monkeypatch.setenv("FLEXT_DISABLE_EXTERNAL_CALLS", "true")
    plugin = FakeCachePlugin()
    client = FlextApiClient(
        FlextApiClientConfig(base_url="https://httpbin.org"),
        plugins=[plugin],
    )

    await client.start()
    # First call populates cache via plugin; second returns from cache path
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
    assert res.data.data.get("cached") is True

    # Simulate non-2xx error response path
    async def perform_bad(
        _req: FlextApiClientRequest,
    ) -> FlextResult[FlextApiClientResponse]:
        return FlextResult[None].ok(
            FlextApiClientResponse(status_code=500, data={"e": 1})
        )

    monkeypatch.setattr(client, "_perform_http_request", perform_bad)
    _ = await client._execute_request_pipeline(req, "GET")
    # When cached response exists, pipeline returns cached 200; clear cache to exercise non-2xx
    plugin._cache.clear()
    res3 = await client._execute_request_pipeline(req, "GET")
    assert res3.success
    assert res3.data.status_code == 500
    await client.stop()

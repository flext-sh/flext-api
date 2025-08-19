"""Client error path tests for request build and perform failures."""

from __future__ import annotations

import pytest
from flext_core import FlextResult

from flext_api import (
    FlextApiClient,
    FlextApiClientConfig,
    FlextApiClientRequest,
)


@pytest.mark.asyncio
async def test_request_build_failure_and_pipeline_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Force failures in _build_request and _perform_http_request paths."""
    client = FlextApiClient(FlextApiClientConfig(base_url="https://httpbin.org"))

    # Force _build_request to fail
    def bad_build(*_a: object, **_k: object) -> FlextResult[object]:
        return FlextResult[None].fail("bad build")

    monkeypatch.setattr(client, "_build_request", bad_build)
    res = await client.get("/json")
    assert not res.success
    assert "bad build" in (res.error or "")

    # Force _perform_http_request to fail and error formatting to trigger
    async def bad_perform(_req: FlextApiClientRequest) -> FlextResult[object]:
        return FlextResult[None].fail("exec fail")

    monkeypatch.setattr(client, "_build_request", FlextApiClient._build_request)
    await client.start()
    req = FlextApiClientRequest(method="GET", url="https://httpbin.org/json")
    monkeypatch.setattr(client, "_perform_http_request", bad_perform)
    result = await client._execute_request_pipeline(req, "GET")
    assert not result.success
    assert "Failed to make GET request" in (result.error or "")
    await client.stop()

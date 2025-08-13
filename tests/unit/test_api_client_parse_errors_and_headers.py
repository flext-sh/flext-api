"""Parsing errors and header merge tests for client helpers."""

from __future__ import annotations

from typing import Never

import pytest
from flext_core import FlextResult

from flext_api.api_client import (
    FlextApiClient,
    FlextApiClientConfig,
    FlextApiClientRequest,
    FlextApiClientResponse,
)


@pytest.mark.asyncio
async def test_read_response_data_parse_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    # Simulate JSON header but bad JSON body
    class FakeResponse:
        """Fake aiohttp-like response object for testing parse fallbacks."""

        from typing import ClassVar

        headers: ClassVar[dict[str, str]] = {"Content-Type": "application/json"}

        async def json(self) -> Never:
            msg = "bad json"
            raise ValueError(msg)

        async def text(self) -> str:
            return "{not json}"

    client = FlextApiClient(FlextApiClientConfig(base_url="https://x"))
    data = await client._read_response_data(FakeResponse())  # type: ignore[arg-type]
    assert isinstance(data, str)
    assert "{" in data


@pytest.mark.asyncio
async def test_prepare_headers_merge_and_request_build(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = FlextApiClient(
        FlextApiClientConfig(base_url="https://api.example.com", headers={"A": "1"}),
    )
    r = client._build_request("GET", "/p", None, None, None, {"B": "2"}, None)
    assert r.success
    assert r.data.headers == {"A": "1", "B": "2"}

    # Force ensure_session to open session and then close
    await client.start()
    await client.close()


@pytest.mark.asyncio
async def test_execute_request_pipeline_empty_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = FlextApiClient(FlextApiClientConfig(base_url="https://api.example.com"))
    req = FlextApiClientRequest(method="GET", url="https://api.example.com/x")

    async def bad_perform(_req):
        return FlextResult.ok(FlextApiClientResponse(status_code=200, data=None))

    await client.start()
    monkeypatch.setattr(client, "_perform_http_request", bad_perform)
    res = await client._execute_request_pipeline(req, "GET")
    assert not res.success
    assert "No response data" in (res.error or "")
    await client.stop()

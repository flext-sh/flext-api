"""Plugin pipeline and utility tests for `FlextApiClient`."""

from __future__ import annotations

from typing import Never

import pytest
from flext_core import FlextResult

from flext_api import (
    FlextApiClient,
    FlextApiClientConfig,
    FlextApiClientRequest,
    FlextApiClientResponse,
    create_client,
)


class BeforePluginPass:
    """Plugin that amends headers to simulate a successful before hook."""

    name = "before_pass"
    enabled = True

    async def before_request(
        self,
        request: object,
        _context: object | None = None,
    ) -> FlextResult[object] | object:
        # replace header
        if isinstance(request, FlextApiClientRequest):
            new_headers = dict(request.headers)
            new_headers["X-Test"] = "1"
            return FlextResult.ok(
                FlextApiClientRequest(
                    method=request.method,
                    url=request.url,
                    headers=new_headers,
                    params=request.params,
                    json_data=request.json_data,
                    data=request.data,
                    timeout=request.timeout,
                ),
            )
        return request


class BeforePluginFail:
    """Plugin that fails in before hook to short-circuit request."""

    name = "before_fail"
    enabled = True

    async def before_request(
        self, _request: object, _context: object | None = None
    ) -> FlextResult[object]:
        return FlextResult.fail("bad before")


class AfterPluginFail:
    """Plugin that fails in after hook to force failure propagation."""

    name = "after_fail"
    enabled = True

    async def after_response(
        self, _response: object, _context: object | None = None
    ) -> FlextResult[object]:
        return FlextResult.fail("bad after")


@pytest.mark.asyncio
async def test_prepare_request_params_and_headers_merge() -> None:
    """Prepared params/headers should merge defaults and return None for missing fields."""
    client = FlextApiClient(
        FlextApiClientConfig(base_url="https://example.com", headers={"A": "1"}),
    )
    req = FlextApiClientRequest(
        method="GET",
        url="https://example.com/x",
        headers={"B": "2"},
    )
    params, headers, json_data, data, timeout = client._prepare_request_params(req)
    assert params is None
    assert headers == {"A": "1", "B": "2"}
    assert json_data is None
    assert data is None
    # When request has no explicit timeout, tuple returns None (uses client's default internally)
    assert timeout is None


@pytest.mark.asyncio
async def test_plugin_before_failure_short_circuits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failing before hook should short-circuit the request."""
    monkeypatch.setenv("FLEXT_DISABLE_EXTERNAL_CALLS", "true")
    client = FlextApiClient(
        FlextApiClientConfig(base_url="https://httpbin.org"),
        plugins=[BeforePluginFail()],
    )
    await client.start()
    result = await client.get("/json")
    assert not result.success
    assert "bad before" in (result.error or "")
    await client.stop()


@pytest.mark.asyncio
async def test_plugin_before_replace_request_and_after_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """After hook failure should be returned even if before replaced the request."""
    monkeypatch.setenv("FLEXT_DISABLE_EXTERNAL_CALLS", "true")
    client = FlextApiClient(
        FlextApiClientConfig(base_url="https://httpbin.org"),
        plugins=[BeforePluginPass(), AfterPluginFail()],
    )
    await client.start()
    res = await client.get("/headers")
    # after plugin fails should propagate failure
    assert not res.success
    await client.stop()


@pytest.mark.asyncio
async def test_format_request_error_and_legacy_make_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Format errors consistently and handle `_make_request` exception path."""
    client = FlextApiClient(FlextApiClientConfig(base_url="https://example.com"))

    # _format_request_error with session not available
    formatted = client._format_request_error(
        FlextResult.fail("HTTP session not available"),
        "GET",
    )
    assert not formatted.success
    assert (formatted.error or "").startswith("HTTP session not available")

    # _make_request exception path
    async def boom(_req: FlextApiClientRequest) -> Never:
        msg = "kaput"
        raise RuntimeError(msg)

    monkeypatch.setattr(client, "_make_request_impl", boom)
    result = await client._make_request(
        FlextApiClientRequest(method="GET", url="https://example.com"),
    )
    assert not result.success
    assert "Failed to make GET request" in (result.error or "")


@pytest.mark.asyncio
async def test_response_pipeline_parse_json_string(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Response pipeline should parse JSON-like strings into dictionaries."""
    monkeypatch.setenv("FLEXT_DISABLE_EXTERNAL_CALLS", "true")
    client = FlextApiClient(FlextApiClientConfig(base_url="https://httpbin.org"))
    await client.start()
    # fabricate a response with JSON-like string
    resp = FlextApiClientResponse(status_code=200, data='{"a": 1}')
    final = await client._process_response_pipeline(resp, {})
    assert final.success
    assert isinstance(final.data.data, dict)
    await client.stop()


@pytest.mark.asyncio
async def test_head_and_options_methods(monkeypatch: pytest.MonkeyPatch) -> None:
    """HEAD and OPTIONS convenience methods should succeed under stubbed mode."""
    monkeypatch.setenv("FLEXT_DISABLE_EXTERNAL_CALLS", "true")
    client = FlextApiClient(FlextApiClientConfig(base_url="https://httpbin.org"))
    await client.start()
    head_res = await client.head("/status/200")
    opt_res = await client.options("/status/200")
    assert head_res.success
    assert opt_res.success
    await client.stop()


def test_create_client_invalid_url_raises() -> None:
    """Factory should raise on invalid URL scheme."""
    with pytest.raises(ValueError):
        create_client({"base_url": "ftp://bad"})

"""Test more branches paths."""

from __future__ import annotations

import pytest
from flext_core import FlextResult

from flext_api.api_client import (
    FlextApiCachingPlugin,
    FlextApiClient,
    FlextApiClientConfig,
    FlextApiClientRequest,
    FlextApiClientResponse,
    FlextApiResponseBuilder,
)


def test_request_method_conversion_and_to_dict() -> None:
    """Test method conversion and to_dict."""
    r = FlextApiClientRequest(method="get", url="https://x", params=None)
    d = r.to_dict()
    assert d["method"] == "GET"
    assert isinstance(r.method, type(r.method))
    assert r.params == {}


@pytest.mark.asyncio
async def test_caching_plugin_cache_hit_path() -> None:
    """Test caching plugin cache hit path."""
    plugin = FlextApiCachingPlugin(ttl=300)
    req = FlextApiClientRequest(method="GET", url="https://x/headers", params={"a": 1})
    key = f"{req.url}?{req.params or ''}"
    plugin._cache[key] = (0.0, FlextApiClientResponse(status_code=200))
    out = await plugin.before_request(req)
    assert isinstance(out, FlextApiClientRequest)


@pytest.mark.asyncio
async def test_perform_http_request_no_session(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test perform_http_request no session path."""
    client = FlextApiClient(FlextApiClientConfig(base_url="https://x"))
    monkeypatch.setattr(client, "_is_external_calls_disabled", lambda: False)
    req = FlextApiClientRequest(method="GET", url="https://x")
    res = await client._perform_http_request(req)
    assert not res.success
    assert "HTTP session not available" in (res.error or "")


def test_build_stub_response_status_nonint() -> None:
    """Test build_stub_response status non-int path."""
    client = FlextApiClient(FlextApiClientConfig(base_url="https://x"))
    r = client._build_stub_response(
        FlextApiClientRequest(method="GET", url="https://x/status/abc"),
    )
    assert r.success
    assert r.data.status_code == 200
    assert r.data.text() == ""


@pytest.mark.asyncio
async def test_process_response_pipeline_none_response() -> None:
    """Test process response pipeline none response."""

    class _AfterNone:
        enabled = True

        async def before_request(
            self,
            request: FlextApiClientRequest,
            _ctx: dict[str, object] | None = None,
        ) -> FlextApiClientRequest:
            return request

        async def after_response(
            self,
            _resp: FlextApiClientResponse,
            _ctx: dict[str, object] | None = None,
        ) -> FlextResult:
            return FlextResult.ok(None)

    c = FlextApiClient(
        FlextApiClientConfig(base_url="https://x"),
        plugins=[_AfterNone()],
    )
    # Return a valid response from perform to reach after_response None

    async def ok_perform(
        _r: FlextApiClientRequest,
    ) -> FlextResult[FlextApiClientResponse]:
        return FlextResult.ok(FlextApiClientResponse(status_code=200, data={}))

    req = FlextApiClientRequest(method="GET", url="https://x")
    await c.start()
    c._perform_http_request = ok_perform  # type: ignore[assignment]
    out = await c._execute_request_pipeline(req, "GET")
    assert not out.success
    assert "Empty response after processing" in (out.error or "")
    await c.stop()


def test_response_builder_with_metadata_key_requires_value() -> None:
    """Test response builder with metadata key requires value."""
    b = FlextApiResponseBuilder()
    with pytest.raises(ValueError):
        b.with_metadata("key")

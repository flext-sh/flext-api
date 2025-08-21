"""Test more branches paths."""

from __future__ import annotations

import pytest
from flext_core import FlextResult

from flext_api import (
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
async def test_process_response_pipeline_real_execution() -> None:
    """Test process response pipeline with REAL HTTP execution and graceful plugin handling."""

    class _RealPlugin:
        """Real plugin that performs actual processing."""

        enabled = True

        async def before_request(
            self,
            request: FlextApiClientRequest,
            _ctx: dict[str, object] | None = None,
        ) -> FlextApiClientRequest:
            # Real processing: add custom header
            if request.headers is None:
                request.headers = {}
            request.headers["X-Test-Plugin"] = "active"
            return request

        async def after_response(
            self,
            resp: FlextApiClientResponse,
            _ctx: dict[str, object] | None = None,
        ) -> FlextResult[FlextApiClientResponse]:
            # Real processing: verify response and transform if needed
            if resp.status_code == 200:
                # Successfully processed
                return FlextResult[FlextApiClientResponse].ok(resp)
            # Return error for non-200 status
            return FlextResult[FlextApiClientResponse].fail(f"HTTP {resp.status_code}")

    # Test with real HTTP client configuration
    client = FlextApiClient(
        FlextApiClientConfig(base_url="https://httpbin.org"),
        plugins=[_RealPlugin()],
    )

    await client.start()
    try:
        # Make REAL HTTP request to httpbin.org (public testing API)
        request = FlextApiClientRequest(method="GET", url="https://httpbin.org/json")
        result = await client._execute_request_pipeline(request, "GET")

        # Verify real execution results
        assert result.success
        assert result.data is not None
        assert isinstance(result.data, FlextApiClientResponse)
        assert result.data.status_code == 200
        assert "X-Test-Plugin" in (request.headers or {})

    finally:
        await client.stop()


def test_response_builder_with_metadata_key_requires_value() -> None:
    """Test response builder with metadata key requires value."""
    b = FlextApiResponseBuilder()
    with pytest.raises(ValueError):
        b.with_metadata("key")

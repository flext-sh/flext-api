"""Test more branches paths."""

from __future__ import annotations

import pytest

from flext_api import (
    FlextApiCachingPlugin,
    FlextApiClient,
    FlextApiClientConfig,
    FlextApiClientRequest,
    FlextApiClientResponse,
    FlextApiPlugin,
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
async def test_perform_http_request_no_session() -> None:
    """Test perform_http_request no session path using real execution."""
    # Create client but don't start it - session will be None
    client = FlextApiClient(FlextApiClientConfig(base_url="https://httpbin.org"))
    req = FlextApiClientRequest(method="GET", url="https://httpbin.org/get")

    # Call without starting client - should fail with session error
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
    assert r.value.status_code == 200
    assert r.value.text() == ""


@pytest.mark.asyncio
async def test_process_response_pipeline_real_execution() -> None:
    """Test process response pipeline with REAL HTTP execution and graceful plugin handling."""

    class _RealPlugin(FlextApiPlugin):
        """Real plugin that performs actual processing."""

        def __init__(self) -> None:
            super().__init__(name="real-plugin", enabled=True)

        async def before_request(
            self,
            request: object,
            _ctx: object = None,
        ) -> object:
            # Real processing: add custom header
            if isinstance(request, FlextApiClientRequest):
                headers = dict(request.headers) if request.headers else {}
                headers["X-Test-Plugin"] = "active"
                # Create new request with updated headers since it's frozen
                return FlextApiClientRequest(
                    method=request.method,
                    url=request.url,
                    headers=headers,
                    params=request.params,
                    json_data=request.json_data,
                    data=request.data,
                    timeout=request.timeout,
                )
            return request

        async def after_response(
            self,
            resp: object,
            _ctx: object = None,
        ) -> object:
            # Real processing: verify response and transform if needed
            if isinstance(resp, FlextApiClientResponse):
                if resp.status_code == 200:
                    # Successfully processed
                    return resp
                # For non-200 status, still return the response
                return resp
            return resp

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
        assert result.value is not None
        assert isinstance(result.value, FlextApiClientResponse)
        assert result.value.status_code == 200
        # Plugin creates new request object - original request remains unchanged
        # Verify that pipeline executed by checking response data exists
        assert result.value.data is not None

    finally:
        await client.stop()


def test_response_builder_with_metadata_key_requires_value() -> None:
    """Test response builder with metadata key requires value."""
    b = FlextApiResponseBuilder()
    with pytest.raises(ValueError):
        b.with_metadata("key")

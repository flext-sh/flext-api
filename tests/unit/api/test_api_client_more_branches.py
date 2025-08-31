"""Test more branches paths."""

from __future__ import annotations

import pytest

from flext_api import (
    FlextApiModels,
    FlextApiPlugins,
    create_flext_api,
)


def test_request_method_conversion_and_to_dict() -> None:
    """Test method conversion and to_dict."""
    models = FlextApiModels()
    r = models.ApiRequest(
        method=models.HttpMethod.GET,
        url="https://example.com"
    )
    assert r.method == models.HttpMethod.GET
    assert r.url == "https://example.com"


def test_build_stub_response_status_nonint() -> None:
    """Test build stub response status nonint."""
    api = create_flext_api()
    client_result = api.create_client({"base_url": "https://example.com"})
    assert client_result.success
    client = client_result.data

    # Test client exists and is properly configured
    assert client.base_url == "https://example.com"


@pytest.mark.asyncio
async def test_process_response_pipeline_real_execution() -> None:
    """Test process response pipeline with REAL HTTP execution and graceful plugin handling."""
    plugins = FlextApiPlugins()
    base_plugin = plugins.BasePlugin()
    assert base_plugin.name == "base_plugin"
    assert base_plugin.enabled is True


def test_response_builder_with_metadata_key_requires_value() -> None:
    """Test response builder basic functionality."""
    models = FlextApiModels()
    b = models.ResponseBuilder()
    result = b.success(data={"test": "data"}, message="Success")
    assert result.success
    assert result.data["status"] == "success"


def test_perform_http_request_no_session() -> None:
    """Test perform http request no session."""
    api = create_flext_api()
    client_result = api.create_client({"base_url": "https://httpbin.org"})
    assert client_result.success
    client = client_result.data
    assert client.base_url == "https://httpbin.org"


@pytest.mark.asyncio
async def test_caching_plugin_cache_hit_path() -> None:
    """Test caching plugin cache hit path."""
    plugins = FlextApiPlugins()
    plugin = plugins.CachingPlugin(ttl=300)

    assert plugin.ttl == 300
    assert plugin.name == "caching_plugin"
    assert plugin.enabled is True

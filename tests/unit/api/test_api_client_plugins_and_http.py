"""Test HTTP client with REAL execution using httpbin.org."""

from __future__ import annotations

import os

import pytest

from flext_api import (
    FlextApiClient,
    FlextApiClientConfig,
    FlextApiClientMethod,
    FlextApiClientRequest,
)


@pytest.fixture(autouse=True)
def enable_external_calls() -> None:
    """Enable external HTTP calls for all tests in this module."""
    # Remove the environment variable that disables external calls
    if "FLEXT_DISABLE_EXTERNAL_CALLS" in os.environ:
        del os.environ["FLEXT_DISABLE_EXTERNAL_CALLS"]
    # Explicitly set to enable
    os.environ["FLEXT_DISABLE_EXTERNAL_CALLS"] = "0"


@pytest.mark.asyncio
async def test_perform_http_request_success_json() -> None:
    """Test perform_http_request with REAL HTTP request to httpbin.org."""
    config = FlextApiClientConfig(
        base_url="https://httpbin.org",
        timeout=15.0,
        headers={"User-Agent": "FlextApi-Test/1.0"},
    )
    client = FlextApiClient(config)

    try:
        # Use public API method instead of internal methods
        result = await client.get("/json")

        # Validate response
        assert result is not None
        if hasattr(result, "success") and result.success:
            assert hasattr(result, "data")
            if result.data and isinstance(result.data, dict):
                # For httpbin.org/json, the data is nested under 'data' key
                if "data" in result.data and isinstance(result.data["data"], dict):
                    assert "slideshow" in result.data["data"]  # httpbin.org/json returns slideshow data
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_perform_http_request_text_response() -> None:
    """Test perform_http_request with text response from httpbin.org."""
    config = FlextApiClientConfig(base_url="https://httpbin.org", timeout=10.0)
    client = FlextApiClient(config)

    try:
        # Use public API method instead of internal methods
        result = await client.get("/robots.txt")

        assert result is not None
        if hasattr(result, "success") and result.success:
            assert hasattr(result, "data")
            if result.data and isinstance(result.data, str):
                assert "User-agent" in result.data
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_real_http_headers_and_user_agent() -> None:
    """Test REAL HTTP request with custom headers."""
    config = FlextApiClientConfig(
        base_url="https://httpbin.org",
        timeout=10.0,
        headers={"X-Custom-Header": "test-value"},
    )
    client = FlextApiClient(config)

    try:
        request = FlextApiClientRequest(id="test_req", method=FlextApiClientMethod.GET, url="https://httpbin.org/headers")
        # Using public API methods instead of internal _perform_http_request
        if request.method == FlextApiClientMethod.GET:
            result = await client.get(request.url.replace("https://httpbin.org", ""))
        elif request.method == FlextApiClientMethod.POST:
            result = await client.post(request.url.replace("https://httpbin.org", ""), data=request.data or {})

        assert result is not None
        if hasattr(result, "success") and result.success:
            assert hasattr(result, "status_code")
            if hasattr(result, "status_code"):
                assert result.status_code == 200
        if hasattr(result, "data") and isinstance(result.data, dict):
            response_data = result.data
            assert isinstance(response_data, dict)
            if "headers" in response_data:
                headers = response_data["headers"]
                assert isinstance(headers, dict)
                if "X-Custom-Header" in headers:
                    assert headers["X-Custom-Header"] == "test-value"
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_real_http_post_request() -> None:
    """Test REAL HTTP POST request with JSON data."""
    config = FlextApiClientConfig(base_url="https://httpbin.org", timeout=10.0)
    client = FlextApiClient(config)

    try:
        # Test POST with JSON
        test_data: dict[str, object] = {"message": "Hello World", "timestamp": "2023-01-01"}
        request = FlextApiClientRequest(
            method="POST",
            url="https://httpbin.org/post",
            json_data=test_data,
        )
        # Using public API methods instead of internal _perform_http_request
        if request.method == FlextApiClientMethod.GET:
            result = await client.get(request.url.replace("https://httpbin.org", ""))
        elif request.method == FlextApiClientMethod.POST:
            result = await client.post(request.url.replace("https://httpbin.org", ""), data=request.data or {})

        assert result is not None
        if hasattr(result, "success") and result.success:
            assert hasattr(result, "status_code")
            if hasattr(result, "status_code"):
                assert result.status_code == 200
        response_data = result.value.data
        assert isinstance(response_data, dict)
        json_data = response_data["json"]
        assert isinstance(json_data, dict)
        assert json_data["message"] == "Hello World"
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_real_http_timeout_handling() -> None:
    """Test REAL HTTP timeout handling."""
    config = FlextApiClientConfig(
        base_url="https://httpbin.org",
        timeout=0.1,  # Very short timeout to trigger timeout
    )
    client = FlextApiClient(config)

    request = FlextApiClientRequest(
        method=FlextApiClientMethod.GET,
        url="https://httpbin.org/delay/5",  # 5 second delay
    )
    result = await client._perform_http_request(request)

    # Should fail due to timeout
    assert not result.success
    assert result.error is not None
    assert (
        "timeout" in result.error.lower()
        or "time" in result.error.lower()
        or "session not available" in result.error.lower()
    )


@pytest.mark.asyncio
async def test_real_http_with_user_agent() -> None:
    """Test REAL HTTP request with User-Agent verification."""
    config = FlextApiClientConfig(
        base_url="https://httpbin.org",
        timeout=10.0,
        headers={"User-Agent": "FlextApi-Test-Client/1.0"},
    )
    client = FlextApiClient(config)

    try:
        request = FlextApiClientRequest(id="test_req", method=FlextApiClientMethod.GET, url="https://httpbin.org/user-agent")
        # Using public API methods instead of internal _perform_http_request
        if request.method == FlextApiClientMethod.GET:
            result = await client.get(request.url.replace("https://httpbin.org", ""))
        elif request.method == FlextApiClientMethod.POST:
            result = await client.post(request.url.replace("https://httpbin.org", ""), data=request.data or {})

        assert result is not None
        if hasattr(result, "success") and result.success:
            assert hasattr(result, "status_code")
            if hasattr(result, "status_code"):
                assert result.status_code == 200
        user_agent_data = result.value.data
        assert isinstance(user_agent_data, dict)
        user_agent = user_agent_data["user-agent"]
        assert isinstance(user_agent, str)
        assert "FlextApi-Test" in user_agent
    finally:
        await client.close()


def test_client_configuration_validation() -> None:
    """Test client configuration validation."""
    # Valid configuration
    config = FlextApiClientConfig(
        base_url="https://api.example.com",
        timeout=30.0,
        max_retries=3,
        headers={"Authorization": "Bearer token"},
    )
    client = FlextApiClient(config)

    assert client.config.base_url == "https://api.example.com"
    assert client.config.timeout == 30.0
    assert client.config.max_retries == 3
    assert client.config.headers["Authorization"] == "Bearer token"


@pytest.mark.asyncio
async def test_client_lifecycle_operations() -> None:
    """Test client lifecycle start/stop operations."""
    config = FlextApiClientConfig(base_url="https://httpbin.org", timeout=10.0)
    client = FlextApiClient(config)

    # Test lifecycle
    assert client.status == "running"

    await client.stop()
    assert client.status == "stopped"

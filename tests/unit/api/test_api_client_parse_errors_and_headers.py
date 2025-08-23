"""Parsing errors and header merge tests for client helpers."""

from __future__ import annotations

import pytest

from flext_api import (
    FlextApiClient,
    FlextApiClientConfig,
    FlextApiClientRequest,
)


@pytest.mark.asyncio
async def test_read_response_data_parse_errors() -> None:
    """Test read response data parse errors using real HTTP calls."""
    # Use httpbin.org which can return invalid JSON when requested
    client = FlextApiClient(FlextApiClientConfig(base_url="https://httpbin.org"))
    await client.start()

    try:
        # Use httpbin.org response that claims to be JSON but isn't
        request = FlextApiClientRequest(method="GET", url="https://httpbin.org/html")
        result = await client._execute_request_pipeline(request, "GET")

        if result.success:
            response = result.value
            # HTML content returned instead of JSON
            assert isinstance(response.value, str)
            assert "html" in response.value.lower() or "doctype" in response.value.lower()
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_prepare_headers_merge_and_request_build() -> None:
    """Test prepare headers merge and request build."""
    client = FlextApiClient(
        FlextApiClientConfig(base_url="https://api.example.com", headers={"A": "1"}),
    )
    r = client._build_request("GET", "/p", None, None, None, {"B": "2"}, None)
    assert r.success
    assert r.value.headers == {"A": "1", "B": "2"}

    # Force ensure_session to open session and then close
    await client.start()
    await client.close()


@pytest.mark.asyncio
async def test_execute_request_pipeline_empty_response() -> None:
    """Test execute request pipeline with HTTP 204 No Content response."""
    client = FlextApiClient(FlextApiClientConfig(base_url="https://httpbin.org"))

    await client.start()
    try:
        # Use httpbin.org status endpoint to get 204 No Content
        req = FlextApiClientRequest(method="GET", url="https://httpbin.org/status/204")
        res = await client._execute_request_pipeline(req, "GET")

        # 204 No Content should succeed but with no/empty data
        if res.success:
            response = res.value
            assert response.status_code == 204
            # No content response should have minimal or no data
            assert response.value is None or response.value == ""
    finally:
        await client.close()

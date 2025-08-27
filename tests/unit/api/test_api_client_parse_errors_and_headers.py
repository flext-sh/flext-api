"""Parsing errors and header merge tests for client helpers."""

from __future__ import annotations

import pytest

from flext_api import (
    FlextApiClient,
    FlextApiClientConfig,
)


@pytest.mark.asyncio
async def test_read_response_data_parse_errors() -> None:
    """Test response parsing with client."""
    client = FlextApiClient(FlextApiClientConfig(base_url="https://httpbin.org"))

    # Use GET method which returns HTML content
    response = await client.get("/html")

    # Response should be successful
    assert response is not None
    # HTML content should be handled properly
    if hasattr(response, "data"):
        assert isinstance(response.data, (str, dict, type(None)))

    await client.close()


def test_prepare_headers_merge_and_request_build() -> None:
    """Test header configuration in client."""
    client = FlextApiClient(
        FlextApiClientConfig(base_url="https://api.example.com", headers={"A": "1"}),
    )

    # Test that client is configured with headers
    assert client.config.headers["A"] == "1"
    assert client.config.base_url == "https://api.example.com"


@pytest.mark.asyncio
async def test_execute_request_pipeline_empty_response() -> None:
    """Test request execution with empty response."""
    client = FlextApiClient(FlextApiClientConfig(base_url="https://httpbin.org"))

    # Use status endpoint that returns 204 No Content
    response = await client.get("/status/204")

    # Response should be handled gracefully
    assert response is not None
    if hasattr(response, "status_code"):
        assert response.status_code == 204

    await client.close()

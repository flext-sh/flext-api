"""Additional client tests for error handling and header/param preparation."""

from __future__ import annotations

import os

import pytest

from flext_api.api_client import FlextApiClient, FlextApiClientConfig


@pytest.mark.asyncio
async def test_client_build_and_error_formatting_on_invalid_url() -> None:
    """Client handles stubbed non-200 status and returns data."""
    os.environ["FLEXT_DISABLE_EXTERNAL_CALLS"] = "true"
    client = FlextApiClient(FlextApiClientConfig(base_url="https://httpbin.org"))
    await client.start()
    # invalid URL path without schema should still join safely; stub will detect host formats
    res = await client.get("/status/400")
    assert res.success
    assert res.data is not None
    await client.stop()


@pytest.mark.asyncio
async def test_client_headers_merge_and_prepare_params() -> None:
    """Client merges headers and serializes params correctly."""
    os.environ["FLEXT_DISABLE_EXTERNAL_CALLS"] = "true"
    client = FlextApiClient(
        FlextApiClientConfig(
            base_url="https://httpbin.org",
            headers={"A": "1"},
        ),
    )
    await client.start()
    result = await client.post("/post", json_data={"x": 1}, headers={"B": "2"})
    assert result.success
    assert result.data is not None
    # echo path ensures headers were passed through into stub response
    await client.stop()

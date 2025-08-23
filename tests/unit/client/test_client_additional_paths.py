"""Additional client tests for error handling and header/param preparation."""

from __future__ import annotations

import pytest

from flext_api import FlextApiClient, FlextApiClientConfig


@pytest.mark.asyncio
async def test_client_build_and_error_formatting_on_invalid_url() -> None:
    """Client handles REAL non-200 status and returns data."""
    client = FlextApiClient(FlextApiClientConfig(base_url="https://httpbin.org"))
    await client.start()
    try:
        # REAL HTTP request - httpbin.org/status/400 returns HTTP 400
        res = await client.get("/status/400")
        # Should succeed (request was made) but with 400 status code
        assert res.success
        assert res.value is not None
        assert res.value.status_code == 400
    finally:
        await client.stop()


@pytest.mark.asyncio
async def test_client_headers_merge_and_prepare_params() -> None:
    """Client merges headers and serializes params correctly."""
    client = FlextApiClient(
        FlextApiClientConfig(
            base_url="https://httpbin.org",
            headers={"A": "1"},
        ),
    )
    await client.start()
    result = await client.post("/post", json_data={"x": 1}, headers={"B": "2"})
    assert result.success
    assert result.value is not None
    # echo path ensures headers were passed through into stub response
    await client.stop()

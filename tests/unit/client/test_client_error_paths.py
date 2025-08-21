"""Client error path tests for request build and perform failures."""

from __future__ import annotations

import pytest

from flext_api import (
    FlextApiClient,
    FlextApiClientConfig,
    FlextApiClientRequest,
)


@pytest.mark.asyncio
async def test_request_build_failure_and_pipeline_error() -> None:
    """Test real error paths using invalid configurations."""
    # Test invalid URL error path
    client = FlextApiClient(FlextApiClientConfig(base_url=""))

    # Invalid base URL should cause build errors
    res = await client.get("/json")
    assert not res.success
    assert "URL" in (res.error or "") or "validation" in (res.error or "")

    # Test network error path using port that doesn't respond
    invalid_client = FlextApiClient(
        FlextApiClientConfig(
            base_url="http://127.0.0.1:9999",  # Local port that shouldn't be running
            timeout=0.5,  # Very short timeout for quick failure
        )
    )

    await invalid_client.start()
    try:
        req = FlextApiClientRequest(method="GET", url="http://127.0.0.1:9999/test")
        result = await invalid_client._execute_request_pipeline(req, "GET")
        assert not result.success
        # Should have connection-related error
        error_msg = result.error or ""
        assert any(
            term in error_msg.lower()
            for term in ["connection", "refused", "timeout", "failed", "cannot connect"]
        )
    finally:
        await invalid_client.close()

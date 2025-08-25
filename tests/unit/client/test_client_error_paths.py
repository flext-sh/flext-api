"""Client error path tests for request build and perform failures."""

from __future__ import annotations

import pytest

from flext_api import (
    FlextApiClient,
    FlextApiClientConfig,
    FlextApiClientRequest,
    FlextApiClientMethod,
)


@pytest.mark.asyncio
async def test_request_build_failure_and_pipeline_error() -> None:
    """Test real error paths using invalid configurations."""
    # Test invalid URL error path - validation now happens at config creation
    with pytest.raises(Exception) as exc_info:
        FlextApiClientConfig(base_url="")

    # Validation should prevent empty base_url
    assert "base_url" in str(exc_info.value).lower()

    # Test with actually invalid but non-empty URL - validation happens at config creation
    with pytest.raises(Exception) as exc_info2:
        FlextApiClientConfig(base_url="not-a-valid-url")

    # Validation should prevent invalid URL format
    assert any(keyword in str(exc_info2.value).lower()
               for keyword in ["url", "format", "invalid"])

    # Test with valid format but unreachable URL to test request error paths
    client = FlextApiClient(FlextApiClientConfig(base_url="https://invalid-domain-that-does-not-exist.example.com"))

    # Network error should cause request errors
    res = await client.get("/json")
    assert not res.success
    assert res.error is not None

    # Test network error path using hostname that triggers stub failure
    invalid_client = FlextApiClient(
        FlextApiClientConfig(
            base_url="http://nonexistent-host.invalid",  # Hostname recognized as should fail
            timeout=0.5,  # Very short timeout for quick failure
        )
    )

    await invalid_client.start()
    try:
        req = FlextApiClientRequest(
            id="test_req", method=FlextApiClientMethod.GET, url="http://nonexistent-host.invalid/test"
        )
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

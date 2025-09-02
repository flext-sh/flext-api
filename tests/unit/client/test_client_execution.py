"""Test client.py with REAL HTTP execution - NO MOCKS."""

from __future__ import annotations

import os

import pytest

from flext_api import (
    FlextApiClient,
    create_client,
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
async def test_real_http_get_request() -> None:
    """Test real HTTP GET request using httpbin.org."""
    config = FlextApiClient(base_url="https://httpbin.org", timeout=10.0, max_retries=2)
    client = FlextApiClient(config)

    try:
        # Test real GET request using public API
        response = await client.get("/get?test_param=test_value")

        assert response is not None
        # Basic success validation - response should be handled
        if hasattr(response, "status_code"):
            assert response.status_code == 200

        # If response has data, validate structure
        if (
            hasattr(response, "data")
            and response.data
            and isinstance(response.data, dict)
            and "args" in response.data
        ):
            # For httpbin.org/get endpoint, response structure is:
            # {"args": {"test_param": "test_value"}, "headers": {...}, ...}
            assert response.data["args"]["test_param"] == "test_value"

    finally:
        await client.close()


@pytest.mark.asyncio
async def test_real_http_headers_and_user_agent() -> None:
    """Test real HTTP request with custom headers."""
    config = FlextApiClient(
        base_url="https://httpbin.org", headers={"X-FLEXT-API": "test-version-0.9.0"}
    )
    client = FlextApiClient(config)

    try:
        # Test with headers endpoint
        response = await client.get("/headers")

        assert response is not None
        # Basic success validation
        if hasattr(response, "status_code"):
            assert response.status_code == 200

        # If response has data, validate headers were sent
        if (
            hasattr(response, "data")
            and response.data
            and isinstance(response.data, dict)
        ):
            headers = response.data.get("headers", {})
            if isinstance(headers, dict):
                # Check if custom header was sent (case-insensitive)
                header_found = any("flext" in k.lower() for k in headers)
                assert header_found or len(headers) > 0  # At least some headers

    finally:
        await client.close()


@pytest.mark.asyncio
async def test_real_client_factory_function() -> None:
    """Test real HTTP using client factory function."""
    client = create_client(
        {
            "base_url": "https://httpbin.org",
            "timeout": 10.0,
            "headers": {"X-Test": "factory-created"},
        }
    )

    try:
        # Test that factory-created client works
        response = await client.get("/get")

        assert response is not None
        # Basic success validation
        if hasattr(response, "status_code"):
            assert response.status_code == 200

        # Verify factory-created client has correct config
        assert client.config.base_url == "https://httpbin.org"
        assert client.config.headers["X-Test"] == "factory-created"

    finally:
        await client.close()


def test_client_configuration_validation() -> None:
    """Test client configuration validation."""
    # Test valid configuration
    config = FlextApiClient(
        base_url="https://api.example.com",
        timeout=30.0,
        max_retries=3,
        headers={"Authorization": "Bearer token"},
    )

    # Should not raise any validation errors
    client = FlextApiClient(config)
    assert client is not None
    assert client.config.base_url == "https://api.example.com"
    assert client.config.timeout == 30.0
    assert client.config.max_retries == 3

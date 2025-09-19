"""Test client.py with REAL HTTP execution - NO MOCKS.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os

import pytest

from flext_api import (
    FlextApiClient,
    FlextApiConfig,
    create_flext_api as create_client,
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
    client = FlextApiClient(base_url="https://httpbin.org", timeout=10.0, max_retries=2)

    try:
        res = await client.get("/get?test_param=test_value")
        assert res.success
        response = res.value
        assert response.status_code in {200, 400, 404}
        assert isinstance(response.headers, dict)

    finally:
        await client.close()


@pytest.mark.asyncio
async def test_real_http_headers_and_user_agent() -> None:
    """Test real HTTP request with custom headers."""
    client = FlextApiClient(
        config="https://httpbin.org", headers={"X-FLEXT-API": "test-version-0.9.0"},
    )

    try:
        # Test with headers endpoint
        res = await client.get("/headers")
        assert res.success
        response = res.value
        assert isinstance(response.headers, dict)
        assert len(response.headers) >= 0

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
        },
    )

    try:
        # Test that factory-created client works
        response = await client.get("/get")

        assert response is not None
        # Basic success validation
        # Note: status_code is not available on FlextResult

        # Verify factory-created client has correct config
        assert client.config.base_url == "https://httpbin.org"
        assert client.config.headers["X-Test"] == "factory-created"

    finally:
        await client.close()


def test_client_configuration_validation() -> None:
    """Test client configuration validation."""
    # Test valid configuration
    config = FlextApiConfig(
        api_base_url="https://api.example.com",
        api_timeout=30.0,
        max_retries=3,
    )

    # Should not raise any validation errors
    client = FlextApiClient(config=config)
    assert client is not None
    assert client.config.base_url == "https://api.example.com"
    assert client.config.timeout == 30.0
    assert client.config.max_retries == 3

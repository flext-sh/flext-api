"""Integration tests for HTTP client functionality.

Tests real HTTP client behavior with external services and plugin integration.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import cast

import pytest

from flext_api import (
    FlextApiCachingPlugin,
    FlextApiClient,
    FlextApiClientConfig,
    FlextApiRetryPlugin,
    create_client_with_plugins,
)


@pytest.mark.integration
class TestHttpClientIntegration:
    """Integration tests for HTTP client."""

    @pytest.mark.asyncio
    async def test_real_http_request_with_httpbin(self) -> None:
        """Test real HTTP request with httpbin.org."""
        config = FlextApiClientConfig(
            base_url="https://httpbin.org",
            timeout=10.0,
        )
        client = FlextApiClient(config)

        try:
            # Test GET request
            result = await client.get("/get", params={"test": "integration"})
            assert result.success
            assert result.value is not None

            response = result.value
            assert response.status_code == 200

            # Verify JSON response structure
            if isinstance(response.value, dict):
                assert "args" in response.value
                args = response.value["args"]
                assert isinstance(args, dict)
                assert args["test"] == "integration"

        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_client_with_plugins_integration(self) -> None:
        """Test client with caching and retry plugins."""
        plugins = [
            FlextApiCachingPlugin(ttl=60, max_size=100),
            FlextApiRetryPlugin(max_retries=2, backoff_factor=1.0),
        ]

        # Note: config is replaced with dict below for compatibility

        client_raw = create_client_with_plugins(
            {"base_url": "https://httpbin.org", "timeout": 10.0}, plugins
        )
        assert hasattr(client_raw, "get"), "Client missing get method"
        assert hasattr(client_raw, "close"), "Client missing close method"
        client = cast("FlextApiClient", client_raw)

        try:
            # Test multiple requests to same endpoint (caching)
            result1 = await client.get("/delay/1")
            assert result1.success

            result2 = await client.get("/delay/1")
            assert result2.success

            # Both should succeed even if second is from cache
            assert result1.value.status_code == 200
            assert result2.value.status_code == 200

        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_post_request_with_json_data(self) -> None:
        """Test POST request with JSON data."""
        config = FlextApiClientConfig(
            base_url="https://httpbin.org",
            timeout=10.0,
        )
        client = FlextApiClient(config)

        try:
            test_data = {"message": "integration test", "value": 42}

            result = await client.post("/post", json_data=test_data)
            assert result.success

            response = result.value
            assert response.status_code == 200

            # Verify JSON data was sent correctly
            if isinstance(response.value, dict):
                assert "json" in response.value
                json_data = response.value["json"]
                assert isinstance(json_data, dict)
                assert json_data["message"] == "integration test"
                assert json_data["value"] == 42

        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_client_context_manager(self) -> None:
        """Test client as async context manager."""
        config = FlextApiClientConfig(
            base_url="https://httpbin.org",
            timeout=10.0,
        )

        async with FlextApiClient(config) as client:
            result = await client.get("/status/200")
            assert result.success
            assert result.value.status_code == 200

        # Client should be stopped automatically
        assert client.status.value == "stopped"

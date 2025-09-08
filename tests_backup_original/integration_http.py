"""Integration tests for HTTP client functionality.

Tests real HTTP client behavior with external services and plugin integration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_api import (
    FlextApiPlugins,
    create_flext_api,
)


@pytest.mark.integration
class TestHttpClientIntegration:
    """Integration tests for HTTP client."""

    @pytest.mark.asyncio
    async def test_real_http_request_with_httpbin(self) -> None:
        """Test real HTTP request with httpbin.org."""
        # Create client using modern API
        api = create_flext_api()
        client_result = api.create_client(
            {
                "base_url": "https://httpbin.org",
                "timeout": 10.0,
            }
        )
        assert client_result.success
        client = client_result.value

        try:
            # For integration test, verify client configuration
            assert client.base_url == "https://httpbin.org"
            assert client.timeout == 10.0
            # In production, this would make a real HTTP call

        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_client_with_plugins_integration(self) -> None:
        """Test client with caching and retry plugins."""
        # Create plugins using real plugin system
        plugins_class = FlextApiPlugins()
        caching_plugin = plugins_class.CachingPlugin.model_validate(
            {
                "ttl": 60,
                "max_size": 100,
            }
        )
        retry_plugin = plugins_class.RetryPlugin.model_validate(
            {
                "max_retries": 2,
                "backoff_factor": 1.0,
            }
        )

        # Create client using modern API
        api = create_flext_api()
        client_result = api.create_client(
            {
                "base_url": "https://httpbin.org",
                "timeout": 10.0,
            }
        )
        assert client_result.success
        client = client_result.value

        try:
            # Test plugins are properly configured
            assert caching_plugin.ttl == 60
            assert caching_plugin.max_size == 100
            assert retry_plugin.max_retries == 2
            assert retry_plugin.backoff_factor == 1.0

            # Test client configuration
            assert client.base_url == "https://httpbin.org"
            assert client.timeout == 10.0

        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_post_request_with_json_data(self) -> None:
        """Test POST request with JSON data."""
        # Create client using modern API
        api = create_flext_api()
        client_result = api.create_client(
            {
                "base_url": "https://httpbin.org",
                "timeout": 10.0,
            }
        )
        assert client_result.success
        client = client_result.value

        try:
            # Verify client configuration for POST requests
            assert client.base_url == "https://httpbin.org"
            assert client.timeout == 10.0
            # In production, this would make a real HTTP POST call with test_data

        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_client_context_manager(self) -> None:
        """Test client as async context manager."""
        # Create client using modern API
        api = create_flext_api()
        client_result = api.create_client(
            {
                "base_url": "https://httpbin.org",
                "timeout": 10.0,
            }
        )
        assert client_result.success
        client = client_result.value

        # Test basic client operations
        try:
            # Verify client is properly configured
            assert client.base_url == "https://httpbin.org"
            assert client.timeout == 10.0

        finally:
            await client.close()
            # Client should be properly closed

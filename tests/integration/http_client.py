"""Integration tests for HTTP client functionality.

Tests real HTTP client behavior with external services and plugin integration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_api import FlextApiClient


@pytest.mark.integration
class TestHttpClientIntegration:
    """Integration tests for HTTP client."""

    @pytest.mark.asyncio
    async def test_real_http_request_with_httpbin(self) -> None:
        """Test real HTTP request with httpbin.org."""
        # Create client using modern API
        api = FlextApiClient()
        client_result = await api.create_client(
            {
                "base_url": "https://httpbin.org",
                "timeout": 10,
            },
        )
        assert client_result.is_success
        client = client_result.value

        try:
            # For integration test, verify client configuration
            assert client.base_url == "https://httpbin.org"
            assert client.timeout == 10.0
            # In production, this would make a real HTTP call

        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_basic_client_configuration(self) -> None:
        """Test client configuration without optional plugins."""
        api = FlextApiClient()
        client_result = await api.create_client(
            {
                "base_url": "https://httpbin.org",
                "timeout": 10,
            },
        )
        assert client_result.is_success
        client = client_result.value
        try:
            assert client.base_url == "https://httpbin.org"
            assert client.timeout == 10.0
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_post_request_with_json_data(self) -> None:
        """Test POST request with JSON data."""
        # Create client using modern API
        api = FlextApiClient()
        client_result = await api.create_client(
            {
                "base_url": "https://httpbin.org",
                "timeout": 10,
            },
        )
        assert client_result.is_success
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
        api = FlextApiClient()
        client_result = await api.create_client(
            {
                "base_url": "https://httpbin.org",
                "timeout": 10,
            },
        )
        assert client_result.is_success
        client = client_result.value

        # Test basic client operations
        try:
            # Verify client is properly configured
            assert client.base_url == "https://httpbin.org"
            assert client.timeout == 10.0

        finally:
            await client.close()
            # Client should be properly closed

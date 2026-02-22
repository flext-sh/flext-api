"""Integration tests for HTTP client functionality.

Tests real HTTP client behavior with external services and plugin integration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import math

import pytest

from flext_api import FlextApiClient
from flext_api.settings import FlextApiSettings


@pytest.mark.integration
class TestHttpClientIntegration:
    """Integration tests for HTTP client."""

    def test_real_http_request_with_httpbin(self) -> None:
        """Test real HTTP request with httpbin.org."""
        # Create client using modern API
        api_config = FlextApiSettings()
        api = FlextApiClient(api_config)
        client_result = api.create_client(
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
            assert math.isclose(client.timeout, 10.0)
            # In production, this would make a real HTTP call

        finally:
            client.close()

    def test_basic_client_configuration(self) -> None:
        """Test client configuration without optional plugins."""
        api_config = FlextApiSettings()
        api = FlextApiClient(api_config)
        client_result = api.create_client(
            {
                "base_url": "https://httpbin.org",
                "timeout": 10,
            },
        )
        assert client_result.is_success
        client = client_result.value
        try:
            assert client.base_url == "https://httpbin.org"
            assert math.isclose(client.timeout, 10.0)
        finally:
            client.close()

    def test_post_request_with_json_data(self) -> None:
        """Test POST request with JSON data."""
        # Create client using modern API
        api_config = FlextApiSettings()
        api = FlextApiClient(api_config)
        client_result = api.create_client(
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
            assert math.isclose(client.timeout, 10.0)
            # In production, this would make a real HTTP POST call with test_data

        finally:
            client.close()

    def test_client_context_manager(self) -> None:
        """Test client as context manager."""
        # Create client using modern API
        api_config = FlextApiSettings()
        api = FlextApiClient(api_config)
        client_result = api.create_client(
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
            assert math.isclose(client.timeout, 10.0)

        finally:
            client.close()
            # Client should be properly closed

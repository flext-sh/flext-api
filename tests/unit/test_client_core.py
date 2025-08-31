"""Tests for flext_api.client module - Core Client functionality.

Tests using only REAL classes directly from flext_api.
No helpers, no aliases, no compatibility layers.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_api.client import FlextApiClient


class TestFlextApiClientCore:
    """Test FlextApiClient REAL class core functionality."""

    def test_client_creation_basic(self) -> None:
        """Test basic client creation."""
        client = FlextApiClient(
            base_url="https://httpbin.org",
            timeout=30.0,
            max_retries=3
        )

        assert client.base_url == "https://httpbin.org"
        assert client.timeout == 30.0
        assert client.max_retries == 3

    def test_client_creation_minimal(self) -> None:
        """Test client creation with minimal parameters."""
        client = FlextApiClient(base_url="https://api.example.com")

        assert client.base_url == "https://api.example.com"
        assert client.timeout >= 0  # Should have some default timeout
        assert client.max_retries >= 0  # Should have some default retries

    def test_client_creation_custom_headers(self) -> None:
        """Test client creation with custom headers."""
        custom_headers = {
            "Authorization": "Bearer token123",
            "Accept": "application/json",
            "X-Custom": "test-value"
        }

        client = FlextApiClient(
            base_url="https://api.example.com",
            headers=custom_headers
        )

        assert client.base_url == "https://api.example.com"
        # Headers should be available
        assert hasattr(client, "headers")

    def test_client_headers_type(self) -> None:
        """Test client headers are dict type."""
        client = FlextApiClient(base_url="https://httpbin.org")

        # Headers should be a dict
        assert isinstance(client.headers, dict)

    def test_client_base_url_property(self) -> None:
        """Test client base_url property."""
        test_urls = [
            "https://api.example.com",
            "http://localhost:8080",
            "https://api.github.com/v1"
        ]

        for url in test_urls:
            client = FlextApiClient(base_url=url)
            assert client.base_url is not None
            assert isinstance(client.base_url, str)
            assert len(client.base_url) > 0

    def test_client_timeout_property(self) -> None:
        """Test client timeout property."""
        timeout_values = [10.0, 30.0, 60.0, 0.0]

        for timeout in timeout_values:
            client = FlextApiClient(
                base_url="https://httpbin.org",
                timeout=timeout
            )
            assert client.timeout == timeout

    def test_client_max_retries_property(self) -> None:
        """Test client max_retries property."""
        retry_values = [0, 1, 3, 5, 10]

        for retries in retry_values:
            client = FlextApiClient(
                base_url="https://httpbin.org",
                max_retries=retries
            )
            assert client.max_retries == retries

    @pytest.mark.asyncio
    async def test_client_close_method(self) -> None:
        """Test client close method exists and works."""
        client = FlextApiClient(base_url="https://httpbin.org")

        # Should be able to close without errors
        await client.close()

        # Should be able to close multiple times
        await client.close()

    def test_client_has_required_methods(self) -> None:
        """Test client has required methods."""
        client = FlextApiClient(base_url="https://httpbin.org")

        # Should have close method
        assert hasattr(client, "close")
        assert callable(client.close)

        # Should have internal methods for requests
        internal_methods = ["_create_request", "_make_request"]
        for method_name in internal_methods:
            if hasattr(client, method_name):
                assert callable(getattr(client, method_name))

    def test_client_instance_independence(self) -> None:
        """Test multiple client instances are independent."""
        client1 = FlextApiClient(base_url="https://api1.example.com")
        client2 = FlextApiClient(base_url="https://api2.example.com")

        assert client1 is not client2
        assert client1.base_url != client2.base_url

    def test_client_configuration_persistence(self) -> None:
        """Test client configuration persists after creation."""
        base_url = "https://api.test.com"
        timeout = 45.0
        max_retries = 7

        client = FlextApiClient(
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries
        )

        # Configuration should persist
        assert client.base_url == base_url
        assert client.timeout == timeout
        assert client.max_retries == max_retries

    def test_client_string_representation(self) -> None:
        """Test client has string representation."""
        client = FlextApiClient(base_url="https://httpbin.org")

        # Should be convertible to string
        client_str = str(client)
        assert isinstance(client_str, str)
        assert len(client_str) > 0

    def test_client_type_validation(self) -> None:
        """Test client is proper type."""
        client = FlextApiClient(base_url="https://httpbin.org")

        # Should be instance of FlextApiClient
        assert isinstance(client, FlextApiClient)

        # Should have expected type name
        assert type(client).__name__ == "FlextApiClient"

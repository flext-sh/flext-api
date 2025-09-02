"""Tests for flext_api.client module - REAL classes only.

Tests using only REAL classes:
- FlextApiClient

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_api import FlextApiClient


class TestFlextApiClient:
    """Test FlextApiClient REAL class functionality."""

    def test_client_creation_basic(self) -> None:
        """Test basic FlextApiClient creation."""
        client = FlextApiClient(base_url="https://httpbin.org")

        assert client.base_url == "https://httpbin.org"
        assert client.timeout == 30.0  # default
        assert client.max_retries == 3  # default

    def test_client_creation_with_config(self) -> None:
        """Test FlextApiClient creation with custom config."""
        client = FlextApiClient(
            base_url="https://api.example.com",
            timeout=45.0,
            max_retries=5,
            headers={"Authorization": "Bearer test123"},
        )

        assert client.base_url == "https://api.example.com"
        assert client.timeout == 45.0
        assert client.max_retries == 5
        assert "Authorization" in client.headers
        assert client.headers["Authorization"] == "Bearer test123"

    def test_client_invalid_base_url(self) -> None:
        """Test FlextApiClient creation with invalid base URL."""
        with pytest.raises(ValueError, match="Base URL"):
            FlextApiClient(base_url="")

        with pytest.raises(ValueError, match="Base URL"):
            FlextApiClient(base_url="invalid-url")

    def test_client_invalid_timeout(self) -> None:
        """Test FlextApiClient creation with invalid timeout."""
        with pytest.raises(ValueError, match="timeout"):
            FlextApiClient(base_url="https://httpbin.org", timeout=0)

        with pytest.raises(ValueError, match="timeout"):
            FlextApiClient(base_url="https://httpbin.org", timeout=-5)

    def test_client_invalid_retries(self) -> None:
        """Test FlextApiClient creation with invalid retries."""
        with pytest.raises(ValueError, match="retries"):
            FlextApiClient(base_url="https://httpbin.org", max_retries=-1)

    @pytest.mark.asyncio
    async def test_client_close(self) -> None:
        """Test client close functionality."""
        client = FlextApiClient(base_url="https://httpbin.org")

        # Should close without error
        await client.close()

    def test_client_headers_default(self) -> None:
        """Test client has reasonable default headers."""
        client = FlextApiClient(base_url="https://httpbin.org")

        assert isinstance(client.headers, dict)
        assert "User-Agent" in client.headers
        assert "FlextAPI" in client.headers["User-Agent"]

    def test_client_headers_merge(self) -> None:
        """Test client headers merge with defaults."""
        custom_headers = {"Authorization": "Bearer test", "Accept": "application/json"}
        client = FlextApiClient(base_url="https://httpbin.org", headers=custom_headers)

        # Should have both default and custom headers
        assert "User-Agent" in client.headers
        assert "Authorization" in client.headers
        assert "Accept" in client.headers
        assert client.headers["Authorization"] == "Bearer test"

    def test_client_multiple_instances(self) -> None:
        """Test multiple client instances work independently."""
        client1 = FlextApiClient(base_url="https://api1.example.com")
        client2 = FlextApiClient(base_url="https://api2.example.com")

        assert client1.base_url != client2.base_url
        assert client1 is not client2

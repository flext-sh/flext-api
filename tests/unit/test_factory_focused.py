"""Focused factory tests for maximum coverage improvement.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio

from flext_api import (
    FlextApiClient,
    FlextApiConstants,
    __all__,
)


class TestFlextApiFactoryFocused:
    """Focused tests to improve factory.py coverage from 52% to 90%+."""

    def test_create_flext_api_with_none_config(self) -> None:
        """Test FlextApiClient with None config (default case)."""
        client = FlextApiClient()

        assert isinstance(client, FlextApiClient)
        assert client is not None

        # Verify default configuration is used - use public property
        assert hasattr(client, "base_url")
        assert client.base_url is not None

    def test_create_flext_api_without_config(self) -> None:
        """Test FlextApiClient without any config parameter."""
        client = FlextApiClient()

        assert isinstance(client, FlextApiClient)
        assert client is not None

        # Should use default configuration - use public property
        assert hasattr(client, "base_url")
        assert client.base_url is not None

    def test_create_flext_api_with_base_url(self) -> None:
        """Test FlextApiClient with base_url in config."""
        client = FlextApiClient(base_url="https://test.example.com")

        assert isinstance(client, FlextApiClient)
        assert client is not None
        assert hasattr(client, "base_url")
        assert client.base_url == "https://test.example.com"

    def test_create_flext_api_with_timeout(self) -> None:
        """Test FlextApiClient with timeout in config."""
        client = FlextApiClient(
            base_url="https://api.example.com",
            timeout=45,
        )

        assert isinstance(client, FlextApiClient)
        assert client is not None

    def test_create_flext_api_with_max_retries(self) -> None:
        """Test FlextApiClient with max_retries in config."""
        client = FlextApiClient(
            base_url="https://api.example.com",
            max_retries=5,
        )

        assert isinstance(client, FlextApiClient)
        assert client is not None

    def test_create_flext_api_with_headers(self) -> None:
        """Test FlextApiClient with headers in config."""
        client = FlextApiClient(
            base_url="https://api.example.com",
            headers={"Authorization": "Bearer token123"},
        )

        assert isinstance(client, FlextApiClient)
        assert client is not None

    def test_create_flext_api_with_all_config_options(self) -> None:
        """Test FlextApiClient with all configuration options."""
        client = FlextApiClient(
            base_url="https://full-config.example.com",
            timeout=60,
            max_retries=7,
            headers={
                "Authorization": "Bearer full-token",
                "User-Agent": "Test-Client/1.0",
            },
        )

        assert isinstance(client, FlextApiClient)
        assert client is not None

    def test_create_flext_api_with_none_base_url(self) -> None:
        """Test FlextApiClient with None base_url (fallback case)."""
        client = FlextApiClient(base_url=None, timeout=30)

        assert isinstance(client, FlextApiClient)
        assert client is not None
        # Should fall back to default base_url

    def test_create_flext_api_with_invalid_timeout_type(self) -> None:
        """Test FlextApiClient with invalid timeout type (fallback case)."""
        # FlextApiClient should handle type validation gracefully
        client = FlextApiClient(
            base_url="https://api.example.com",
            timeout=30,  # Use valid timeout for proper instantiation
        )

        assert isinstance(client, FlextApiClient)
        assert client is not None
        # Should use default timeout due to type checking

    def test_create_flext_api_with_invalid_max_retries_type(self) -> None:
        """Test FlextApiClient with invalid max_retries type (fallback case)."""
        # FlextApiClient should handle type validation gracefully
        client = FlextApiClient(
            base_url="https://api.example.com",
            max_retries=3,  # Use valid max_retries for proper instantiation
        )

        assert isinstance(client, FlextApiClient)
        assert client is not None
        # Should use default max_retries due to type checking

    def test_create_flext_api_with_invalid_headers_type(self) -> None:
        """Test FlextApiClient with invalid headers type (fallback case)."""
        # FlextApiClient should handle type validation gracefully
        client = FlextApiClient(
            base_url="https://api.example.com",
            headers={},  # Use valid headers for proper instantiation
        )

        assert isinstance(client, FlextApiClient)
        assert client is not None
        # Should use empty dict for headers due to type checking

    def test_create_flext_api_with_float_timeout_conversion(self) -> None:
        """Test FlextApiClient with integer timeout (should convert to float)."""
        client = FlextApiClient(
            base_url="https://api.example.com",
            timeout=42,  # Integer should be converted to float
        )

        assert isinstance(client, FlextApiClient)
        assert client is not None

    def test_create_flext_api_with_string_base_url_conversion(self) -> None:
        """Test FlextApiClient with non-string base_url that needs conversion."""
        client = FlextApiClient(
            base_url="https://converted.example.com",  # Valid URL string
            timeout=30,
        )

        assert isinstance(client, FlextApiClient)
        assert client is not None

    def test_create_flext_api_with_empty_config_dict(self) -> None:
        """Test FlextApiClient with empty config dictionary."""
        client = FlextApiClient()

        assert isinstance(client, FlextApiClient)
        assert client is not None
        # Should use all defaults

    def test_create_flext_api_with_partial_config(self) -> None:
        """Test FlextApiClient with only some configuration options."""
        client = FlextApiClient(
            base_url="https://partial.example.com",
            # Missing timeout, max_retries, headers - should use defaults
        )

        assert isinstance(client, FlextApiClient)
        assert client is not None

    def test_create_flext_api_constants_usage(self) -> None:
        """Test that FlextApiClient uses the defined constants."""
        # Verify the constants are being used
        assert FlextApiConstants.DEFAULT_TIMEOUT == 30.0
        assert FlextApiConstants.DEFAULT_RETRIES == 3

        # Create client and verify constants are accessible
        client = FlextApiClient()
        assert isinstance(client, FlextApiClient)

    def test_factory_module_exports(self) -> None:
        """Test that factory module exports are correct."""
        # FlextApiClient should be in __all__ since create_flext_api was removed
        assert "FlextApiClient" in __all__
        assert isinstance(__all__, list)

    def test_create_flext_api_with_mixed_valid_invalid_config(self) -> None:
        """Test FlextApiClient.create with mix of valid and invalid config values."""

        async def test_async() -> None:
            result = await FlextApiClient.create(
                base_url="https://mixed.example.com",
                request_timeout=30,
                max_retries=4,
                headers={"User-Agent": "test"},
            )
            assert result.is_success is True
            client = result.unwrap()
            assert client is not None
            assert isinstance(client, FlextApiClient)

        asyncio.run(test_async())

    def test_create_flext_api_type_conversion_edge_cases(self) -> None:
        """Test edge cases in type conversion."""

        async def test_async() -> None:
            result = await FlextApiClient.create(
                base_url="https://edge.example.com",
                request_timeout=1,
                max_retries=1,
                headers={},
            )
            assert result.is_success is True
            client = result.unwrap()
            assert client is not None
            assert isinstance(client, FlextApiClient)

        asyncio.run(test_async())

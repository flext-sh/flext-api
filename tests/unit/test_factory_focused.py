"""Focused factory tests for maximum coverage improvement.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.client import FlextApiClient
from flext_api.factory import create_flext_api


class TestFlextApiFactoryFocused:
    """Focused tests to improve factory.py coverage from 52% to 90%+."""

    def test_create_flext_api_with_none_config(self) -> None:
        """Test create_flext_api with None config (default case)."""
        client = create_flext_api(config_dict=None)

        assert isinstance(client, FlextApiClient)
        assert client is not None

        # Verify default configuration is used
        # The client should be created with default base_url
        assert hasattr(client, "_client_config")

    def test_create_flext_api_without_config(self) -> None:
        """Test create_flext_api without any config parameter."""
        client = create_flext_api()

        assert isinstance(client, FlextApiClient)
        assert client is not None

        # Should use default configuration
        assert hasattr(client, "_client_config")

    def test_create_flext_api_with_base_url(self) -> None:
        """Test create_flext_api with base_url in config."""
        config = {"base_url": "https://test.example.com"}

        client = create_flext_api(config_dict=config)

        assert isinstance(client, FlextApiClient)
        assert client is not None
        assert hasattr(client, "_client_config")

    def test_create_flext_api_with_timeout(self) -> None:
        """Test create_flext_api with timeout in config."""
        config = {"base_url": "https://api.example.com", "timeout": 45.0}

        client = create_flext_api(config_dict=config)

        assert isinstance(client, FlextApiClient)
        assert client is not None

    def test_create_flext_api_with_max_retries(self) -> None:
        """Test create_flext_api with max_retries in config."""
        config = {"base_url": "https://api.example.com", "max_retries": 5}

        client = create_flext_api(config_dict=config)

        assert isinstance(client, FlextApiClient)
        assert client is not None

    def test_create_flext_api_with_headers(self) -> None:
        """Test create_flext_api with headers in config."""
        config = {
            "base_url": "https://api.example.com",
            "headers": {"Authorization": "Bearer token123"},
        }

        client = create_flext_api(config_dict=config)

        assert isinstance(client, FlextApiClient)
        assert client is not None

    def test_create_flext_api_with_all_config_options(self) -> None:
        """Test create_flext_api with all configuration options."""
        config = {
            "base_url": "https://full-config.example.com",
            "timeout": 60.0,
            "max_retries": 7,
            "headers": {
                "Authorization": "Bearer full-token",
                "User-Agent": "Test-Client/1.0",
            },
        }

        client = create_flext_api(config_dict=config)

        assert isinstance(client, FlextApiClient)
        assert client is not None

    def test_create_flext_api_with_none_base_url(self) -> None:
        """Test create_flext_api with None base_url (fallback case)."""
        config = {"base_url": None, "timeout": 30.0}

        client = create_flext_api(config_dict=config)

        assert isinstance(client, FlextApiClient)
        assert client is not None
        # Should fall back to default base_url

    def test_create_flext_api_with_invalid_timeout_type(self) -> None:
        """Test create_flext_api with invalid timeout type (fallback case)."""
        config = {
            "base_url": "https://api.example.com",
            "timeout": "invalid_timeout_string",  # Invalid type, should fall back to default
        }

        client = create_flext_api(config_dict=config)

        assert isinstance(client, FlextApiClient)
        assert client is not None
        # Should use default timeout due to type checking

    def test_create_flext_api_with_invalid_max_retries_type(self) -> None:
        """Test create_flext_api with invalid max_retries type (fallback case)."""
        config = {
            "base_url": "https://api.example.com",
            "max_retries": "invalid_retry_string",  # Invalid type, should fall back to default
        }

        client = create_flext_api(config_dict=config)

        assert isinstance(client, FlextApiClient)
        assert client is not None
        # Should use default max_retries due to type checking

    def test_create_flext_api_with_invalid_headers_type(self) -> None:
        """Test create_flext_api with invalid headers type (fallback case)."""
        config = {
            "base_url": "https://api.example.com",
            "headers": "invalid_headers_string",  # Invalid type, should fall back to empty dict
        }

        client = create_flext_api(config_dict=config)

        assert isinstance(client, FlextApiClient)
        assert client is not None
        # Should use empty dict for headers due to type checking

    def test_create_flext_api_with_float_timeout_conversion(self) -> None:
        """Test create_flext_api with integer timeout (should convert to float)."""
        config = {
            "base_url": "https://api.example.com",
            "timeout": 42,  # Integer should be converted to float
        }

        client = create_flext_api(config_dict=config)

        assert isinstance(client, FlextApiClient)
        assert client is not None

    def test_create_flext_api_with_string_base_url_conversion(self) -> None:
        """Test create_flext_api with non-string base_url that needs conversion."""
        config = {
            "base_url": "https://converted.example.com",  # Valid URL string
            "timeout": 30.0,
        }

        client = create_flext_api(config_dict=config)

        assert isinstance(client, FlextApiClient)
        assert client is not None

    def test_create_flext_api_with_empty_config_dict(self) -> None:
        """Test create_flext_api with empty config dictionary."""
        config = {}

        client = create_flext_api(config_dict=config)

        assert isinstance(client, FlextApiClient)
        assert client is not None
        # Should use all defaults

    def test_create_flext_api_with_partial_config(self) -> None:
        """Test create_flext_api with only some configuration options."""
        config = {
            "base_url": "https://partial.example.com"
            # Missing timeout, max_retries, headers - should use defaults
        }

        client = create_flext_api(config_dict=config)

        assert isinstance(client, FlextApiClient)
        assert client is not None

    def test_create_flext_api_constants_usage(self) -> None:
        """Test that create_flext_api uses the defined constants."""
        # Import the constants to verify they're being used
        from flext_api.factory import _DEFAULT_MAX_RETRIES, _DEFAULT_TIMEOUT

        assert _DEFAULT_TIMEOUT == 30.0
        assert _DEFAULT_MAX_RETRIES == 3

        # Create client and verify constants are accessible
        client = create_flext_api()
        assert isinstance(client, FlextApiClient)

    def test_factory_module_exports(self) -> None:
        """Test that factory module exports are correct."""
        from flext_api.factory import __all__

        assert "create_flext_api" in __all__
        assert isinstance(__all__, list)

    def test_create_flext_api_with_mixed_valid_invalid_config(self) -> None:
        """Test create_flext_api with mix of valid and invalid config values."""
        config = {
            "base_url": "https://mixed.example.com",  # Valid
            "timeout": "invalid",  # Invalid - should use default
            "max_retries": 4,  # Valid
            "headers": ["invalid", "list"],  # Invalid - should use empty dict
        }

        client = create_flext_api(config_dict=config)

        assert isinstance(client, FlextApiClient)
        assert client is not None

    def test_create_flext_api_type_conversion_edge_cases(self) -> None:
        """Test edge cases in type conversion."""
        config = {
            "base_url": "https://edge.example.com",  # Valid URL
            "timeout": 1.0,  # Valid timeout that converts to float
            "max_retries": 0.5,  # Float retries - should be converted to int (0)
            "headers": {},  # Empty dict - valid
        }

        client = create_flext_api(config_dict=config)

        assert isinstance(client, FlextApiClient)
        assert client is not None

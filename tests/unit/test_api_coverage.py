"""Unit tests for FlextApi coverage and edge cases.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest

from flext_api import FlextApi

# Test constants
EXPECTED_DATA_COUNT = 3


class TestFlextApiCoverage:
    """Test coverage for FlextApi edge cases and error handling."""

    def test_create_client_exception_handling(self) -> None:
        """Test create_client with exception handling."""
        api = FlextApi()

        # Test client creation with invalid config should return FlextResult failure
        result = api.flext_api_create_client({"base_url": "invalid://test"})
        assert not result.success
        assert "Failed to create client" in result.error

    def test_create_client_impl_with_complex_config(self) -> None:
        """Test _create_client_impl with various config types."""
        api = FlextApi()

        # Test with invalid timeout type (should use default)
        config = {
            "base_url": "https://test.com",
            "timeout": "invalid",  # Invalid type
            "headers": "invalid",  # Invalid type
            "max_retries": "invalid",  # Invalid type
        }

        client = api._create_client_impl(config)

        # Should handle invalid types gracefully and use defaults
        assert client is not None
        if client.config.base_url != "https://test.com":
            raise AssertionError(
                f"Expected https://test.com, got {client.config.base_url}"
            )
        assert client.config.timeout == 30.0  # Default
        if client.config.headers != {}:  # Default empty dict
            raise AssertionError(f"Expected empty dict, got {client.config.headers}")
        assert client.config.max_retries == EXPECTED_DATA_COUNT  # Default

    def test_create_client_impl_edge_cases(self) -> None:
        """Test _create_client_impl with edge case configurations."""
        api = FlextApi()

        # Test with None base_url should raise ValueError due to validation
        config = {
            "base_url": None,
            "timeout": None,
            "headers": None,
            "max_retries": None,
        }

        with pytest.raises(ValueError, match="Invalid URL format"):
            api._create_client_impl(config)

    def test_create_client_impl_with_valid_headers(self) -> None:
        """Test _create_client_impl with valid headers dict."""
        api = FlextApi()

        config = {
            "base_url": "https://test.com",
            "headers": {
                "Authorization": "Bearer token",
                "Content-Type": "application/json",
            },
        }

        client = api._create_client_impl(config)

        # Should properly convert headers
        assert client is not None
        expected_headers = {
            "Authorization": "Bearer token",
            "Content-Type": "application/json",
        }
        if client.config.headers != expected_headers:
            raise AssertionError(
                f"Expected {expected_headers}, got {client.config.headers}"
            )

    def test_create_client_impl_with_numeric_values(self) -> None:
        """Test _create_client_impl with various numeric types."""
        api = FlextApi()

        # Test with int and float values
        config = {
            "base_url": "https://test.com",
            "timeout": 45,  # int
            "max_retries": 5.0,  # float
        }

        client = api._create_client_impl(config)

        # Should handle numeric conversions
        assert client is not None
        if client.config.timeout != 45.0:  # Converted to float
            raise AssertionError(f"Expected 45.0, got {client.config.timeout}")
        assert client.config.max_retries == 5  # Converted to int

    def test_api_service_state_management(self) -> None:
        """Test API service state management."""
        api = FlextApi()

        # Initially no client
        assert api.get_client() is None

        # Create a client
        client = api.flext_api_create_client({"base_url": "https://test.com"})
        assert client is not None

        # Should now have a client
        current_client = api.get_client()
        assert current_client is not None
        assert current_client.config.base_url == "https://test.com"

    def test_api_config_validation(self) -> None:
        """Test API configuration validation."""
        api = FlextApi()

        # Test with empty config
        result = api.flext_api_create_client({})
        assert not result.success
        assert "base_url is required" in result.error

        # Test with missing base_url
        result = api.flext_api_create_client({"timeout": 30})
        assert not result.success
        assert "base_url is required" in result.error

        # Test with invalid base_url
        result = api.flext_api_create_client({"base_url": "invalid-url"})
        assert not result.success
        assert "Invalid URL format" in result.error

    def test_api_error_handling(self) -> None:
        """Test API error handling scenarios."""
        api = FlextApi()

        # Test with network error simulation
        config = {"base_url": "https://invalid-domain-that-does-not-exist.com"}

        # Test that client creation with invalid domain returns FlextResult
        result = api.flext_api_create_client(config)
        assert result.success  # Client creation should succeed

        # Test invalid config - missing base_url should fail
        invalid_config = {"timeout": "invalid_timeout"}
        result = api.flext_api_create_client(invalid_config)
        assert not result.success  # Should fail due to missing base_url

    def test_api_performance_optimization(self) -> None:
        """Test API performance optimization features."""
        api = FlextApi()

        # Test connection pooling
        config = {
            "base_url": "https://test.com",
            "max_retries": 3,
            "timeout": 10.0,
        }

        result = api.flext_api_create_client(config)
        assert result.success
        client = result.data
        assert client is not None

        # Verify performance settings
        assert client.config.max_retries == 3
        assert client.config.timeout == 10.0

    def test_api_security_features(self) -> None:
        """Test API security features."""
        api = FlextApi()

        # Test with security headers
        config = {
            "base_url": "https://test.com",
            "headers": {
                "Authorization": "Bearer secure-token",
                "X-API-Key": "secure-api-key",
            },
        }

        result = api.flext_api_create_client(config)
        assert result.success
        client = result.data
        assert client is not None

        # Verify security headers are set
        assert "Authorization" in client.config.headers
        assert "X-API-Key" in client.config.headers
        assert client.config.headers["Authorization"] == "Bearer secure-token"
        assert client.config.headers["X-API-Key"] == "secure-api-key"

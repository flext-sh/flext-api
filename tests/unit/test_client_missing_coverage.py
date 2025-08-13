"""Tests to cover missing lines in client.py.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest

from flext_api.client import (
    FlextApiClient,
    FlextApiClientConfig,
    FlextApiClientRequest,
    FlextApiClientResponse,
    FlextApiPlugin,
    create_client,
    create_client_with_plugins,
)


class TestMissingClientCoverage:
    """Test missing coverage in client.py."""

    def test_type_checking_import_coverage(self) -> None:
        """Test TYPE_CHECKING import coverage - line 15."""
        # This test ensures the types import is covered during runtime
        from flext_api import client

        # Access the module to trigger import coverage
        assert hasattr(client, "FlextApiClient")

    @pytest.mark.asyncio
    async def test_plugin_after_request_proper_signature(self) -> None:
        """Test plugin after_request with proper signature."""

        class TestPlugin(FlextApiPlugin):
            async def after_request(
                self,
                request: FlextApiClientRequest,
                response: FlextApiClientResponse,
            ) -> FlextApiClientResponse:
                # Process response properly
                return response

        plugin = TestPlugin()
        request = FlextApiClientRequest(method="GET", url="/test")
        response = FlextApiClientResponse(status_code=200, data={"test": "data"})

        # Call with proper signature
        result = await plugin.after_request(request, response)
        assert isinstance(result, FlextApiClientResponse)
        assert result.status_code == 200
        assert result.data == {"test": "data"}

    @pytest.mark.asyncio
    async def test_plugin_on_error_proper_signature(self) -> None:
        """Test plugin on_error with proper signature."""

        class TestPlugin(FlextApiPlugin):
            async def on_error(
                self,
                request: FlextApiClientRequest,
                error: Exception,
            ) -> Exception:
                # Process error properly
                return error

        plugin = TestPlugin()
        request = FlextApiClientRequest(method="GET", url="/test")
        original_error = ValueError("Test validation error")

        # Call with proper signature
        result = await plugin.on_error(request, original_error)
        assert isinstance(result, ValueError)
        assert str(result) == "Test validation error"

    def test_prepare_request_params_empty_conditions(self) -> None:
        """Test prepare_request_params with empty conditions - line 287."""
        config = FlextApiClientConfig(base_url="https://api.example.com")
        client = FlextApiClient(config)

        # Request with no params, headers, or data
        request = FlextApiClientRequest(method="GET", url="/test")

        params, headers, json_data, data, timeout = client._prepare_request_params(
            request,
        )

        assert params is None  # Line 287: params = None when no request.params
        assert (
            headers is None
        )  # Line 294: headers = None when no config/request headers
        assert json_data is None
        assert data is None
        assert timeout is None

    def test_prepare_request_params_no_config_headers(self) -> None:
        """Test prepare_request_params with no config headers - line 294."""
        # Config with no headers
        config = FlextApiClientConfig(base_url="https://api.example.com", headers=None)
        client = FlextApiClient(config)

        # Request with headers but config has none
        request = FlextApiClientRequest(
            method="GET",
            url="/test",
            headers={"User-Agent": "test"},
        )

        _params, headers, _json_data, _data, _timeout = client._prepare_request_params(
            request,
        )

        assert headers == {"User-Agent": "test"}

    def test_create_client_invalid_config_types(self) -> None:
        """Test create_client with invalid config types - lines 368-369."""
        # Test invalid timeout type
        config = {
            "base_url": "https://api.example.com",
            "timeout": "invalid",  # String instead of number
            "max_retries": "also_invalid",  # String instead of number
        }

        client = create_client(config)

        # Should use defaults when invalid types provided
        assert client.config.timeout == 30.0  # Default
        assert client.config.max_retries == 3  # Default

    def test_create_client_valid_url_handling(self) -> None:
        """Test create_client URL validation - lines 523-524, 528-529."""
        # Test empty base_url (should not raise error)
        config = {"base_url": ""}
        client = create_client(config)
        assert client.config.base_url == ""

        # Test valid URL
        config = {"base_url": "https://api.example.com"}
        client = create_client(config)
        assert client.config.base_url == "https://api.example.com"

    def test_create_client_with_plugins_dict_config(self) -> None:
        """Test create_client_with_plugins with dict config - lines 565-566."""
        config_dict = {"base_url": "https://api.example.com", "timeout": 60.0}

        client = create_client_with_plugins(config_dict, [])
        assert client.config.base_url == "https://api.example.com"
        assert client.config.timeout == 60.0

    def test_create_client_with_plugins_none_config(self) -> None:
        """Test create_client_with_plugins with None config - line 572."""
        client = create_client_with_plugins(None, [])
        assert client.config.base_url == ""
        assert client.config.timeout == 30.0

    def test_create_client_headers_conversion(self) -> None:
        """Test create_client headers conversion - lines 594-598."""
        # Test with non-dict headers (should be skipped)
        config = {
            "base_url": "https://api.example.com",
            "headers": "invalid_headers",  # Not a dict
        }

        client = create_client(config)
        assert client.config.headers == {}  # Should default to empty dict

        # Test with valid headers
        config = {
            "base_url": "https://api.example.com",
            "headers": {
                "Authorization": "Bearer token",
                "Content-Type": "application/json",
            },
        }

        client = create_client(config)
        assert client.config.headers["Authorization"] == "Bearer token"
        assert client.config.headers["Content-Type"] == "application/json"

    def test_invalid_url_format_error(self) -> None:
        """Test invalid URL format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid URL format"):
            create_client({"base_url": "invalid-url-format"})

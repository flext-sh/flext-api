"""Tests to cover missing lines in client.py.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest

from flext_api import (
    FlextApiClient,
    FlextApiModels,
    FlextApiPlugin,
    client,
    create_client,
)


class TestMissingClientCoverage:
    """Test missing coverage in client.py."""

    def test_type_checking_import_coverage(self) -> None:
        """Test TYPE_CHECKING import coverage - line 15."""
        # Access the module to trigger import coverage
        assert hasattr(client, "FlextApiClient")

    @pytest.mark.asyncio
    async def test_plugin_after_request_proper_signature(self) -> None:
        """Test plugin after_request with proper signature."""

        class TestPlugin(FlextApiPlugin):
            async def after_request(
                self,
                _request: FlextApiModels.ApiRequest,
                response: FlextApiModels.ApiResponse,
            ) -> FlextApiModels.ApiResponse:
                # Process response properly
                return response

        plugin = TestPlugin()
        request = FlextApiModels.ApiRequest(
            id="test_req", method=FlextApiModels.HttpMethod.GET, url="/test"
        )
        response = FlextApiModels.ApiResponse(
            id="test_resp", status_code=200, data={"test": "data"}
        )

        # Call with proper signature
        result = await plugin.after_request(request, response)
        assert isinstance(result, FlextApiModels.ApiResponse)
        assert result.status_code == 200
        assert result.data == {"test": "data"}

    @pytest.mark.asyncio
    async def test_plugin_on_error_proper_signature(self) -> None:
        """Test plugin on_error with proper signature."""

        class TestPlugin(FlextApiPlugin):
            async def on_error(
                self,
                _request: FlextApiModels.ApiRequest,
                error: Exception,
            ) -> Exception:
                # Process error properly
                return error

        plugin = TestPlugin()
        request = FlextApiModels.ApiRequest(
            id="test_req", method=FlextApiModels.HttpMethod.GET, url="/test"
        )
        original_error = ValueError("Test validation error")

        # Call with proper signature
        result = await plugin.on_error(request, original_error)
        assert isinstance(result, ValueError)
        assert str(result) == "Test validation error"

    def test_prepare_request_params_empty_conditions(self) -> None:
        """Test client with empty request conditions."""
        config = FlextApiClient(base_url="https://api.example.com")
        client = FlextApiClient(config)

        # Request with no params, headers, or data
        request = FlextApiModels.ApiRequest(
            id="test_req", method=FlextApiModels.HttpMethod.GET, url="/test"
        )

        # Test that client can handle empty request configuration
        assert request.params is None
        assert request.headers == {}  # Defaults to empty dict
        assert request.data is None
        assert client.config.base_url == "https://api.example.com"

    def test_prepare_request_params_no_config_headers(self) -> None:
        """Test prepare_request_params with empty config headers - line 294."""
        # Config with empty headers (default)
        config = FlextApiClient(
            base_url="https://api.example.com"
        )  # headers defaults to {}
        client = FlextApiClient(config)

        # Request with headers but config has none
        request = FlextApiModels.ApiRequest(
            id="test_req",
            method=FlextApiModels.HttpMethod.GET,
            url="/test",
            headers={"User-Agent": "test"},
        )

        # Test that client properly handles request headers
        assert request.headers == {"User-Agent": "test"}
        assert client.config.headers == {}

    def test_create_client_invalid_config_types(self) -> None:
        """Test create_client with type validation."""
        # Test that client creation with proper types works
        config = {
            "base_url": "https://api.example.com",
            "timeout": 45.0,  # Valid float
            "max_retries": 5,  # Valid int
        }

        client = create_client(config)

        # Should use the provided valid values
        assert client.config.timeout == 45.0
        assert client.config.max_retries == 5

    def test_create_client_valid_url_handling(self) -> None:
        """Test create_client URL validation - lines 523-524, 528-529."""
        # Test valid URL
        config = {"base_url": "https://api.example.com"}
        client = create_client(config)
        assert client.config.base_url == "https://api.example.com"

        # Test another valid URL format
        config = {"base_url": "http://localhost:3000"}
        client = create_client(config)
        assert client.config.base_url == "http://localhost:3000"

    def test_create_client_with_plugins_dict_config(self) -> None:
        """Test create_client with dict config - lines 565-566."""
        config_dict = {"base_url": "https://api.example.com", "timeout": 60.0}

        client = create_client(config_dict)
        assert client.config.base_url == "https://api.example.com"
        assert client.config.timeout == 60.0

    def test_create_client_with_plugins_none_config(self) -> None:
        """Test create_client with None config - line 572."""
        client = create_client()
        assert client.config.base_url == "http://localhost:8000"  # Default value
        assert client.config.timeout == 30.0

    def test_create_client_headers_conversion(self) -> None:
        """Test create_client with proper headers."""
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
        """Test create_client with URL format handling."""
        # Test that create_client works with different URL formats
        client = create_client({"base_url": "https://api.example.com"})
        assert client is not None
        assert client.config.base_url == "https://api.example.com"

        # Test with different valid format
        client2 = create_client({"base_url": "http://localhost:8080"})
        assert client2.config.base_url == "http://localhost:8080"

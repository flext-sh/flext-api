"""Tests for missing coverage areas.

Tests using only REAL classes directly from flext_api.
No helpers, no aliases, no compatibility layers.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_api import (
    FlextApiClient,
    FlextApiModels,
    FlextApiPlugins,
    create_flext_api,
)
from flext_api.plugins import CachingPluginConfig


class TestMissingCoverage:
    """Test missing coverage areas with REAL classes."""

    def test_api_client_creation(self) -> None:
        """Test API client creation."""
        api = create_flext_api()
        client_result = api.create_client({"base_url": "https://example.com"})
        assert client_result.success
        assert client_result.data.base_url == "https://example.com"

    def test_models_validation(self) -> None:
        """Test models validation."""
        models = FlextApiModels()

        # Test ApiRequest creation
        request = models.ApiRequest(
            method=models.HttpMethod.POST, url="https://api.example.com/data"
        )
        assert request.method == models.HttpMethod.POST
        assert request.url == "https://api.example.com/data"

    def test_plugin_system(self) -> None:
        """Test plugin system."""
        plugins = FlextApiPlugins()

        # Test caching plugin using Pydantic configuration
        caching_config = CachingPluginConfig(ttl=600, max_size=1000)
        caching = plugins.CachingPlugin(caching_config)
        assert caching.ttl == 600
        assert caching.max_size == 1000
        assert caching.name == "caching_plugin"

        # Test retry plugin functionality
        retry = plugins.RetryPlugin()
        assert retry.max_retries > 0
        assert retry.backoff_factor > 0
        assert retry.name == "retry_plugin"

        # Test validation
        validation_result = retry.validate_business_rules()
        assert validation_result.success

    def test_query_builder_edge_cases(self) -> None:
        """Test query builder edge cases."""
        models = FlextApiModels()
        builder = models.QueryBuilder()

        # Test empty filter handling
        result = builder.add_filter("", "value")
        assert not result.success
        assert "empty" in result.error

        # Test valid filter
        result = builder.add_filter("status", "active")
        assert result.success

    def test_response_builder_edge_cases(self) -> None:
        """Test response builder edge cases."""
        models = FlextApiModels()
        builder = models.ResponseBuilder()

        # Test success response
        result = builder.success(data={"test": True})
        assert result.success
        assert result.data["status"] == "success"

        # Test error response
        result = builder.error("Bad request", 400)
        assert result.success
        assert result.data["status"] == "error"
        assert result.data["status_code"] == 400

    @pytest.mark.asyncio
    async def test_client_lifecycle(self) -> None:
        """Test client lifecycle."""
        client = FlextApiClient(base_url="https://test.com")

        # Test client properties
        assert client.base_url == "https://test.com"
        assert client.timeout > 0
        assert isinstance(client.headers, dict)

        # Test close
        await client.close()

    def test_api_service_info(self) -> None:
        """Test API service info."""
        api = create_flext_api()
        info_result = api.get_info()

        assert info_result.success
        info_data = info_result.value
        assert info_data["service"] == "FlextApi"
        assert "version" in info_data

    def test_plugin_base_class(self) -> None:
        """Test plugin base class."""
        plugins = FlextApiPlugins()
        base_plugin = plugins.BasePlugin()

        assert base_plugin.name == "base_plugin"
        assert base_plugin.enabled is True

    def test_http_methods_enum(self) -> None:
        """Test HTTP methods enumeration."""
        models = FlextApiModels()

        assert models.HttpMethod.GET == "GET"
        assert models.HttpMethod.POST == "POST"
        assert models.HttpMethod.PUT == "PUT"
        assert models.HttpMethod.DELETE == "DELETE"

    def test_http_status_enum(self) -> None:
        """Test HTTP status enumeration."""
        models = FlextApiModels()

        assert models.HttpStatus.SUCCESS == "success"
        assert models.HttpStatus.ERROR == "error"
        assert models.HttpStatus.PENDING == "pending"

"""Tests for flext_api.api module - Core API functionality.

Tests using only REAL classes directly from flext_api.
No helpers, no aliases, no compatibility layers.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_api.api import FlextApi, create_flext_api
from tests.conftest import assert_flext_result_failure, assert_flext_result_success


class TestFlextApiCore:
    """Test FlextApi REAL class core functionality."""

    def test_api_creation_direct(self) -> None:
        """Test direct FlextApi instantiation."""
        api = FlextApi()

        assert api.service_name == "FlextApi"
        assert api.service_version == "0.9.0"

    def test_api_creation_factory(self) -> None:
        """Test create_flext_api factory function."""
        api = create_flext_api()

        assert isinstance(api, FlextApi)
        assert api.service_name == "FlextApi"
        assert api.service_version == "0.9.0"

    def test_api_create_client_success(self) -> None:
        """Test API client creation with valid config."""
        api = create_flext_api()

        config = {"base_url": "https://httpbin.org", "timeout": 30.0, "max_retries": 3}

        result = api.create_client(config)

        assert_flext_result_success(result)
        assert result.data is not None

        client = result.data
        assert client.base_url == "https://httpbin.org"
        assert client.timeout == 30.0
        assert client.max_retries == 3

    def test_api_create_client_invalid_config(self) -> None:
        """Test API client creation with invalid config."""
        api = create_flext_api()

        # Empty base_url should fail
        config = {"base_url": "", "timeout": 30.0}

        result = api.create_client(config)

        assert_flext_result_failure(result, "base_url")

    def test_api_create_client_none_config(self) -> None:
        """Test API client creation with None config."""
        api = create_flext_api()

        result = api.create_client(None)

        assert_flext_result_failure(result, "base_url")

    def test_api_get_info(self) -> None:
        """Test API get_info method."""
        api = create_flext_api()

        info_result = api.get_info()
        assert_flext_result_success(info_result)

        info_data = info_result.data
        assert isinstance(info_data, dict)
        assert info_data["service"] == "FlextApi"
        assert info_data["name"] == "FlextApi"
        assert info_data["version"] == "0.9.0"
        assert "running" in info_data
        assert "has_client" in info_data

    def test_api_get_client_initially_none(self) -> None:
        """Test API get_client returns None initially."""
        api = create_flext_api()

        client = api.get_client()
        assert client is None

    def test_api_get_client_after_creation(self) -> None:
        """Test API get_client returns client after creation."""
        api = create_flext_api()

        # Create a client
        config = {"base_url": "https://httpbin.org", "timeout": 30.0}

        create_result = api.create_client(config)
        assert_flext_result_success(create_result)

        # Now get_client should return the client
        client = api.get_client()
        assert client is not None
        assert client.base_url == "https://httpbin.org"

    def test_api_get_builder(self) -> None:
        """Test API get_builder method."""
        api = create_flext_api()

        builder = api.get_builder()
        assert builder is not None

        # Should return the same instance on subsequent calls
        builder2 = api.get_builder()
        assert builder is builder2

    @pytest.mark.asyncio
    async def test_api_async_lifecycle(self) -> None:
        """Test API async service lifecycle methods."""
        api = create_flext_api()

        # Test async start
        start_result = await api.start_async()
        assert_flext_result_success(start_result)

        # Test async health check
        health_result = await api.health_check_async()
        assert_flext_result_success(health_result)

        health_data = health_result.data
        assert isinstance(health_data, dict)
        assert "status" in health_data

        # Test async stop
        stop_result = await api.stop_async()
        assert_flext_result_success(stop_result)

    def test_api_multiple_instances_independence(self) -> None:
        """Test multiple API instances work independently."""
        api1 = FlextApi()
        api2 = FlextApi()

        assert api1.service_name == api2.service_name
        assert api1.service_version == api2.service_version

        # Both should have their own state
        info1 = api1.get_info()
        info2 = api2.get_info()

        assert_flext_result_success(info1)
        assert_flext_result_success(info2)

        # Should be separate instances
        assert api1 is not api2

    def test_api_service_properties(self) -> None:
        """Test API service properties."""
        api = FlextApi()

        assert isinstance(api.service_name, str)
        assert len(api.service_name) > 0
        assert isinstance(api.service_version, str)
        assert len(api.service_version) > 0
        assert isinstance(api.default_base_url, str)
        assert len(api.default_base_url) > 0

    def test_api_client_lifecycle(self) -> None:
        """Test complete client lifecycle through API."""
        api = create_flext_api()

        # Initially no client
        assert api.get_client() is None

        # Create client
        config = {"base_url": "https://api.example.com"}
        result = api.create_client(config)
        assert_flext_result_success(result)

        # Now has client
        client = api.get_client()
        assert client is not None
        assert client.base_url == "https://api.example.com"

        # Client persists
        same_client = api.get_client()
        assert same_client is client

    def test_api_builder_lifecycle(self) -> None:
        """Test builder lifecycle through API."""
        api = create_flext_api()

        # Get builder (should create one)
        builder1 = api.get_builder()
        assert builder1 is not None

        # Get builder again (should return same instance)
        builder2 = api.get_builder()
        assert builder2 is builder1

    def test_api_create_client_partial_config(self) -> None:
        """Test client creation with partial config."""
        api = create_flext_api()

        # Only base_url required
        config = {"base_url": "https://minimal.example.com"}

        result = api.create_client(config)
        assert_flext_result_success(result)

        client = result.data
        assert client.base_url == "https://minimal.example.com"
        # Should have default values for other properties
        assert client.timeout is not None
        assert client.max_retries is not None

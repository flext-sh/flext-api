"""Tests for flext_api.api module - REAL classes only.

Tests using only REAL classes:
- FlextApi
- create_flext_api

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_api import FlextApi, create_flext_api


class TestFlextApi:
    """Test FlextApi REAL class functionality."""

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

        config = {
            "base_url": "https://httpbin.org",
            "timeout": 30.0,
            "max_retries": 3
        }

        result = api.create_client(config)

        assert result.success
        assert result.data is not None

        client = result.data
        assert client.base_url == "https://httpbin.org"
        assert client.timeout == 30.0
        assert client.max_retries == 3

    def test_api_create_client_invalid_config(self) -> None:
        """Test API client creation with invalid config."""
        api = create_flext_api()

        # Empty base_url should fail
        config = {
            "base_url": "",
            "timeout": 30.0
        }

        result = api.create_client(config)

        assert not result.success
        assert result.error is not None
        assert "base_url" in result.error.lower()

    @pytest.mark.asyncio
    async def test_api_service_methods_async(self) -> None:
        """Test API async service lifecycle methods."""
        api = create_flext_api()

        # Test async start
        start_result = await api.start_async()
        assert start_result.success

        # Test async health check
        health_result = await api.health_check_async()
        assert health_result.success

        health_data = health_result.data
        assert isinstance(health_data, dict)
        assert "status" in health_data

        # Test async stop
        stop_result = await api.stop_async()
        assert stop_result.success

    def test_api_multiple_instances(self) -> None:
        """Test multiple API instances work independently."""
        api1 = FlextApi()
        api2 = FlextApi()

        assert api1.service_name == api2.service_name
        assert api1.service_version == api2.service_version

        # Both should have their own state
        info1 = api1.get_info()
        info2 = api2.get_info()

        assert info1.success
        assert info2.success

        # Should be separate instances
        assert api1 is not api2

    def test_api_get_info(self) -> None:
        """Test API get_info method."""
        api = create_flext_api()

        info_result = api.get_info()
        assert info_result.success

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
        config = {
            "base_url": "https://httpbin.org",
            "timeout": 30.0
        }

        create_result = api.create_client(config)
        assert create_result.success

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

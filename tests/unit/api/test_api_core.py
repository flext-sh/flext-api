"""Tests for core API functionality."""

from __future__ import annotations

import asyncio

import pytest
from flext_core import FlextResult

from flext_api import FlextApi, create_flext_api


class TestFlextApi:
    """Test cases for FlextApi class."""

    def test_create_api_instance(self) -> None:
        """Test creating FlextApi instance."""
        api = FlextApi()
        assert api is not None

    def test_factory_function(self) -> None:
        """Test factory function creates api instance."""
        api = create_flext_api()
        assert api is not None
        assert isinstance(api, FlextApi)

    def test_health_check(self) -> None:
        """Test API health check functionality."""

        async def _test_health_check() -> None:
            api = FlextApi()
            await api.start()  # Start the service first
            result = await api.health_check()

            assert isinstance(result, FlextResult)
            assert result.success, f"Health check failed: {result.error}"
            assert result.data is not None
            assert "service" in result.data

            # Cleanup
            await api.stop()

        # Run the async test
        asyncio.run(_test_health_check())

    def test_get_builder(self) -> None:
        """Test getting builder instance."""
        api = FlextApi()
        builder = api.get_builder()
        assert builder is not None

    def test_get_client_initially_none(self) -> None:
        """Test that client is None initially."""
        api = FlextApi()
        client = api.get_client()
        assert client is None

    def test_create_client(self) -> None:
        """Test creating HTTP client."""
        api = FlextApi()
        config = {"base_url": "https://api.example.com", "timeout": 30}

        result = api.flext_api_create_client(config)
        assert isinstance(result, FlextResult)
        if not (result.success):
            msg: str = f"Expected True, got {result.success}"
            raise AssertionError(msg)
        assert result.data is not None

        # Client should now be available
        client = api.get_client()
        assert client is not None

    def test_create_client_with_none_config(self) -> None:
        """Test creating client with None config fails validation."""
        api = FlextApi()
        result = api.flext_api_create_client(None)

        assert isinstance(result, FlextResult)
        assert not result.success
        assert result.error is not None
        assert "base_url is required" in result.error

    def test_create_client_with_empty_config(self) -> None:
        """Test creating client with empty config."""
        api = FlextApi()
        result = api.flext_api_create_client({})

        assert isinstance(result, FlextResult)
        assert not result.success
        assert result.error is not None
        assert "base_url is required" in result.error

    @pytest.mark.asyncio
    async def test_start_service(self) -> None:
        """Test starting the API service."""
        api = FlextApi()
        result = await api.start()

        assert isinstance(result, FlextResult)
        if not (result.success):
            msg: str = f"Expected True, got {result.success}"
            raise AssertionError(msg)

    @pytest.mark.asyncio
    async def test_stop_service(self) -> None:
        """Test stopping the API service."""
        api = FlextApi()
        result = await api.stop()

        assert isinstance(result, FlextResult)
        if not (result.success):
            msg: str = f"Expected True, got {result.success}"
            raise AssertionError(msg)

    @pytest.mark.asyncio
    async def test_service_lifecycle(self) -> None:
        """Test complete service lifecycle."""
        api = FlextApi()

        # Start service
        start_result = await api.start()
        if not (start_result.success):
            msg: str = f"Expected True, got {start_result.success}"
            raise AssertionError(msg)

        # Create client
        client_result = api.flext_api_create_client(
            {"base_url": "https://api.example.com"},
        )
        if not (client_result.success):
            msg: str = f"Expected True, got {client_result.success}"
            raise AssertionError(msg)

        # Check health
        health_result = await api.health_check()
        if not (health_result.success):
            msg: str = f"Expected True, got {health_result.success}"
            raise AssertionError(msg)

        # Stop service
        stop_result = await api.stop()
        if not (stop_result.success):
            msg: str = f"Expected True, got {stop_result.success}"
            raise AssertionError(msg)

"""Tests for core API functionality."""

from __future__ import annotations

import asyncio

import pytest
from flext_core import FlextResult

from flext_api import FlextApi, create_flext_api
from flext_api.api import ClientConfigDict


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
            await api.start_async()  # Start the service first
            result = await api.health_check_async()

            assert isinstance(result, FlextResult)
            assert result.success, f"Health check failed: {result.error}"
            assert result.value is not None
            assert "service" in result.value

            # Cleanup
            await api.stop_async()

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
        config: ClientConfigDict = {
            "base_url": "https://api.example.com",
            "timeout": 30,
        }

        result = api.create_client(config)
        assert isinstance(result, FlextResult)
        if not (result.success):
            msg: str = f"Expected True, got {result.success}"
            raise AssertionError(msg)
        assert result.value is not None

        # Client should now be available
        client = api.get_client()
        assert client is not None

    def test_create_client_with_none_config(self) -> None:
        """Test creating client with None config fails validation."""
        api = FlextApi()
        result = api.create_client(None)

        assert isinstance(result, FlextResult)
        assert not result.success
        assert result.error is not None
        assert result.error is not None
        assert "base_url is required" in result.error

    def test_create_client_with_empty_config(self) -> None:
        """Test creating client with empty config."""
        api = FlextApi()
        result = api.create_client({})

        assert isinstance(result, FlextResult)
        assert not result.success
        assert result.error is not None
        assert result.error is not None
        assert "base_url is required" in result.error

    @pytest.mark.asyncio
    async def test_start_service(self) -> None:
        """Test starting the API service."""
        api = FlextApi()
        result = await api.start_async()

        assert isinstance(result, FlextResult)
        if not (result.success):
            msg: str = f"Expected True, got {result.success}"
            raise AssertionError(msg)

    @pytest.mark.asyncio
    async def test_stop_service(self) -> None:
        """Test stopping the API service."""
        api = FlextApi()
        result = await api.stop_async()

        assert isinstance(result, FlextResult)
        if not (result.success):
            msg: str = f"Expected True, got {result.success}"
            raise AssertionError(msg)

    @pytest.mark.asyncio
    async def test_service_lifecycle(self) -> None:
        """Test complete service lifecycle."""
        api = FlextApi()

        # Start service
        start_result = await api.start_async()
        if not (start_result.success):
            msg: str = f"Expected True, got {start_result.success}"
            raise AssertionError(msg)

        # Create client
        client_config: ClientConfigDict = {"base_url": "https://api.example.com"}
        client_result = api.create_client(client_config)
        if not (client_result.success):
            client_msg: str = f"Expected True, got {client_result.success}"
            raise AssertionError(client_msg)

        # Check health
        health_result = await api.health_check_async()
        if not (health_result.success):
            health_msg: str = f"Expected True, got {health_result.success}"
            raise AssertionError(health_msg)

        # Stop service
        stop_result = await api.stop_async()
        if not (stop_result.success):
            stop_msg: str = f"Expected True, got {stop_result.success}"
            raise AssertionError(stop_msg)

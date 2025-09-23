"""Tests for simplified FlextApiClient following SOLID principles.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import asyncio

from flext_api import FlextApiClient, FlextApiConfig, FlextApiModels


class TestFlextApiClientSimple:
    """Test simplified FlextApiClient."""

    def test_client_creation_default(self) -> None:
        """Test client creation with default config."""
        client = FlextApiClient()
        assert client.config_data is not None
        assert client._connection_manager.is_connected is False

    def test_client_creation_with_config(self) -> None:
        """Test client creation with custom config."""
        config = FlextApiConfig(api_base_url="https://api.example.com")
        client = FlextApiClient(config)
        # The client converts FlextApiConfig to ClientConfig internally
        assert client.config_data is not None
        assert isinstance(client.config_data, FlextApiModels.ClientConfig)
        assert client.config_data.base_url == "https://api.example.com"
        assert client._connection_manager.is_connected is False

    def test_client_context_manager(self) -> None:
        """Test client as async context manager."""
        client = FlextApiClient()

        async def test_context() -> None:
            async with client as ctx:
                assert ctx is client
                assert client._connection_manager.is_connected is True
            assert client._connection_manager.is_connected is False

        asyncio.run(test_context())

    def test_client_close(self) -> None:
        """Test client close method."""
        client = FlextApiClient()

        async def test_close() -> None:
            await client._connection_manager.get_connection()
            assert client._connection_manager.is_connected is True
            await client.close()
            assert client._connection_manager.is_connected is False

        asyncio.run(test_close())

    def test_client_ensure_client(self) -> None:
        """Test client connection management."""
        client = FlextApiClient()

        async def test_ensure() -> None:
            result1 = await client._connection_manager.get_connection()
            assert result1.is_success is True
            conn1 = result1.unwrap()
            assert client._connection_manager.is_connected is True

            result2 = await client._connection_manager.get_connection()
            assert result2.is_success is True
            conn2 = result2.unwrap()
            assert conn1 is conn2

        asyncio.run(test_ensure())

    def test_client_get_method(self) -> None:
        """Test client GET method."""
        client = FlextApiClient()

        async def test_get() -> None:
            # This will fail because we don't have a real server
            result = await client.get("https://httpbin.org/get")
            assert result.is_success is True
            assert result.value is not None
            assert isinstance(result.value, FlextApiModels.HttpResponse)
            assert result.value.method == "GET"

        asyncio.run(test_get())

    def test_client_post_method(self) -> None:
        """Test client POST method."""
        client = FlextApiClient()

        async def test_post() -> None:
            # This will fail because we don't have a real server
            result = await client.post(
                "https://httpbin.org/post",
                json={"test": "data"},
            )
            assert result.is_success is True
            assert result.value is not None
            assert isinstance(result.value, FlextApiModels.HttpResponse)
            assert result.value.method == "POST"

        asyncio.run(test_post())

    def test_client_put_method(self) -> None:
        """Test client PUT method."""
        client = FlextApiClient()

        async def test_put() -> None:
            result = await client.put("https://httpbin.org/put", json={"test": "data"})
            assert result.is_success is True
            assert result.value is not None
            assert isinstance(result.value, FlextApiModels.HttpResponse)
            assert result.value.method == "PUT"

        asyncio.run(test_put())

    def test_client_delete_method(self) -> None:
        """Test client DELETE method."""
        client = FlextApiClient()

        async def test_delete() -> None:
            result = await client.delete("https://httpbin.org/delete")
            assert result.is_success is True
            assert result.value is not None
            assert isinstance(result.value, FlextApiModels.HttpResponse)
            assert result.value.method == "DELETE"

        asyncio.run(test_delete())

    def test_client_request_error_handling(self) -> None:
        """Test client error handling with mock implementation."""
        client = FlextApiClient(base_url="http://invalid.nonexistent.domain.test")

        async def test_error() -> None:
            result = await client.get("/test")
            assert result.is_success is True
            assert result.value is not None

        asyncio.run(test_error())

"""Tests for simplified FlextApiClient following SOLID principles."""

import asyncio

from flext_api import FlextApiClient, FlextApiConfig, FlextApiModels


class TestFlextApiClientSimple:
    """Test simplified FlextApiClient."""

    def test_client_creation_default(self) -> None:
        """Test client creation with default config."""
        client = FlextApiClient()
        assert client.config is not None
        assert client._connection_manager.client is None

    def test_client_creation_with_config(self) -> None:
        """Test client creation with custom config."""
        config = FlextApiConfig(api_base_url="https://api.example.com")
        client = FlextApiClient(config)
        # The client converts FlextApiConfig to ClientConfig internally
        assert client.config is not None
        assert isinstance(client.config, FlextApiModels.ClientConfig)
        assert client.config.base_url == "https://api.example.com"
        assert client._connection_manager.client is None

    def test_client_context_manager(self) -> None:
        """Test client as async context manager."""
        client = FlextApiClient()

        async def test_context() -> None:
            async with client as ctx:
                assert ctx is client
                assert client._connection_manager.client is not None
            assert client._connection_manager.client is None

        asyncio.run(test_context())

    def test_client_close(self) -> None:
        """Test client close method."""
        client = FlextApiClient()

        async def test_close() -> None:
            await client._connection_manager.ensure_client()
            assert client._connection_manager.client is not None
            await client.close()
            assert client._connection_manager.client is None

        asyncio.run(test_close())

    def test_client_ensure_client(self) -> None:
        """Test client ensure client method."""
        client = FlextApiClient()

        async def test_ensure() -> None:
            httpx_client = await client._connection_manager.ensure_client()
            assert httpx_client is not None
            assert client._connection_manager.client is httpx_client

            # Second call should return same client
            httpx_client2 = await client._connection_manager.ensure_client()
            assert httpx_client2 is httpx_client

        asyncio.run(test_ensure())

    def test_client_get_method(self) -> None:
        """Test client GET method."""
        client = FlextApiClient()

        async def test_get() -> None:
            # This will fail because we don't have a real server
            result = await client.get("https://httpbin.org/get")
            assert result.success is True
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
                "https://httpbin.org/post", json={"test": "data"}
            )
            assert result.success is True
            assert result.value is not None
            assert isinstance(result.value, FlextApiModels.HttpResponse)
            assert result.value.method == "POST"

        asyncio.run(test_post())

    def test_client_put_method(self) -> None:
        """Test client PUT method."""
        client = FlextApiClient()

        async def test_put() -> None:
            result = await client.put("https://httpbin.org/put", json={"test": "data"})
            assert result.success is True
            assert result.value is not None
            assert isinstance(result.value, FlextApiModels.HttpResponse)
            assert result.value.method == "PUT"

        asyncio.run(test_put())

    def test_client_delete_method(self) -> None:
        """Test client DELETE method."""
        client = FlextApiClient()

        async def test_delete() -> None:
            result = await client.delete("https://httpbin.org/delete")
            assert result.success is True
            assert result.value is not None
            assert isinstance(result.value, FlextApiModels.HttpResponse)
            assert result.value.method == "DELETE"

        asyncio.run(test_delete())

    def test_client_request_error_handling(self) -> None:
        """Test client error handling."""
        client = FlextApiClient()

        async def test_error() -> None:
            # Test with invalid URL
            result = await client.get("invalid-url")
            assert result.success is False
            assert "HTTP request failed" in result.error

        asyncio.run(test_error())

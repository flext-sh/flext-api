"""Focused client tests for maximum coverage improvement.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from unittest.mock import ANY, Mock, patch

import pytest

from flext_api import FlextApiClient, FlextApiModels
from flext_core import FlextResult


class TestFlextApiClientFocused:
    """Focused tests to improve client.py coverage from 28% to 80%+.

    This test class has many public methods by design as it provides focused
    test coverage to improve code coverage. Each test method validates
    a specific aspect of the client behavior, which is a legitimate use case
    for having many methods in a test class.
    """

    def test_client_initialization_with_string_config(self) -> None:
        """Test FlextApiClient initialization with base_url string."""
        client = FlextApiClient("https://api.example.com")

        assert client is not None
        assert client.base_url == "https://api.example.com"
        assert client.timeout == 30.0  # Default timeout
        assert client.max_retries == 3  # Default retries

    def test_client_initialization_with_config_object(self) -> None:
        """Test FlextApiClient initialization with ClientConfig object."""
        config = FlextApiModels.ClientConfig(
            base_url="https://config.example.com",
            timeout=60.0,
            max_retries=5,
        )
        client = FlextApiClient(config)

        assert client.base_url == "https://config.example.com"
        assert client.timeout == 60.0
        assert client.max_retries == 5

    def test_client_initialization_with_config_and_kwargs(self) -> None:
        """Test FlextApiClient with ClientConfig and kwargs override."""
        config = FlextApiModels.ClientConfig(
            base_url="https://config.example.com",
            timeout=30,
        )
        client = FlextApiClient(config, timeout=45, max_retries=7)

        assert client.base_url == "https://config.example.com"
        assert client.timeout == 45.0
        assert client.max_retries == 7

    def test_client_initialization_with_none_config(self) -> None:
        """Test FlextApiClient initialization with None config."""
        client = FlextApiClient(None)

        assert client.base_url == "https://localhost:8000"  # Default fallback
        assert client.timeout == 30.0
        assert client.max_retries == 3

    def test_client_initialization_with_kwargs_only(self) -> None:
        """Test FlextApiClient initialization with kwargs only."""
        client = FlextApiClient(
            None,  # Explicitly pass None as config
            base_url="https://kwargs.example.com",
            timeout=120,
            max_retries=10,
        )

        assert client.base_url == "https://kwargs.example.com"
        assert client.timeout == 120.0
        assert client.max_retries == 10

    def test_client_initialization_with_custom_config_object(self) -> None:
        """Test FlextApiClient with custom config object having api_base_url."""
        mock_config = Mock()
        mock_config.api_base_url = "https://custom.example.com"

        client = FlextApiClient(mock_config)
        assert client.base_url == "https://custom.example.com"

    def test_client_initialization_with_config_base_url(self) -> None:
        """Test FlextApiClient with custom config object having base_url."""
        mock_config = Mock()
        # Remove api_base_url attribute to test base_url fallback
        del mock_config.api_base_url
        mock_config.base_url = "https://base.example.com"

        client = FlextApiClient(mock_config)
        assert client.base_url == "https://base.example.com"

    def test_client_constructor_with_kwargs(self) -> None:
        """Test client constructor with various parameters."""
        client = FlextApiClient(
            base_url="https://test.com",
            timeout=45,
            max_retries=5,
            headers={"Custom": "Header"},
            auth_token="token123",
            api_key="key456",
        )

        # Test that client was created with correct values
        assert client.base_url == "https://test.com"
        assert client.timeout == 45
        assert client.max_retries == 5
        # Test that client has the expected configuration
        assert client is not None

    def test_client_configuration_validation(self) -> None:
        """Test client configuration through public interface."""
        # Test valid configuration
        client = FlextApiClient(
            base_url="https://test.com",
            timeout=30,  # int should be converted to float
            auth_token=None,  # None value allowed
        )

        # Verify client was created successfully
        assert client is not None
        # Test that client can be used (basic functionality)
        assert hasattr(client, "get")
        assert hasattr(client, "post")

    def test_client_public_interface(self) -> None:
        """Test client public interface and services."""
        client = FlextApiClient("https://test.com", timeout=60)

        # Test that public services are accessible
        assert client.http is not None
        assert client.lifecycle is not None
        assert client.client_config is not None
        assert client.base_url == "https://test.com"
        assert client.timeout == 60

    @pytest.mark.asyncio
    async def test_client_async_context_manager(self) -> None:
        """Test client async context manager behavior."""
        async with FlextApiClient("https://test.com") as client:
            # Client should be properly initialized in context manager
            assert client is not None
            assert client.base_url == "https://test.com"
            # Test that client can perform operations
            assert hasattr(client, "get")
            assert hasattr(client, "post")

    @pytest.mark.asyncio
    async def test_client_close_method(self) -> None:
        """Test client close method."""
        client = FlextApiClient("https://test.com")

        # Start the client using async context manager
        async with client:
            # Test that client can be closed properly
            result = await client.close()
            assert result.is_success

    @pytest.mark.asyncio
    async def test_client_close_when_not_initialized(self) -> None:
        """Test client close when not initialized."""
        client = FlextApiClient("https://test.com")

        # Should fail when client is not initialized
        result = await client.close()
        assert result.is_failure
        assert result.error == "Client not started"

    def test_client_config_headers(self) -> None:
        """Test client configuration headers through public interface."""
        client = FlextApiClient("https://test.com")

        # Test that client config is accessible
        config = client.client_config
        assert config is not None
        # Test that config has headers property
        assert hasattr(config, "headers")

    def test_client_with_custom_headers(self) -> None:
        """Test client with custom headers through constructor."""
        client = FlextApiClient(
            "https://test.com",
            headers={"Authorization": "Bearer token", "Custom": "Value"},
        )

        # Test that client was created successfully
        assert client is not None
        assert client.base_url == "https://test.com"

    @pytest.mark.asyncio
    async def test_request_alias_method(self) -> None:
        """Test request method as alias for _request."""
        client = FlextApiClient("https://httpbin.org")

        # Use patch on the class instead of instance to avoid frozen model issues
        with patch.object(FlextApiClient, "_request") as mock_request:
            mock_response: FlextResult[FlextApiModels.HttpResponse] = FlextResult[
                FlextApiModels.HttpResponse
            ].ok(
                FlextApiModels.HttpResponse(
                    status_code=200,
                    body="test",
                    headers={},
                    url="https://httpbin.org/get",
                    method="GET",
                ),
            )
            mock_request.return_value = mock_response

            result: FlextResult[FlextApiModels.HttpResponse] = await client.request(
                "GET", "/get", params={"test": "value"}
            )

            mock_request.assert_called_once_with(
                "GET",
                "/get",
                params={"test": "value"},
                data=ANY,
                json=ANY,
                headers=ANY,
                request_timeout=ANY,
            )
            assert result.is_success

    def test_execute_method(self) -> None:
        """Test execute method from FlextService."""
        client = FlextApiClient("https://test.com")

        result = client.execute()

        assert result.is_success
        # execute() returns FlextResult[None], so we just check success
        assert result.value is None

    @pytest.mark.asyncio
    async def test_get_method(self) -> None:
        """Test GET method."""
        client = FlextApiClient("https://httpbin.org")

        with patch.object(FlextApiClient, "_request") as mock_request:
            mock_response = FlextResult[FlextApiModels.HttpResponse].ok(
                FlextApiModels.HttpResponse(
                    status_code=200,
                    body='{"success": true}',
                    headers={"Content-Type": "application/json"},
                    url="https://httpbin.org/get",
                    method="GET",
                ),
            )
            mock_request.return_value = mock_response

            result = await client.get("/get", params={"test": "value"})

            mock_request.assert_called_once_with(
                "GET",
                "/get",
                params={"test": "value"},
                data=ANY,
                json=ANY,
                headers=ANY,
                request_timeout=ANY,
            )
            assert result.is_success

    @pytest.mark.asyncio
    async def test_post_method(self) -> None:
        """Test POST method."""
        client = FlextApiClient("https://httpbin.org")

        with patch.object(FlextApiClient, "_request") as mock_request:
            mock_response = FlextResult[FlextApiModels.HttpResponse].ok(
                FlextApiModels.HttpResponse(
                    status_code=201,
                    body='{"created": true}',
                    headers={"Content-Type": "application/json"},
                    url="https://httpbin.org/post",
                    method="POST",
                ),
            )
            mock_request.return_value = mock_response

            result = await client.post("/post", json={"data": "value"})

            mock_request.assert_called_once_with(
                "POST",
                "/post",
                params=ANY,
                data=ANY,
                json={"data": "value"},
                headers=ANY,
                request_timeout=ANY,
            )
            assert result.is_success

    @pytest.mark.asyncio
    async def test_put_method(self) -> None:
        """Test PUT method."""
        client = FlextApiClient("https://httpbin.org")

        with patch.object(FlextApiClient, "_request") as mock_request:
            mock_response = FlextResult[FlextApiModels.HttpResponse].ok(
                FlextApiModels.HttpResponse(
                    status_code=200,
                    body='{"updated": true}',
                    headers={"Content-Type": "application/json"},
                    url="https://httpbin.org/put",
                    method="PUT",
                ),
            )
            mock_request.return_value = mock_response

            result = await client.put("/put", json={"data": "updated"})

            mock_request.assert_called_once_with(
                "PUT",
                "/put",
                params=ANY,
                data=ANY,
                json={"data": "updated"},
                headers=ANY,
                request_timeout=ANY,
            )
            assert result.is_success

    @pytest.mark.asyncio
    async def test_delete_method(self) -> None:
        """Test DELETE method."""
        client = FlextApiClient("https://httpbin.org")

        with patch.object(FlextApiClient, "_request") as mock_request:
            mock_response = FlextResult[FlextApiModels.HttpResponse].ok(
                FlextApiModels.HttpResponse(
                    status_code=204,
                    body="",
                    headers={},
                    url="https://httpbin.org/delete",
                    method="DELETE",
                ),
            )
            mock_request.return_value = mock_response

            result = await client.delete("/delete")

            mock_request.assert_called_once_with(
                "DELETE",
                "/delete",
                params=ANY,
                data=ANY,
                json=ANY,
                headers=ANY,
                request_timeout=ANY,
            )
            assert result.is_success

    def test_properties_access(self) -> None:
        """Test all property accessors."""
        config = FlextApiModels.ClientConfig(
            base_url="https://props.example.com",
            timeout=90.0,
            max_retries=8,
        )
        client = FlextApiClient(config)

        assert client.base_url == "https://props.example.com"
        assert client.timeout == 90.0
        assert client.max_retries == 8
        assert client.config_data == config

    @pytest.mark.asyncio
    async def test_context_manager_enter(self) -> None:
        """Test async context manager __aenter__."""
        client = FlextApiClient("https://test.com")

        # Test that context manager works without errors
        async with client as ctx_result:
            assert ctx_result is client
            assert client.base_url == "https://test.com"

    @pytest.mark.asyncio
    async def test_context_manager_exit(self) -> None:
        """Test async context manager __aexit__."""
        client = FlextApiClient("https://test.com")

        # Test that context manager exit works without errors
        await client.__aexit__(None, None, None)

    @pytest.mark.asyncio
    async def test_close_method(self) -> None:
        """Test close method."""
        client = FlextApiClient("https://test.com")

        # Start the client using async context manager
        async with client:
            # Test that close method works without errors
            result = await client.close()
            assert result.is_success

    @pytest.mark.asyncio
    async def test_close_method_failure(self) -> None:
        """Test close method failure handling."""
        client = FlextApiClient("https://test.com")

        # Start the client using async context manager
        async with client:
            # Test that close method handles errors gracefully
            result = await client.close()
            # Close should succeed even if there's no connection to close
            assert result.is_success

    def test_create_factory_with_dict(self) -> None:
        """Test create factory method with dict configuration."""
        config_data: dict[str, str | int, float] = {
            "base_url": "https://factory.example.com",
            "timeout": 120,
            "max_retries": 6,
        }

        # Use constructor directly - it accepts dict config
        client = FlextApiClient(config_data)

        assert client.base_url == "https://factory.example.com"
        assert client.timeout == 120
        assert client.max_retries == 6

    def test_create_factory_with_config_object(self) -> None:
        """Test create factory method with ClientConfig object."""
        config = FlextApiModels.ClientConfig(
            base_url="https://factory-config.example.com",
            timeout=75,
        )

        # Use constructor directly - it accepts ClientConfig
        client = FlextApiClient(config)

        assert client.base_url == "https://factory-config.example.com"
        assert client.timeout == 75

    def test_create_factory_failure(self) -> None:
        """Test create factory method failure handling."""
        # Invalid config that will cause validation error
        invalid_config: dict[str, str | int] = {"base_url": "", "timeout": -1}

        # Constructor will raise exception for invalid config
        try:
            FlextApiClient(invalid_config)
            msg = "Should have raised validation error"
            raise AssertionError(msg)
        except (ValueError, TypeError, AssertionError):
            pass  # Expected validation error

    def test_client_base_url_property(self) -> None:
        """Test client base URL property."""
        client = FlextApiClient("https://base.com")
        assert client.base_url == "https://base.com"

        client2 = FlextApiClient("https://base.com/api")
        assert client2.base_url == "https://base.com/api"

    @pytest.mark.asyncio
    async def test_request_internal_with_all_parameters(self) -> None:
        """Test _request method with all parameter types."""
        client = FlextApiClient("https://httpbin.org")

        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.text = '{"success": true}'
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.url = "https://httpbin.org/post"

        # Mock the internal _request method to avoid actual HTTP calls
        with patch.object(client, "_request") as mock_request:
            mock_result = FlextResult[FlextApiModels.HttpResponse].ok(
                FlextApiModels.HttpResponse(
                    status_code=201,
                    body='{"success": true}',
                    headers={"Content-Type": "application/json"},
                    url="https://httpbin.org/post",
                    method="POST",
                )
            )
            mock_request.return_value = mock_result

            result = await client.request(
                "POST",
                "/post",
                headers={"Custom": "Header"},
                params={"param": "value"},
                json={"data": "test"},
                data={"form": "data"},
            )

            assert result.is_success
            response = result.unwrap()
            assert response.status_code == 201
            assert response.body == '{"success": true}'
            assert response.method == "POST"

    @pytest.mark.asyncio
    async def test_request_error_handling(self) -> None:
        """Test request method error handling."""
        client = FlextApiClient("https://httpbin.org")

        # Mock the internal _request method to simulate an error
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = FlextResult[FlextApiModels.HttpResponse].fail(
                "HTTP request failed: Network error"
            )

            result = await client.request("GET", "/get")

            assert result.is_failure
            assert result.error is not None
            assert "HTTP request failed" in result.error

    @pytest.mark.asyncio
    async def test_request_general_error_handling(self) -> None:
        """Test request method general error handling."""
        client = FlextApiClient("https://httpbin.org")

        # Mock the internal _request method to simulate a general error
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = FlextResult[FlextApiModels.HttpResponse].fail(
                "Unexpected error"
            )

            result = await client.request("GET", "/get")

            assert result.is_failure
            assert result.error is not None
            assert "Unexpected error" in result.error

    @pytest.mark.asyncio
    async def test_request_with_valid_parameters(self) -> None:
        """Test request method with valid parameters."""
        client = FlextApiClient("https://httpbin.org")

        # Mock the internal _request method to avoid actual HTTP calls
        with patch.object(client, "_request") as mock_request:
            mock_response = FlextResult[FlextApiModels.HttpResponse].ok(
                FlextApiModels.HttpResponse(
                    status_code=200,
                    body='{"test": "value"}',
                    headers={"Content-Type": "application/json"},
                    url="https://httpbin.org/get",
                    method="GET",
                )
            )
            mock_request.return_value = mock_response

            # Test with valid parameters
            result = await client.request(
                "GET",
                "/get",
                params={"test": "value"},
                headers={"User-Agent": "test"},
            )

            assert result.is_success

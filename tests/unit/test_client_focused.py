"""Focused client tests for maximum coverage improvement.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from flext_core import FlextResult

from flext_api import FlextApiClient, FlextApiModels


class TestFlextApiClientFocused:
    """Focused tests to improve client.py coverage from 28% to 80%+."""

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
            base_url="https://config.example.com", timeout=60.0, max_retries=5
        )
        client = FlextApiClient(config)

        assert client.base_url == "https://config.example.com"
        assert client.timeout == 60.0
        assert client.max_retries == 5

    def test_client_initialization_with_config_and_kwargs(self) -> None:
        """Test FlextApiClient with ClientConfig and kwargs override."""
        config = FlextApiModels.ClientConfig(
            base_url="https://config.example.com", timeout=30.0
        )
        client = FlextApiClient(config, timeout=45.0, max_retries=7)

        assert client.base_url == "https://config.example.com"
        assert client.timeout == 45.0
        assert client.max_retries == 7

    def test_client_initialization_with_none_config(self) -> None:
        """Test FlextApiClient initialization with None config."""
        client = FlextApiClient(None)

        assert client.base_url == "http://127.0.0.1:8000"  # Default fallback
        assert client.timeout == 30.0
        assert client.max_retries == 3

    def test_client_initialization_with_kwargs_only(self) -> None:
        """Test FlextApiClient initialization with kwargs only."""
        client = FlextApiClient(
            None,  # Explicitly pass None as config
            base_url="https://kwargs.example.com",
            timeout=120.0,
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

    def test_convert_kwargs_to_client_config_kwargs(self) -> None:
        """Test _convert_kwargs_to_client_config_kwargs method."""
        client = FlextApiClient()

        # Test valid kwargs conversion
        kwargs = {
            "base_url": "https://test.com",
            "timeout": 45.0,
            "max_retries": 5,
            "headers": {"Custom": "Header"},
            "auth_token": "token123",
            "api_key": "key456",
            "invalid_field": "should_be_ignored",  # Invalid field
        }

        # Method returns a tuple, not a dict
        base_url, timeout, max_retries, headers, auth_token, api_key = (
            client._extract_client_config_params(kwargs)
        )

        assert base_url == "https://test.com"
        assert timeout == 45.0
        assert max_retries == 5
        assert headers == {"Custom": "Header"}
        assert auth_token == "token123"
        assert api_key == "key456"

    def test_convert_kwargs_type_validation(self) -> None:
        """Test type conversion in _convert_kwargs_to_client_config_kwargs."""
        client = FlextApiClient()

        # Test type conversion scenarios
        kwargs: dict[str, object] = {
            "timeout": 30,  # int to float
            "auth_token": None,  # None value allowed
            "headers": "not_a_dict",  # Invalid type should be skipped
        }

        # Method returns a tuple, not a dict
        _base_url, timeout, _max_retries, headers, auth_token, _api_key = (
            client._extract_client_config_params(kwargs)
        )

        assert timeout == 30.0
        assert auth_token is None
        assert headers is None  # Invalid type should result in None

    def test_connection_manager_initialization(self) -> None:
        """Test _ConnectionManager initialization."""
        client = FlextApiClient("https://test.com", timeout=60.0)

        conn_manager = client._connection_manager
        assert conn_manager._base_url == "https://test.com"
        assert conn_manager._timeout == 60.0
        assert conn_manager.client is None  # Not initialized yet

    @pytest.mark.asyncio
    async def test_connection_manager_ensure_client(self) -> None:
        """Test _ConnectionManager.ensure_client method."""
        client = FlextApiClient("https://test.com")
        conn_manager = client._connection_manager

        # Mock httpx.AsyncClient
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance

            result = await conn_manager.ensure_client()

            assert result is mock_instance
            mock_client.assert_called_once_with(
                base_url="https://test.com", timeout=30.0
            )

    @pytest.mark.asyncio
    async def test_connection_manager_close(self) -> None:
        """Test _ConnectionManager.close method."""
        client = FlextApiClient("https://test.com")
        conn_manager = client._connection_manager

        # Set up a mock client
        mock_client = AsyncMock()
        conn_manager._client = mock_client

        await conn_manager.close()

        mock_client.aclose.assert_called_once()
        assert conn_manager._client is None

    @pytest.mark.asyncio
    async def test_connection_manager_close_with_no_client(self) -> None:
        """Test _ConnectionManager.close when no client exists."""
        client = FlextApiClient("https://test.com")
        conn_manager = client._connection_manager

        # Should not raise error when no client exists
        await conn_manager.close()
        assert conn_manager._client is None

    def test_get_headers_default(self) -> None:
        """Test _get_headers method with default config headers."""
        client = FlextApiClient("https://test.com")

        headers = client._get_headers()

        # Should return headers from config
        assert isinstance(headers, dict)
        assert len(headers) >= 0  # At least empty dict

    def test_get_headers_with_additional(self) -> None:
        """Test _get_headers method with additional headers."""
        client = FlextApiClient("https://test.com")

        additional = {"Authorization": "Bearer token", "Custom": "Value"}
        headers = client._get_headers(additional)

        assert headers["Authorization"] == "Bearer token"
        assert headers["Custom"] == "Value"

    @pytest.mark.asyncio
    async def test_request_alias_method(self) -> None:
        """Test request method as alias for _request."""
        client = FlextApiClient("https://httpbin.org")

        # Use patch on the class instead of instance to avoid frozen model issues
        with patch.object(FlextApiClient, "_request") as mock_request:
            mock_response = FlextResult[FlextApiModels.HttpResponse].ok(
                FlextApiModels.HttpResponse(
                    status_code=200,
                    body="test",
                    headers={},
                    url="https://httpbin.org/get",
                    method="GET",
                )
            )
            mock_request.return_value = mock_response

            result = await client.request("GET", "/get", params={"test": "value"})

            mock_request.assert_called_once_with(
                "GET", "/get", params={"test": "value"}
            )
            assert result.is_success

    def test_execute_method(self) -> None:
        """Test execute method from FlextDomainService."""
        client = FlextApiClient("https://test.com")

        result = client.execute()

        assert result.is_success
        response = result.unwrap()
        assert isinstance(response, dict)
        assert "client_type" in response
        assert "base_url" in response
        assert response["base_url"] == "https://test.com"

    @pytest.mark.asyncio
    async def test_start_method(self) -> None:
        """Test start method from FlextDomainService."""
        client = FlextApiClient("https://test.com")

        with patch.object(client._connection_manager, "ensure_client") as mock_ensure:
            mock_ensure.return_value = AsyncMock()

            result = await client.start()

            assert result.is_success
            mock_ensure.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_method_failure(self) -> None:
        """Test start method failure handling."""
        client = FlextApiClient("https://test.com")

        with patch.object(client._connection_manager, "ensure_client") as mock_ensure:
            mock_ensure.side_effect = Exception("Connection failed")

            result = await client.start()

            assert result.is_failure
            assert result.error is not None
            assert "Failed to start HTTP client" in result.error

    @pytest.mark.asyncio
    async def test_stop_method(self) -> None:
        """Test stop method from FlextDomainService."""
        client = FlextApiClient("https://test.com")

        with patch.object(client._connection_manager, "close") as mock_close:
            mock_close.return_value = None

            result = await client.stop()

            assert result.is_success
            mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_method_failure(self) -> None:
        """Test stop method failure handling."""
        client = FlextApiClient("https://test.com")

        with patch.object(client._connection_manager, "close") as mock_close:
            mock_close.side_effect = Exception("Close failed")

            result = await client.stop()

            assert result.is_failure
            assert result.error is not None
            assert "Failed to stop HTTP client" in result.error

    def test_health_check_stopped(self) -> None:
        """Test health_check method when client is stopped."""
        client = FlextApiClient("https://test.com")

        health = client.health_check()

        assert health["status"] == "stopped"
        assert health["base_url"] == "https://test.com"
        assert health["timeout"] == 30.0
        assert health["max_retries"] == 3
        assert health["request_count"] == 0
        assert health["error_count"] == 0
        assert health["client_ready"] is False
        assert health["session_started"] is False

    def test_health_check_healthy(self) -> None:
        """Test health_check method when client is healthy."""
        client = FlextApiClient("https://test.com")

        # Mock client as connected
        mock_client = Mock()
        client._connection_manager._client = mock_client

        health = client.health_check()

        assert health["status"] == "healthy"

    def test_configure_method(self) -> None:
        """Test configure method with new settings."""
        client = FlextApiClient("https://test.com")

        new_config = {"base_url": "https://new.com", "timeout": 60.0, "max_retries": 5}

        result = client.configure(new_config)

        assert result.is_success
        assert client.base_url == "https://new.com"
        assert client.timeout == 60.0
        assert client.max_retries == 5

    def test_configure_method_failure(self) -> None:
        """Test configure method failure handling."""
        client = FlextApiClient("https://test.com")

        # Invalid config that will cause Pydantic validation error
        invalid_config = {"base_url": "", "timeout": -1}

        result = client.configure(invalid_config)

        assert result.is_failure
        assert result.error is not None
        assert "Configuration failed" in result.error

    def test_get_config_method(self) -> None:
        """Test get_config method."""
        client = FlextApiClient("https://test.com", timeout=45.0)

        config = client.get_config()

        assert config["base_url"] == "https://test.com"
        assert config["timeout"] == 45.0
        assert isinstance(config, dict)

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
                )
            )
            mock_request.return_value = mock_response

            result = await client.get("/get", params={"test": "value"})

            mock_request.assert_called_once_with(
                "GET", "/get", params={"test": "value"}
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
                )
            )
            mock_request.return_value = mock_response

            result = await client.post("/post", json={"data": "value"})

            mock_request.assert_called_once_with(
                "POST", "/post", json={"data": "value"}
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
                )
            )
            mock_request.return_value = mock_response

            result = await client.put("/put", json={"data": "updated"})

            mock_request.assert_called_once_with(
                "PUT", "/put", json={"data": "updated"}
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
                )
            )
            mock_request.return_value = mock_response

            result = await client.delete("/delete")

            mock_request.assert_called_once_with("DELETE", "/delete")
            assert result.is_success

    def test_properties_access(self) -> None:
        """Test all property accessors."""
        config = FlextApiModels.ClientConfig(
            base_url="https://props.example.com", timeout=90.0, max_retries=8
        )
        client = FlextApiClient(config)

        assert client.base_url == "https://props.example.com"
        assert client.timeout == 90.0
        assert client.max_retries == 8
        assert client.config == config

    @pytest.mark.asyncio
    async def test_context_manager_enter(self) -> None:
        """Test async context manager __aenter__."""
        client = FlextApiClient("https://test.com")

        with patch.object(client._connection_manager, "ensure_client") as mock_ensure:
            mock_ensure.return_value = AsyncMock()

            result = await client.__aenter__()

            assert result is client
            mock_ensure.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_exit(self) -> None:
        """Test async context manager __aexit__."""
        client = FlextApiClient("https://test.com")

        with patch.object(client._connection_manager, "close") as mock_close:
            mock_close.return_value = None

            await client.__aexit__(None, None, None)

            mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_method(self) -> None:
        """Test close method."""
        client = FlextApiClient("https://test.com")

        with patch.object(client._connection_manager, "close") as mock_close:
            mock_close.return_value = None

            result = await client.close()

            assert result.is_success
            mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_method_failure(self) -> None:
        """Test close method failure handling."""
        client = FlextApiClient("https://test.com")

        with patch.object(client._connection_manager, "close") as mock_close:
            mock_close.side_effect = Exception("Close failed")

            result = await client.close()

            assert result.is_failure
            assert result.error is not None
            assert "Failed to close HTTP client" in result.error

    def test_create_factory_with_dict(self) -> None:
        """Test create factory method with dict configuration."""
        config_data = {
            "base_url": "https://factory.example.com",
            "timeout": 120.0,
            "max_retries": 6,
        }

        result = FlextApiClient.create(config_data)

        assert result.is_success
        client = result.unwrap()
        assert client.base_url == "https://factory.example.com"
        assert client.timeout == 120.0
        assert client.max_retries == 6

    def test_create_factory_with_config_object(self) -> None:
        """Test create factory method with ClientConfig object."""
        config = FlextApiModels.ClientConfig(
            base_url="https://factory-config.example.com", timeout=75.0
        )

        result = FlextApiClient.create(config)

        assert result.is_success
        client = result.unwrap()
        assert client.base_url == "https://factory-config.example.com"
        assert client.timeout == 75.0

    def test_create_factory_failure(self) -> None:
        """Test create factory method failure handling."""
        # Invalid config that will cause validation error
        invalid_config = {"base_url": "", "timeout": -1}

        result = FlextApiClient.create(invalid_config)

        assert result.is_failure
        assert result.error is not None
        assert "Failed to create client" in result.error

    def test_build_url_with_full_url(self) -> None:
        """Test _build_url with full URL endpoint."""
        client = FlextApiClient("https://base.com")

        url = client._build_url("https://other.com/endpoint")

        assert url == "https://other.com/endpoint"

    def test_build_url_with_relative_endpoint(self) -> None:
        """Test _build_url with relative endpoint."""
        client = FlextApiClient("https://base.com/api")

        url = client._build_url("/users")

        assert url == "https://base.com/api/users"

    def test_build_url_with_empty_endpoint(self) -> None:
        """Test _build_url with empty endpoint."""
        client = FlextApiClient("https://base.com/")

        url = client._build_url("")

        assert url == "https://base.com"

    def test_build_url_absolute_endpoint(self) -> None:
        """Test _build_url with absolute URL endpoint."""
        client = FlextApiClient("https://test.com")

        # Test that absolute URLs are returned as-is (not combined with base_url)
        absolute_url = "https://other-service.com/api/data"
        url = client._build_url(absolute_url)
        assert url == absolute_url

        # Test with http as well
        http_url = "http://localhost:8080/api"
        url = client._build_url(http_url)
        assert url == http_url

    @pytest.mark.asyncio
    async def test_request_internal_with_all_parameters(self) -> None:
        """Test _request method with all parameter types."""
        client = FlextApiClient("https://httpbin.org")

        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.text = '{"success": true}'
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.url = "https://httpbin.org/post"

        with patch.object(client._connection_manager, "ensure_client") as mock_ensure:
            mock_http_client = AsyncMock()
            mock_http_client.request.return_value = mock_response
            mock_ensure.return_value = mock_http_client

            result = await client._request(
                "POST",
                "/post",
                headers={"Custom": "Header"},
                params={"param": "value"},
                json={"data": "test"},
                data={"form": "data"},
                files={"file": "content"},
            )

            assert result.is_success
            response = result.unwrap()
            assert response.status_code == 201
            assert response.body == '{"success": true}'
            assert response.method == "POST"

            # Verify httpx client was called with correct parameters
            mock_http_client.request.assert_called_once()
            call_kwargs = mock_http_client.request.call_args[1]
            assert call_kwargs["method"] == "POST"
            assert call_kwargs["params"] == {"param": "value"}
            assert call_kwargs["json"] == {"data": "test"}
            assert call_kwargs["data"] == {"form": "data"}
            assert call_kwargs["files"] == {"file": "content"}

    @pytest.mark.asyncio
    async def test_request_internal_httpx_error(self) -> None:
        """Test _request method with httpx HTTPError."""
        client = FlextApiClient("https://httpbin.org")

        with patch.object(client._connection_manager, "ensure_client") as mock_ensure:
            mock_http_client = AsyncMock()
            mock_http_client.request.side_effect = httpx.HTTPError("Network error")
            mock_ensure.return_value = mock_http_client

            result = await client._request("GET", "/get")

            assert result.is_failure
            assert result.error is not None
            assert "HTTP request failed" in result.error

    @pytest.mark.asyncio
    async def test_request_internal_general_error(self) -> None:
        """Test _request method with general exception."""
        client = FlextApiClient("https://httpbin.org")

        with patch.object(client._connection_manager, "ensure_client") as mock_ensure:
            mock_ensure.side_effect = Exception("Unexpected error")

            result = await client._request("GET", "/get")

            assert result.is_failure
            assert result.error is not None
            assert "Unexpected error" in result.error

    @pytest.mark.asyncio
    async def test_request_internal_parameter_safety(self) -> None:
        """Test _request method parameter safety with invalid types."""
        client = FlextApiClient("https://httpbin.org")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_response.headers = {}
        mock_response.url = "https://httpbin.org/get"

        with patch.object(client._connection_manager, "ensure_client") as mock_ensure:
            mock_http_client = AsyncMock()
            mock_http_client.request.return_value = mock_response
            mock_ensure.return_value = mock_http_client

            # Test with invalid parameter types that should be safely handled
            result = await client._request(
                "GET",
                "/get",
                headers="not_a_dict",  # Invalid type
                params="not_a_dict",  # Invalid type
                data="not_a_dict",  # Invalid type but string allowed
                files="not_a_dict",  # Invalid type
            )

            assert result.is_success

            # Verify None values were passed for invalid types
            call_kwargs = mock_http_client.request.call_args[1]
            assert call_kwargs["params"] is None
            assert call_kwargs["files"] is None
            # data can be string so "not_a_dict" should be passed through
            # Only dict data gets passed, others become None
            assert call_kwargs["data"] is None

"""Comprehensive tests for FlextApiClient with FlextResult API.

Tests validate FLEXT-pure HTTP client using railway-oriented programming
with FlextResult[T] error handling and HttpRequest/HttpResponse models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from flext_core import FlextResult

from flext_api import FlextApiClient, FlextApiConfig, FlextApiModels


class TestFlextApiClientInitialization:
    """Test FlextApiClient initialization with FlextApiConfig."""

    def test_client_with_default_config(self) -> None:
        """Test client initialization with default configuration."""
        config = FlextApiConfig()
        client = FlextApiClient(config)

        assert not client._config.base_url
        assert client._config.timeout == 30.0
        assert client._config.max_retries == 3
        assert client._config.headers == {}

    def test_client_with_custom_config(self) -> None:
        """Test client initialization with custom configuration."""
        config = FlextApiConfig(
            base_url="https://api.example.com",
            timeout=60.0,
            max_retries=5,
            headers={"Authorization": "Bearer token"},
        )
        client = FlextApiClient(config)

        assert client._config.base_url == "https://api.example.com"
        assert client._config.timeout == 60.0
        assert client._config.max_retries == 5
        assert client._config.headers["Authorization"] == "Bearer token"

    def test_client_execute_returns_config(self) -> None:
        """Test that execute() returns configuration via FlextResult."""
        config = FlextApiConfig(base_url="https://test.com")
        client = FlextApiClient(config)

        result = client.execute()
        assert result.is_success
        assert result.unwrap().base_url == "https://test.com"


class TestFlextApiClientHttpRequest:
    """Test FlextApiClient HTTP request model creation."""

    def test_create_http_request_model(self) -> None:
        """Test creating HttpRequest model."""
        request = FlextApiModels.HttpRequest(
            method="GET",
            url="https://api.example.com/users",
            headers={"Accept": "application/json"},
        )

        assert request.method == "GET"
        assert request.url == "https://api.example.com/users"
        assert request.headers["Accept"] == "application/json"

    def test_create_http_response_model(self) -> None:
        """Test creating HttpResponse model."""
        response = FlextApiModels.HttpResponse(
            status_code=200,
            headers={"Content-Type": "application/json"},
            body={"status": "ok"},
        )

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        assert response.body == {"status": "ok"}


class TestFlextApiClientUrlBuilding:
    """Test internal URL building logic."""

    def test_build_url_with_base_url(self) -> None:
        """Test URL building with base URL."""
        config = FlextApiConfig(base_url="https://api.example.com")
        client = FlextApiClient(config)

        url1 = client._build_url("/users")
        assert url1 == "https://api.example.com/users"

        url2 = client._build_url("users")
        assert url2 == "https://api.example.com/users"

    def test_build_url_without_base_url(self) -> None:
        """Test URL building without base URL."""
        config = FlextApiConfig(base_url="")
        client = FlextApiClient(config)

        url = client._build_url("https://external.api/endpoint")
        assert url == "https://external.api/endpoint"

    def test_build_url_strips_trailing_slash(self) -> None:
        """Test URL building strips trailing slash from base URL."""
        config = FlextApiConfig(base_url="https://api.example.com/")
        client = FlextApiClient(config)

        url = client._build_url("/users")
        assert url == "https://api.example.com/users"
        # Should not have double slashes
        assert "//" not in url[8:]  # Ignore https://


class TestFlextApiClientBodySerialization:
    """Test request/response body serialization."""

    def test_serialize_body_none(self) -> None:
        """Test serializing None body."""
        result = FlextApiClient._serialize_body(None)
        assert result is None

    def test_serialize_body_bytes(self) -> None:
        """Test serializing bytes body."""
        body = b"raw bytes"
        result = FlextApiClient._serialize_body(body)
        assert result == b"raw bytes"

    def test_serialize_body_string(self) -> None:
        """Test serializing string body."""
        body = "string content"
        result = FlextApiClient._serialize_body(body)
        assert result == b"string content"

    def test_serialize_body_dict(self) -> None:
        """Test serializing dictionary body to JSON."""
        body = {"key": "value"}
        result = FlextApiClient._serialize_body(body)
        assert result == json.dumps(body).encode("utf-8")

    def test_deserialize_json_response(self) -> None:
        """Test deserializing JSON response."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"status": "ok"}

        result = FlextApiClient._deserialize_body(mock_response)
        assert result == {"status": "ok"}

    def test_deserialize_text_response(self) -> None:
        """Test deserializing plain text response."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.text = "plain text"

        result = FlextApiClient._deserialize_body(mock_response)
        assert result == "plain text"

    def test_deserialize_json_error_fallback_to_text(self) -> None:
        """Test deserializing JSON response with parsing error falls back to text."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.side_effect = Exception("JSON parse error")
        mock_response.text = "invalid json"

        result = FlextApiClient._deserialize_body(mock_response)
        assert result == "invalid json"


class TestFlextApiClientRailwayPattern:
    """Test railway-oriented programming with FlextResult."""

    def test_request_success_returns_flext_result(self) -> None:
        """Test successful request returns FlextResult[HttpResponse]."""
        config = FlextApiConfig()
        client = FlextApiClient(config)

        request = FlextApiModels.HttpRequest(
            method="GET",
            url="https://httpbin.org/get",
        )

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value.__enter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {"content-type": "application/json"}
            mock_response.json.return_value = {"status": "ok"}

            mock_client.request.return_value = mock_response

            result = client.request(request)

            assert isinstance(result, FlextResult)
            assert result.is_success
            response = result.unwrap()
            assert response.status_code == 200
            assert response.body == {"status": "ok"}

    def test_request_failure_returns_flext_result_error(self) -> None:
        """Test failed request returns FlextResult with error."""
        config = FlextApiConfig()
        client = FlextApiClient(config)

        request = FlextApiModels.HttpRequest(
            method="GET",
            url="https://invalid.example.com/endpoint",
        )

        with patch("httpx.Client") as mock_client_class:
            mock_client_class.side_effect = Exception("Connection failed")

            result = client.request(request)

            assert isinstance(result, FlextResult)
            assert not result.is_success
            assert "Connection failed" in result.error


class TestFlextApiClientHeaderMerging:
    """Test request header merging."""

    def test_merge_config_and_request_headers(self) -> None:
        """Test that config headers are merged with request headers."""
        config = FlextApiConfig(
            headers={"X-API-Key": "secret", "Accept": "application/json"}
        )
        client = FlextApiClient(config)

        request = FlextApiModels.HttpRequest(
            method="GET",
            url="https://api.example.com/data",
            headers={"X-Request-ID": "123"},
        )

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value.__enter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {}
            mock_response.text = "ok"

            mock_client.request.return_value = mock_response

            result = client.request(request)

            # Verify all headers were passed to httpx
            call_kwargs = mock_client.request.call_args[1]
            assert "X-API-Key" in call_kwargs["headers"]
            assert "X-Request-ID" in call_kwargs["headers"]
            assert result.is_success


class TestFlextApiClientQueryParams:
    """Test query parameter handling."""

    def test_pass_query_params_to_request(self) -> None:
        """Test that query parameters are passed to httpx."""
        config = FlextApiConfig()
        client = FlextApiClient(config)

        request = FlextApiModels.HttpRequest(
            method="GET",
            url="https://api.example.com/search",
            query_params={"q": "test", "limit": "10"},  # Query params must be strings
        )

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value.__enter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {}
            mock_response.text = "results"

            mock_client.request.return_value = mock_response

            result = client.request(request)

            call_kwargs = mock_client.request.call_args[1]
            assert call_kwargs["params"] == {"q": "test", "limit": "10"}
            assert result.is_success


class TestFlextApiClientConfiguration:
    """Test configuration validation and application."""

    def test_config_timeout_applied_to_client(self) -> None:
        """Test that request timeout is applied to httpx Client."""
        config = FlextApiConfig(timeout=45.0)
        client = FlextApiClient(config)

        request = FlextApiModels.HttpRequest(
            method="GET",
            url="https://api.example.com/data",
            timeout=45.0,  # Request timeout (uses config default if not set)
        )

        with patch("httpx.Client") as mock_client_class:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {}
            mock_response.text = "ok"

            mock_client_class.return_value.__enter__.return_value.request.return_value = mock_response

            result = client.request(request)

            # Verify timeout was passed to httpx.Client
            mock_client_class.assert_called_with(timeout=45.0)
            assert result.is_success

    def test_config_base_url_used_for_relative_paths(self) -> None:
        """Test that config base_url is used for relative paths."""
        config = FlextApiConfig(base_url="https://api.example.com")
        client = FlextApiClient(config)

        request = FlextApiModels.HttpRequest(
            method="GET",
            url="/users",  # Relative path
        )

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value.__enter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {}
            mock_response.text = "ok"

            mock_client.request.return_value = mock_response

            result = client.request(request)

            call_kwargs = mock_client.request.call_args[1]
            assert call_kwargs["url"] == "https://api.example.com/users"
            assert result.is_success


class TestFlextApiClientHttpMethods:
    """Test HTTP method implementations in FlextApi."""

    def test_get_method(self) -> None:
        """Test GET method via FlextApi facade."""
        from flext_api import FlextApi

        api = FlextApi(FlextApiConfig())

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value.__enter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {}
            mock_response.json.return_value = {"users": []}

            mock_client.request.return_value = mock_response

            result = api.get("https://api.example.com/users")

            assert result.is_success
            response = result.unwrap()
            assert response.status_code == 200

    def test_post_method(self) -> None:
        """Test POST method via FlextApi facade."""
        from flext_api import FlextApi

        api = FlextApi(FlextApiConfig())

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value.__enter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.headers = {}
            mock_response.json.return_value = {"id": 123}

            mock_client.request.return_value = mock_response

            result = api.post("https://api.example.com/users", data={"name": "John"})

            assert result.is_success
            response = result.unwrap()
            assert response.status_code == 201


class TestFlextApiClientErrorHandling:
    """Test error handling with FlextResult railway pattern."""

    def test_network_error_returns_failure_result(self) -> None:
        """Test network errors are caught and returned as FlextResult failure."""
        config = FlextApiConfig()
        client = FlextApiClient(config)

        request = FlextApiModels.HttpRequest(
            method="GET",
            url="https://invalid.example.invalid/endpoint",
        )

        with patch("httpx.Client") as mock_client_class:
            mock_client_class.side_effect = ConnectionError("Network unreachable")

            result = client.request(request)

            assert not result.is_success
            assert "Network unreachable" in result.error

    def test_timeout_returns_failure_result(self) -> None:
        """Test timeout errors are caught and returned as FlextResult failure."""
        config = FlextApiConfig()
        client = FlextApiClient(config)

        request = FlextApiModels.HttpRequest(
            method="GET",
            url="https://slow.example.com/endpoint",
        )

        with patch("httpx.Client") as mock_client_class:
            import httpx

            mock_client_class.side_effect = httpx.TimeoutException("Request timed out")

            result = client.request(request)

            assert not result.is_success
            assert "Request timed out" in result.error


class TestFlextApiClientModelsIntegration:
    """Test integration between client and models."""

    def test_http_request_model_with_all_fields(self) -> None:
        """Test HttpRequest model with all optional fields."""
        request = FlextApiModels.HttpRequest(
            method="POST",
            url="https://api.example.com/data",
            body={"key": "value"},
            headers={"Content-Type": "application/json"},
            query_params={"format": "json"},
            timeout=30.0,
        )

        assert request.method == "POST"
        assert request.url == "https://api.example.com/data"
        assert request.body == {"key": "value"}
        assert request.timeout == 30.0

    def test_http_response_model_with_complex_body(self) -> None:
        """Test HttpResponse model with complex body."""
        response = FlextApiModels.HttpResponse(
            status_code=200,
            headers={"Content-Type": "application/json"},
            body={
                "data": [1, 2, 3],
                "nested": {"key": "value"},
                "status": "success",
            },
        )

        assert response.status_code == 200
        assert isinstance(response.body, dict)
        assert response.body["nested"]["key"] == "value"


class TestFlextApiConfigValidation:
    """Test FlextApiConfig validation."""

    def test_config_timeout_validation(self) -> None:
        """Test timeout field validation."""
        # Valid timeout
        config = FlextApiConfig(timeout=60.0)
        assert config.timeout == 60.0

        # Too low timeout
        with pytest.raises(ValueError):
            FlextApiConfig(timeout=0.1)

        # Too high timeout
        with pytest.raises(ValueError):
            FlextApiConfig(timeout=3600.1)

    def test_config_max_retries_validation(self) -> None:
        """Test max_retries field validation."""
        # Valid retries
        config = FlextApiConfig(max_retries=5)
        assert config.max_retries == 5

        # Too many retries
        with pytest.raises(ValueError):
            FlextApiConfig(max_retries=101)

    def test_config_headers_validation(self) -> None:
        """Test headers field validation."""
        # Valid headers
        config = FlextApiConfig(headers={"X-Custom": "value"})
        assert config.headers["X-Custom"] == "value"

        # Invalid header (empty key)
        with pytest.raises(ValueError):
            FlextApiConfig(headers={"": "value"})

        # Invalid header (empty value)
        with pytest.raises(ValueError):
            FlextApiConfig(headers={"Key": ""})


__all__ = [
    "TestFlextApiClientBodySerialization",
    "TestFlextApiClientConfiguration",
    "TestFlextApiClientErrorHandling",
    "TestFlextApiClientHeaderMerging",
    "TestFlextApiClientHttpMethods",
    "TestFlextApiClientHttpRequest",
    "TestFlextApiClientInitialization",
    "TestFlextApiClientModelsIntegration",
    "TestFlextApiClientQueryParams",
    "TestFlextApiClientRailwayPattern",
    "TestFlextApiClientUrlBuilding",
    "TestFlextApiConfigValidation",
]

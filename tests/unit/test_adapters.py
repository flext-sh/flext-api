"""Comprehensive tests for FlextApiAdapters with FlextResult API.

Tests validate HTTP protocol adaptation using railway-oriented programming
with FlextResult[T] error handling. ALL TESTS USE REAL FUNCTIONALITY - NO MOCKS.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_api.adapters import FlextApiAdapters
from flext_api.models import FlextApiModels


class TestFlextApiAdaptersHttpProtocol:
    """Test HTTP protocol adaptation methods."""

    def test_adapt_http_request_to_websocket_success(self) -> None:
        """Test successful HTTP request to WebSocket adaptation."""
        # Create test HTTP request
        request = FlextApiModels.HttpRequest(
            method="GET",
            url="https://api.example.com/test",
            headers={"Content-Type": "application/json"},
            body={"key": "value"},
        )

        # Adapt to WebSocket
        result = FlextApiAdapters.HttpProtocol.adapt_http_request_to_websocket(request)

        # Verify success
        assert result.is_success
        message = result.value
        assert isinstance(message, dict)
        assert message["type"] == "request"
        assert message["method"] == "GET"
        assert message["url"] == "https://api.example.com/test"
        assert message["headers"] == {"Content-Type": "application/json"}
        assert message["body"] == {"key": "value"}

    def test_adapt_http_request_to_websocket_with_string_body(self) -> None:
        """Test HTTP request adaptation with string body."""
        request = FlextApiModels.HttpRequest(
            method="POST",
            url="https://api.example.com/test",
            body="plain text body",
        )

        result = FlextApiAdapters.HttpProtocol.adapt_http_request_to_websocket(request)

        assert result.is_success
        message = result.value
        assert message["body"] == "plain text body"

    def test_adapt_http_request_to_websocket_with_dict_body(self) -> None:
        """Test HTTP request adaptation with dict body."""
        request = FlextApiModels.HttpRequest(
            method="POST",
            url="https://api.example.com/test",
            body={"nested": {"data": True}},
        )

        result = FlextApiAdapters.HttpProtocol.adapt_http_request_to_websocket(request)

        assert result.is_success
        message = result.value
        assert message["body"] == {"nested": {"data": True}}

    def test_adapt_websocket_message_to_http_response_success(self) -> None:
        """Test successful WebSocket message to HTTP response adaptation."""
        websocket_message = {
            "status": 201,
            "headers": {"Content-Type": "application/json"},
            "body": {"result": "success"},
        }

        result = FlextApiAdapters.HttpProtocol.adapt_websocket_message_to_http_response(
            websocket_message,
        )

        assert result.is_success
        response = result.value
        assert isinstance(response, FlextApiModels.HttpResponse)
        assert response.status_code == 201
        assert response.headers == {"Content-Type": "application/json"}
        assert response.body == {"result": "success"}

    def test_adapt_websocket_message_to_http_response_default_values(self) -> None:
        """Test WebSocket adaptation with default values."""
        websocket_message = {"body": {"message": "simple response"}}

        result = FlextApiAdapters.HttpProtocol.adapt_websocket_message_to_http_response(
            websocket_message,
        )

        assert result.is_success
        response = result.value
        assert response.status_code == 200
        assert response.headers == {}
        assert response.body == {"message": "simple response"}


class TestFlextApiAdaptersFormatConverter:
    """Test format conversion methods."""

    def test_convert_json_to_messagepack_success(self) -> None:
        """Test successful JSON to MessagePack conversion."""
        data = {"key": "value", "number": 42}

        result = FlextApiAdapters.FormatConverter.convert_json_to_messagepack(data)

        assert result.is_success
        packed = result.value
        assert isinstance(packed, bytes)
        assert len(packed) > 0

    def test_convert_json_to_cbor_success(self) -> None:
        """Test successful JSON to CBOR conversion."""
        data = {"key": "value", "number": 42}

        result = FlextApiAdapters.FormatConverter.convert_json_to_cbor(data)

        assert result.is_success
        packed = result.value
        assert isinstance(packed, bytes)
        assert len(packed) > 0


class TestFlextApiAdaptersSchema:
    """Test schema adaptation methods."""

    def test_adapt_openapi_to_graphql_schema_success(self) -> None:
        """Test successful OpenAPI to GraphQL schema adaptation."""
        openapi_spec = {"openapi": "3.0.0", "info": {"title": "Test API"}}

        result = FlextApiAdapters.Schema.adapt_openapi_to_graphql_schema(openapi_spec)

        assert result.is_success
        schema = result.value
        assert isinstance(schema, dict)
        assert "type" in schema
        assert "query" in schema
        assert "mutation" in schema


class TestFlextApiAdaptersRequestTransformer:
    """Test request/response transformation methods."""

    def test_transform_request_for_websocket_success(self) -> None:
        """Test successful request transformation for WebSocket."""
        request = FlextApiModels.HttpRequest(
            method="GET",
            url="https://api.example.com/test",
            body={"key": "value"},
        )

        result = FlextApiAdapters.RequestTransformer.transform_request_for_protocol(
            request,
            "websocket",
        )

        assert result.is_success
        transformed = result.value
        assert isinstance(transformed, dict)
        assert transformed["type"] == "request"
        assert transformed["method"] == "GET"

    def test_transform_request_for_unknown_protocol(self) -> None:
        """Test request transformation for unknown protocol returns original."""
        request = FlextApiModels.HttpRequest(
            method="GET",
            url="https://api.example.com/test",
        )

        result = FlextApiAdapters.RequestTransformer.transform_request_for_protocol(
            request,
            "unknown",
        )

        assert result.is_success
        assert result.value is request

    def test_transform_response_for_websocket_success(self) -> None:
        """Test successful response transformation from WebSocket."""
        websocket_response = {
            "status": 200,
            "body": {"result": "success"},
            "headers": {"Content-Type": "application/json"},
        }

        result = FlextApiAdapters.RequestTransformer.transform_response_for_protocol(
            websocket_response,
            "websocket",
        )

        assert result.is_success
        transformed = result.value
        assert isinstance(transformed, FlextApiModels.HttpResponse)
        assert transformed.status_code == 200
        assert transformed.body == {"result": "success"}

    def test_transform_response_for_unknown_protocol(self) -> None:
        """Test response transformation for unknown protocol returns original."""
        response = FlextApiModels.HttpResponse(
            status_code=200,
            body={"result": "success"},
        )

        result = FlextApiAdapters.RequestTransformer.transform_response_for_protocol(
            response,
            "unknown",
        )

        assert result.is_success
        assert result.value is response

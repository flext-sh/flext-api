"""Simple unit tests for adapters functionality.

Tests for protocol and format adapters.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.adapters import (
    GraphQLToHttpAdapter,
    HttpToWebSocketAdapter,
    LegacyApiAdapter,
    SchemaAdapter,
)
from flext_api.models import FlextApiModels

# Type aliases for convenience
HttpRequest = FlextApiModels.HttpRequest
HttpResponse = FlextApiModels.HttpResponse


class TestHttpToWebSocketAdapter:
    """Test suite for HttpToWebSocketAdapter."""

    def test_adapter_initialization(self) -> None:
        """Test adapter initialization."""
        adapter = HttpToWebSocketAdapter()

        assert adapter is not None

    def test_adapt_http_request_to_websocket(self) -> None:
        """Test adapting HTTP request to WebSocket message."""
        adapter = HttpToWebSocketAdapter()

        request = HttpRequest(
            method="GET",
            url="/test",
            headers={"Content-Type": "application/json"},
        )

        result = adapter.adapt_request(request)

        assert result.is_success
        message = result.unwrap()
        assert message["type"] == "request"
        assert message["method"] == "GET"
        assert message["url"] == "/test"

    def test_adapt_websocket_message_to_http_response(self) -> None:
        """Test adapting WebSocket message to HTTP response."""
        adapter = HttpToWebSocketAdapter()

        message = {
            "status": 200,
            "body": {"result": "success"},
            "headers": {"Content-Type": "application/json"},
            "url": "/test",
            "method": "GET",
        }

        result = adapter.adapt_response(message)

        assert result.is_success
        response = result.unwrap()
        assert response.status_code == 200
        assert response.body["result"] == "success"


class TestGraphQLToHttpAdapter:
    """Test suite for GraphQLToHttpAdapter."""

    def test_adapter_initialization(self) -> None:
        """Test adapter initialization."""
        adapter = GraphQLToHttpAdapter()

        assert adapter is not None
        assert adapter._endpoint == "/graphql"

    def test_adapter_custom_endpoint(self) -> None:
        """Test adapter with custom endpoint."""
        adapter = GraphQLToHttpAdapter(endpoint="/api/graphql")

        assert adapter._endpoint == "/api/graphql"

    def test_adapt_query_to_http_request(self) -> None:
        """Test adapting GraphQL query to HTTP request."""
        adapter = GraphQLToHttpAdapter()

        query = "query { user(id: 1) { name } }"
        variables = {"id": 1}

        result = adapter.adapt_query_to_request(query, variables)

        assert result.is_success
        request = result.unwrap()
        assert request.method == "POST"
        assert request.url == "/graphql"
        # Body is a dict with query and variables
        assert isinstance(request.body, dict)
        assert request.body["query"] == query
        assert request.body["variables"] == variables

    def test_adapt_http_response_to_graphql_result(self) -> None:
        """Test adapting HTTP response to GraphQL result."""
        adapter = GraphQLToHttpAdapter()

        response = HttpResponse(
            status_code=200,
            body={"data": {"user": {"name": "John"}}},
            url="/graphql",
            method="POST",
        )

        result = adapter.adapt_response_to_result(response)

        assert result.is_success
        graphql_result = result.unwrap()
        assert graphql_result["user"]["name"] == "John"

    def test_adapt_http_response_with_graphql_errors(self) -> None:
        """Test adapting HTTP response with GraphQL errors."""
        adapter = GraphQLToHttpAdapter()

        response = HttpResponse(
            status_code=200,
            body={"errors": [{"message": "Field not found"}]},
            url="/graphql",
            method="POST",
        )

        result = adapter.adapt_response_to_result(response)

        assert result.is_failure
        assert "GraphQL errors" in result.error

    def test_adapt_http_error_response(self) -> None:
        """Test adapting HTTP error response."""
        adapter = GraphQLToHttpAdapter()

        response = HttpResponse(
            status_code=500,
            body={},
            url="/graphql",
            method="POST",
        )

        result = adapter.adapt_response_to_result(response)

        assert result.is_failure
        assert "failed with status 500" in result.error


class TestSchemaAdapter:
    """Test suite for SchemaAdapter."""

    def test_adapter_initialization(self) -> None:
        """Test adapter initialization."""
        adapter = SchemaAdapter()

        assert adapter is not None

    def test_openapi_toapi_conversion(self) -> None:
        """Test OpenAPI to API schema conversion."""
        adapter = SchemaAdapter()

        openapi_schema = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "getUsers",
                        "requestBody": {
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            }
                        },
                    }
                }
            },
        }

        result = adapter.openapi_toapi(openapi_schema)

        assert result.is_success
        api_schema = result.unwrap()
        assert api_schema["api"] == "3.0.0"
        assert "channels" in api_schema

    def test_openapi_to_graphql_schema_conversion(self) -> None:
        """Test OpenAPI to GraphQL schema conversion."""
        adapter = SchemaAdapter()

        openapi_schema = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                        },
                    }
                }
            },
            "paths": {
                "/users": {
                    "get": {"operationId": "getUsers"},
                    "post": {"operationId": "createUser"},
                }
            },
        }

        result = adapter.openapi_to_graphql_schema(openapi_schema)

        assert result.is_success
        graphql_sdl = result.unwrap()
        assert "type User" in graphql_sdl
        assert "type Query" in graphql_sdl
        assert "type Mutation" in graphql_sdl


class TestLegacyApiAdapter:
    """Test suite for LegacyApiAdapter."""

    def test_adapter_initialization(self) -> None:
        """Test adapter initialization."""
        adapter = LegacyApiAdapter(base_url="https://legacy.api.com")

        assert adapter is not None
        assert adapter._base_url == "https://legacy.api.com"

    def test_adapt_modern_request_to_legacy(self) -> None:
        """Test adapting modern request to legacy format."""
        adapter = LegacyApiAdapter(base_url="https://legacy.api.com")

        modern_request = HttpRequest(
            method="POST",  # Changed to POST since we're sending body
            url="/users",
            headers={"Authorization": "Bearer token123"},
            body={"userName": "john"},
        )

        result = adapter.adapt_request(modern_request)

        assert result.is_success
        legacy_request = result.unwrap()
        assert str(legacy_request.url).startswith("https://legacy.api.com")
        assert "X-API-Key" in legacy_request.headers

    def test_adapt_legacy_response_to_modern(self) -> None:
        """Test adapting legacy response to modern format."""
        adapter = LegacyApiAdapter(base_url="https://legacy.api.com")

        # Use a valid status code (200) but with legacy body format
        legacy_response = HttpResponse(
            status_code=200,
            body={"user_name": "john"},  # Legacy snake_case
            url="/users",
            method="GET",
        )

        result = adapter.adapt_response(legacy_response)

        assert result.is_success
        modern_response = result.unwrap()
        assert modern_response.status_code == 200
        assert "userName" in modern_response.body  # Converted to camelCase

    def test_camel_to_snake_conversion(self) -> None:
        """Test camelCase to snake_case conversion."""
        adapter = LegacyApiAdapter(base_url="https://legacy.api.com")

        result = adapter._camel_to_snake("userName")

        assert result == "user_name"

    def test_snake_to_camel_conversion(self) -> None:
        """Test snake_case to camelCase conversion."""
        adapter = LegacyApiAdapter(base_url="https://legacy.api.com")

        result = adapter._snake_to_camel("user_name")

        assert result == "userName"

    def test_status_code_mapping(self) -> None:
        """Test legacy status code mapping."""
        adapter = LegacyApiAdapter(base_url="https://legacy.api.com")

        assert adapter._adapt_status_code(1) == 200  # Success
        assert adapter._adapt_status_code(2) == 400  # Validation error
        assert adapter._adapt_status_code(3) == 401  # Auth error
        assert adapter._adapt_status_code(4) == 404  # Not found
        assert adapter._adapt_status_code(5) == 500  # Server error
        assert adapter._adapt_status_code(999) == 999  # Unknown code preserved

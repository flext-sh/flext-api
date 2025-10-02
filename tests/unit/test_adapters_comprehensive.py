"""Comprehensive tests for flext-api adapters with real functionality.

Tests all adapter classes with real data transformations:
- HttpToWebSocketAdapter
- GraphQLToHttpAdapter
- SchemaAdapter
- LegacyApiAdapter

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


class TestHttpToWebSocketAdapter:
    """Comprehensive tests for HTTP to WebSocket adapter."""

    def test_adapter_initialization(self) -> None:
        """Test adapter initialization."""
        adapter = HttpToWebSocketAdapter()

        assert adapter is not None
        assert adapter._logger is not None

    def test_adapt_http_request_to_websocket_message(self) -> None:
        """Test adapting HTTP request to WebSocket message."""
        adapter = HttpToWebSocketAdapter()

        # Create real HTTP request - POST can have body
        request = FlextApiModels.HttpRequest(
            method="POST",
            url="/api/users",
            headers={
                "Authorization": "Bearer token123",
                "Content-Type": "application/json",
            },
            body={"filter": "active"},
        )

        # Adapt to WebSocket message
        result = adapter.adapt_request(request)

        assert result.is_success
        message = result.unwrap()

        # Verify message structure
        assert message["type"] == "request"
        assert message["method"] == "POST"
        assert message["url"] == "/api/users"
        assert "Authorization" in message["headers"]
        assert message["headers"]["Authorization"] == "Bearer token123"
        assert message["body"]["filter"] == "active"

    def test_adapt_http_post_request(self) -> None:
        """Test adapting HTTP POST request with body."""
        adapter = HttpToWebSocketAdapter()

        request = FlextApiModels.HttpRequest(
            method="POST",
            url="/api/data",
            headers={"Content-Type": "application/json"},
            body={"name": "test", "value": 123},
        )

        result = adapter.adapt_request(request)

        assert result.is_success
        message = result.unwrap()
        assert message["method"] == "POST"
        assert message["body"]["name"] == "test"
        assert message["body"]["value"] == 123

    def test_adapt_websocket_message_to_http_response(self) -> None:
        """Test adapting WebSocket message to HTTP response."""
        adapter = HttpToWebSocketAdapter()

        # Create WebSocket message
        ws_message = {
            "status": 200,
            "body": {"result": "success", "data": {"id": 1, "name": "test"}},
            "headers": {"Content-Type": "application/json"},
            "url": "/api/users",
            "method": "GET",
        }

        # Adapt to HTTP response
        result = adapter.adapt_response(ws_message)

        assert result.is_success
        response = result.unwrap()

        # Verify response structure
        assert response.status_code == 200
        assert response.body["result"] == "success"
        assert response.body["data"]["id"] == 1
        assert response.headers["Content-Type"] == "application/json"
        assert response.url == "/api/users"
        assert response.method == "GET"

    def test_adapt_websocket_message_with_error_status(self) -> None:
        """Test adapting WebSocket message with error status."""
        adapter = HttpToWebSocketAdapter()

        ws_message = {
            "status": 404,
            "body": {"error": "Not found"},
            "headers": {},
            "url": "/api/missing",
            "method": "GET",
        }

        result = adapter.adapt_response(ws_message)

        assert result.is_success
        response = result.unwrap()
        assert response.status_code == 404
        assert response.body["error"] == "Not found"

    def test_adapt_request_with_empty_headers(self) -> None:
        """Test adapting request with no headers."""
        adapter = HttpToWebSocketAdapter()

        # GET request with empty dict for headers (not None)
        request = FlextApiModels.HttpRequest(
            method="GET",
            url="/api/test",
            headers={},
        )

        result = adapter.adapt_request(request)

        assert result.is_success
        message = result.unwrap()
        assert message["headers"] == {}
        assert message.get("body") is None or message["body"] == {}


class TestGraphQLToHttpAdapter:
    """Comprehensive tests for GraphQL to HTTP adapter."""

    def test_adapter_initialization(self) -> None:
        """Test adapter initialization with default endpoint."""
        adapter = GraphQLToHttpAdapter()

        assert adapter is not None
        assert adapter._endpoint == "/graphql"

    def test_adapter_initialization_custom_endpoint(self) -> None:
        """Test adapter initialization with custom endpoint."""
        adapter = GraphQLToHttpAdapter(endpoint="/api/graphql")

        assert adapter._endpoint == "/api/graphql"

    def test_adapt_graphql_query_to_http_request(self) -> None:
        """Test adapting GraphQL query to HTTP request."""
        adapter = GraphQLToHttpAdapter()

        query = """
        query GetUser($id: ID!) {
            user(id: $id) {
                name
                email
            }
        }
        """
        variables = {"id": "123"}

        result = adapter.adapt_query_to_request(query, variables)

        assert result.is_success
        request = result.unwrap()

        # Verify request structure
        assert request.method == "POST"
        assert request.url == "/graphql"
        assert request.body["query"] == query
        assert request.body["variables"] == variables
        assert request.headers["Content-Type"] == "application/json"
        assert request.headers["Accept"] == "application/json"

    def test_adapt_graphql_query_without_variables(self) -> None:
        """Test adapting GraphQL query without variables."""
        adapter = GraphQLToHttpAdapter()

        query = "{ users { name email } }"

        result = adapter.adapt_query_to_request(query)

        assert result.is_success
        request = result.unwrap()
        assert request.body["query"] == query
        assert request.body["variables"] == {}

    def test_adapt_http_response_to_graphql_result(self) -> None:
        """Test adapting HTTP response to GraphQL result."""
        adapter = GraphQLToHttpAdapter()

        # Create HTTP response with GraphQL data
        response = FlextApiModels.HttpResponse(
            status_code=200,
            headers={"Content-Type": "application/json"},
            body={"data": {"user": {"name": "John Doe", "email": "john@example.com"}}},
            url="/graphql",
            method="POST",
        )

        result = adapter.adapt_response_to_result(response)

        assert result.is_success
        graphql_result = result.unwrap()

        # Verify result structure
        assert "user" in graphql_result
        assert graphql_result["user"]["name"] == "John Doe"
        assert graphql_result["user"]["email"] == "john@example.com"

    def test_adapt_http_response_with_graphql_errors(self) -> None:
        """Test adapting HTTP response with GraphQL errors."""
        adapter = GraphQLToHttpAdapter()

        response = FlextApiModels.HttpResponse(
            status_code=200,
            headers={"Content-Type": "application/json"},
            body={
                "errors": [
                    {"message": "User not found"},
                    {"message": "Invalid permissions"},
                ]
            },
            url="/graphql",
            method="POST",
        )

        result = adapter.adapt_response_to_result(response)

        assert result.is_failure
        assert result.error is not None and "User not found" in result.error
        assert result.error is not None and "Invalid permissions" in result.error

    def test_adapt_http_response_non_200_status(self) -> None:
        """Test adapting HTTP response with non-200 status."""
        adapter = GraphQLToHttpAdapter()

        response = FlextApiModels.HttpResponse(
            status_code=500,
            headers={},
            body={},
            url="/graphql",
            method="POST",
        )

        result = adapter.adapt_response_to_result(response)

        assert result.is_failure
        assert result.error is not None and "500" in result.error


class TestSchemaAdapter:
    """Comprehensive tests for schema format adapter."""

    def test_adapter_initialization(self) -> None:
        """Test schema adapter initialization."""
        adapter = SchemaAdapter()

        assert adapter is not None
        assert adapter._logger is not None

    def test_convert_openapi_to_asyncapi(self) -> None:
        """Test converting OpenAPI schema to AsyncAPI schema."""
        adapter = SchemaAdapter()

        openapi_schema = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0",
                "description": "Test API",
            },
            "paths": {
                "/users": {
                    "get": {
                        "summary": "Get users",
                        "responses": {"200": {"description": "Success"}},
                    },
                    "post": {
                        "summary": "Create user",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"name": {"type": "string"}},
                                    }
                                }
                            }
                        },
                    },
                },
                "/users/{id}": {
                    "get": {
                        "summary": "Get user by ID",
                        "responses": {"200": {"description": "Success"}},
                    }
                },
            },
        }

        result = adapter.openapi_toapi(openapi_schema)

        assert result.is_success
        asyncapi_schema = result.unwrap()

        # Verify AsyncAPI structure
        assert asyncapi_schema["api"] == "3.0.0"
        assert asyncapi_schema["info"]["title"] == "Test API"
        assert "channels" in asyncapi_schema

        # Verify channels conversion
        assert "users" in asyncapi_schema["channels"]
        assert asyncapi_schema["channels"]["users"]["address"] == "/users"

    def test_convert_openapi_to_graphql_schema(self) -> None:
        """Test converting OpenAPI to GraphQL schema SDL."""
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
                            "email": {"type": "string"},
                            "active": {"type": "boolean"},
                        },
                    },
                    "Product": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                            "price": {"type": "number"},
                        },
                    },
                }
            },
            "paths": {
                "/users": {"get": {"operationId": "getUsers"}},
                "/users/{id}": {"post": {"operationId": "updateUser"}},
            },
        }

        result = adapter.openapi_to_graphql_schema(openapi_schema)

        assert result.is_success
        graphql_sdl = result.unwrap()

        # Verify GraphQL schema structure
        assert "type User" in graphql_sdl
        assert "type Product" in graphql_sdl
        assert "id: Int" in graphql_sdl
        assert "name: String" in graphql_sdl
        assert "price: Float" in graphql_sdl
        assert "active: Boolean" in graphql_sdl
        assert "type Query" in graphql_sdl
        assert "getUsers:" in graphql_sdl
        assert "type Mutation" in graphql_sdl
        assert "updateUser:" in graphql_sdl

    def test_openapi_type_to_graphql_mapping(self) -> None:
        """Test OpenAPI type to GraphQL type mapping."""
        adapter = SchemaAdapter()

        # Test all type mappings
        assert adapter._map_openapi_type_to_graphql("string") == "String"
        assert adapter._map_openapi_type_to_graphql("integer") == "Int"
        assert adapter._map_openapi_type_to_graphql("number") == "Float"
        assert adapter._map_openapi_type_to_graphql("boolean") == "Boolean"
        assert adapter._map_openapi_type_to_graphql("array") == "[String]"
        assert adapter._map_openapi_type_to_graphql("object") == "JSON"
        assert adapter._map_openapi_type_to_graphql("unknown") == "String"  # Default


class TestLegacyApiAdapter:
    """Comprehensive tests for legacy API adapter."""

    def test_adapter_initialization(self) -> None:
        """Test legacy API adapter initialization."""
        adapter = LegacyApiAdapter(base_url="https://legacy-api.example.com")

        assert adapter is not None
        assert adapter._base_url == "https://legacy-api.example.com"

    def test_adapt_modern_request_to_legacy(self) -> None:
        """Test adapting modern request to legacy API format."""
        adapter = LegacyApiAdapter(base_url="https://legacy.example.com")

        modern_request = FlextApiModels.HttpRequest(
            method="POST",
            url="/api/v2/users",
            headers={
                "Authorization": "Bearer token123",
                "Content-Type": "application/json",
            },
            body={"userName": "john", "userEmail": "john@example.com"},
        )

        result = adapter.adapt_request(modern_request)

        assert result.is_success
        legacy_request = result.unwrap()

        # Verify legacy request structure
        assert legacy_request.method == "POST"
        assert legacy_request.url == "https://legacy.example.com/api/v2/users"
        assert "X-API-Key" in legacy_request.headers  # Authorization -> X-API-Key
        assert legacy_request.body["user_name"] == "john"  # camelCase -> snake_case
        assert legacy_request.body["user_email"] == "john@example.com"

    def test_adapt_legacy_response_to_modern(self) -> None:
        """Test adapting legacy response to modern API format."""
        adapter = LegacyApiAdapter(base_url="https://legacy.example.com")

        # Create legacy response with actual legacy status code
        legacy_response = FlextApiModels.HttpResponse(
            status_code=200,  # Using standard HTTP status
            headers={"Content-Type": "application/json"},
            body={
                "user_id": "123",
                "user_name": "john",
                "user_email": "john@example.com",
            },
            url="https://legacy.example.com/api/users",
            method="GET",
        )

        result = adapter.adapt_response(legacy_response)

        assert result.is_success
        modern_response = result.unwrap()

        # Verify modern response structure
        assert modern_response.status_code == 200
        # Verify payload was normalized (snake_case -> camelCase)
        assert modern_response.body["userId"] == "123"
        assert modern_response.body["userName"] == "john"
        assert modern_response.body["userEmail"] == "john@example.com"

    def test_legacy_status_code_mapping(self) -> None:
        """Test legacy status code to modern HTTP status mapping."""
        adapter = LegacyApiAdapter(base_url="https://legacy.example.com")

        # Test various legacy status codes
        test_cases = [
            (1, 200),  # Success
            (2, 400),  # Validation error
            (3, 401),  # Auth error
            (4, 404),  # Not found
            (5, 500),  # Server error
            (999, 999),  # Unknown code stays unchanged
        ]

        for legacy_code, expected_code in test_cases:
            assert adapter._adapt_status_code(legacy_code) == expected_code

    def test_camel_to_snake_case_conversion(self) -> None:
        """Test camelCase to snake_case conversion."""
        adapter = LegacyApiAdapter(base_url="https://legacy.example.com")

        assert adapter._camel_to_snake("userName") == "user_name"
        assert adapter._camel_to_snake("userEmailAddress") == "user_email_address"
        assert adapter._camel_to_snake("id") == "id"
        assert adapter._camel_to_snake("HTTPResponse") == "h_t_t_p_response"

    def test_snake_to_camel_case_conversion(self) -> None:
        """Test snake_case to camelCase conversion."""
        adapter = LegacyApiAdapter(base_url="https://legacy.example.com")

        assert adapter._snake_to_camel("user_name") == "userName"
        assert adapter._snake_to_camel("user_email_address") == "userEmailAddress"
        assert adapter._snake_to_camel("id") == "id"
        assert adapter._snake_to_camel("api_key") == "apiKey"

    def test_adapt_headers_authorization_transformation(self) -> None:
        """Test header adaptation with authorization transformation."""
        adapter = LegacyApiAdapter(base_url="https://legacy.example.com")

        headers = {
            "Authorization": "Bearer token123",
            "Content-Type": "application/json",
            "User-Agent": "TestClient",
        }

        adapted = adapter._adapt_headers(headers)

        # Authorization should be moved to X-API-Key
        assert "Authorization" not in adapted
        assert "X-API-Key" in adapted
        assert adapted["X-API-Key"] == "Bearer token123"
        # Other headers preserved
        assert adapted["Content-Type"] == "application/json"
        assert adapted["User-Agent"] == "TestClient"

    def test_adapt_payload_with_nested_structure(self) -> None:
        """Test payload adaptation with nested structure."""
        adapter = LegacyApiAdapter(base_url="https://legacy.example.com")

        payload = {
            "userName": "john",
            "userProfile": "admin",
            "userSettings": {"emailNotifications": True, "smsAlerts": False},
        }

        adapted = adapter._adapt_payload(payload)

        # Top-level keys converted
        assert "user_name" in adapted
        assert "user_profile" in adapted
        # Note: This implementation only converts top-level keys
        # Nested conversion would require recursive implementation

    def test_normalize_payload_with_nested_structure(self) -> None:
        """Test payload normalization with nested structure."""
        adapter = LegacyApiAdapter(base_url="https://legacy.example.com")

        payload = {
            "user_id": "123",
            "user_name": "john",
            "user_settings": {"email_enabled": True, "sms_enabled": False},
        }

        normalized = adapter._normalize_payload(payload)

        # Top-level keys converted
        assert "userId" in normalized
        assert "userName" in normalized
        # Note: This implementation only converts top-level keys

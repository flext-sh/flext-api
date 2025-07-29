#!/usr/bin/env python3
"""Tests for FlextApi REST Helpers - Comprehensive validation of REST API functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Comprehensive tests for REST API helpers that provide massive code reduction
for REST API development. Tests all components without mocks.
"""

import asyncio
from typing import Any

import pytest

from flext_api.helpers.flext_api_rest import (
    FlextApiEndpointRegistry,
    FlextApiRequestParser,
    FlextApiResponseBuilder,
    FlextApiRestPlatform,
    FlextApiRestValidator,
    flext_api_create_endpoint_registry,
    flext_api_create_request_parser,
    flext_api_create_response_builder,
    flext_api_create_rest_platform,
    flext_api_create_validator,
)


class TestFlextApiRequestParser:
    """Test request parser functionality."""

    def test_create_request_parser(self) -> None:
        """Test request parser creation."""
        parser = flext_api_create_request_parser()
        assert isinstance(parser, FlextApiRequestParser)

    def test_parse_simple_query_params(self) -> None:
        """Test parsing simple query parameters."""
        query_string = "name=John&age=30&active=true"

        result = FlextApiRequestParser.flext_api_parse_query_params(query_string)

        assert result["name"] == "John"
        assert result["age"] == 30  # Should be converted to int
        assert result["active"] is True  # Should be converted to bool

    def test_parse_complex_query_params(self) -> None:
        """Test parsing complex query parameters with type conversion."""
        query_string = "?score=95.5&items=null&status=false&description=hello world"

        result = FlextApiRequestParser.flext_api_parse_query_params(query_string)

        assert result["score"] == 95.5  # Should be converted to float
        assert result["items"] is None  # Should be converted to None
        assert result["status"] is False  # Should be converted to bool
        assert result["description"] == "hello world"

    def test_parse_array_query_params(self) -> None:
        """Test parsing array query parameters."""
        query_string = "tags=python&tags=api&tags=rest"

        result = FlextApiRequestParser.flext_api_parse_query_params(query_string)

        assert result["tags"] == ["python", "api", "rest"]

    def test_parse_empty_query_string(self) -> None:
        """Test parsing empty query string."""
        result = FlextApiRequestParser.flext_api_parse_query_params("")
        assert result == {}

        result = FlextApiRequestParser.flext_api_parse_query_params("?")
        assert result == {}

    def test_parse_path_parameters(self) -> None:
        """Test parsing path parameters from URL template."""
        template = "/users/{user_id}/posts/{post_id}"
        actual_path = "/users/123/posts/456"

        result = FlextApiRequestParser.flext_api_parse_path_params(
            template,
            actual_path,
        )

        assert result["user_id"] == "123"
        assert result["post_id"] == "456"

    def test_parse_path_parameters_mismatch(self) -> None:
        """Test parsing path parameters with mismatched template."""
        template = "/users/{user_id}/posts/{post_id}"
        actual_path = "/users/123"  # Missing post_id part

        result = FlextApiRequestParser.flext_api_parse_path_params(
            template,
            actual_path,
        )

        assert result == {}  # Should return empty dict for mismatch

    def test_parse_json_body_valid(self) -> None:
        """Test parsing valid JSON body."""
        body = '{"name": "John", "age": 30, "email": "john@example.com"}'

        result = FlextApiRequestParser.flext_api_parse_json_body(body)

        assert result.is_success
        data = result.data
        assert data["name"] == "John"
        assert data["age"] == 30
        assert data["email"] == "john@example.com"

    def test_parse_json_body_invalid(self) -> None:
        """Test parsing invalid JSON body."""
        body = '{"name": "John", "age": 30,}'  # Trailing comma - invalid JSON

        result = FlextApiRequestParser.flext_api_parse_json_body(body)

        assert not result.is_success
        assert "Invalid JSON" in result.error

    def test_parse_json_body_empty(self) -> None:
        """Test parsing empty JSON body."""
        result = FlextApiRequestParser.flext_api_parse_json_body("")
        assert result.is_success
        assert result.data is None

        result = FlextApiRequestParser.flext_api_parse_json_body("   ")
        assert result.is_success
        assert result.data is None

    def test_create_complete_request(self) -> None:
        """Test creating complete request with all components."""
        parser = FlextApiRequestParser()

        result = parser.flext_api_create_request(
            method="POST",
            path="/api/v1/users/123",
            query_string="include=profile&format=json",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer token123",
            },
            body='{"name": "Updated Name"}',
            path_template="/api/v1/users/{user_id}",
            user_id="user123",
            correlation_id="req-456",
        )

        assert result.is_success
        request = result.data

        assert request["method"] == "POST"
        assert request["path"] == "/api/v1/users/123"
        assert request["query_params"]["include"] == "profile"
        assert request["query_params"]["format"] == "json"
        assert request["path_params"]["user_id"] == "123"
        assert request["headers"]["Content-Type"] == "application/json"
        assert request["body"]["name"] == "Updated Name"
        assert request["user_id"] == "user123"
        assert request["correlation_id"] == "req-456"


class TestFlextApiResponseBuilder:
    """Test response builder functionality."""

    def test_create_response_builder(self) -> None:
        """Test response builder creation."""
        builder = flext_api_create_response_builder()
        assert isinstance(builder, FlextApiResponseBuilder)

    def test_success_response(self) -> None:
        """Test creating success response."""
        data = {"id": 1, "name": "John Doe", "email": "john@example.com"}

        response = FlextApiResponseBuilder.flext_api_success_response(
            data,
            status_code=200,
            message="User created successfully",
        )

        assert response["status_code"] == 200
        assert response["success"] is True
        assert response["body"]["success"] is True
        assert response["body"]["message"] == "User created successfully"
        assert response["body"]["data"] == data
        assert response["errors"] == []
        assert "timestamp" in response

    def test_success_response_with_metadata(self) -> None:
        """Test creating success response with metadata."""
        data = [{"id": 1}, {"id": 2}]
        metadata = {"total_count": 2, "page": 1}
        headers = {"X-API-Version": "v1"}

        response = FlextApiResponseBuilder.flext_api_success_response(
            data,
            metadata=metadata,
            headers=headers,
        )

        assert response["body"]["metadata"] == metadata
        assert response["headers"]["X-API-Version"] == "v1"
        assert response["metadata"] == metadata

    def test_error_response(self) -> None:
        """Test creating error response."""
        response = FlextApiResponseBuilder.flext_api_error_response(
            error="User not found",
            status_code=404,
            error_code="USER_NOT_FOUND",
            details={"user_id": "123"},
        )

        assert response["status_code"] == 404
        assert response["success"] is False
        assert response["body"]["success"] is False
        assert response["body"]["error"] == "User not found"
        assert response["body"]["error_code"] == "USER_NOT_FOUND"
        assert response["body"]["details"]["user_id"] == "123"
        assert response["errors"] == ["User not found"]

    def test_paginated_response(self) -> None:
        """Test creating paginated response."""
        items = [{"id": 1}, {"id": 2}, {"id": 3}]

        response = FlextApiResponseBuilder.flext_api_paginated_response(
            items=items,
            page=1,
            page_size=10,
            total_items=25,
        )

        assert response["status_code"] == 200
        assert response["success"] is True

        pagination = response["body"]["data"]["pagination"]
        assert pagination["page"] == 1
        assert pagination["page_size"] == 10
        assert pagination["total_items"] == 25
        assert pagination["total_pages"] == 3
        assert pagination["has_next"] is True
        assert pagination["has_previous"] is False
        assert pagination["next_page"] == 2
        assert pagination["previous_page"] is None

        assert response["headers"]["X-Total-Count"] == "25"
        assert response["headers"]["X-Page"] == "1"

    def test_validation_error_response(self) -> None:
        """Test creating validation error response."""
        validation_errors = [
            "Name is required",
            "Email must be valid",
            "Age must be greater than 0",
        ]

        response = FlextApiResponseBuilder.flext_api_validation_error_response(
            validation_errors,
        )

        assert response["status_code"] == 422
        assert response["success"] is False
        assert response["body"]["error"] == "Validation failed"
        assert response["body"]["validation_errors"] == validation_errors
        assert response["errors"] == validation_errors
        assert response["metadata"]["error_type"] == "validation"


class TestFlextApiRestValidator:
    """Test REST validator functionality."""

    def test_create_validator(self) -> None:
        """Test validator creation."""
        validator = flext_api_create_validator()
        assert isinstance(validator, FlextApiRestValidator)

    def test_add_validation_rules(self) -> None:
        """Test adding validation rules."""
        validator = FlextApiRestValidator()

        validator.flext_api_add_rule(
            "name",
            "str",
            required=True,
            min_length=2,
            max_length=50,
        )
        validator.flext_api_add_rule(
            "age",
            "int",
            required=True,
            min_value=0,
            max_value=120,
        )
        validator.flext_api_add_rule(
            "email",
            "str",
            required=True,
            pattern=r"^[^@]+@[^@]+\.[^@]+$",
        )

        assert len(validator.rules) == 3

    def test_validate_successful(self) -> None:
        """Test successful validation."""
        validator = FlextApiRestValidator()

        validator.flext_api_add_rule("name", "str", required=True, min_length=2)
        validator.flext_api_add_rule("age", "int", required=True, min_value=18)

        data = {"name": "John Doe", "age": 25}

        result = validator.flext_api_validate(data)

        assert result.is_success
        assert result.data == data

    def test_validate_missing_required_field(self) -> None:
        """Test validation with missing required field."""
        validator = FlextApiRestValidator()

        validator.flext_api_add_rule("name", "str", required=True)
        validator.flext_api_add_rule("email", "str", required=True)

        data = {"name": "John"}  # Missing email

        result = validator.flext_api_validate(data)

        assert not result.is_success
        assert "email" in result.error
        assert "required" in result.error

    def test_validate_type_mismatch(self) -> None:
        """Test validation with type mismatch."""
        validator = FlextApiRestValidator()

        validator.flext_api_add_rule("age", "int", required=True)

        data = {"age": "not_a_number"}  # String instead of int

        result = validator.flext_api_validate(data)

        assert not result.is_success
        assert "type" in result.error

    def test_validate_string_constraints(self) -> None:
        """Test validation with string constraints."""
        validator = FlextApiRestValidator()

        validator.flext_api_add_rule("name", "str", min_length=5, max_length=10)

        # Test too short
        result = validator.flext_api_validate({"name": "Joe"})
        assert not result.is_success

        # Test too long
        result = validator.flext_api_validate({"name": "Very Long Name"})
        assert not result.is_success

        # Test valid length
        result = validator.flext_api_validate({"name": "John Doe"})
        assert result.is_success

    def test_validate_numeric_constraints(self) -> None:
        """Test validation with numeric constraints."""
        validator = FlextApiRestValidator()

        validator.flext_api_add_rule("score", "float", min_value=0.0, max_value=100.0)

        # Test too low
        result = validator.flext_api_validate({"score": -5.0})
        assert not result.is_success

        # Test too high
        result = validator.flext_api_validate({"score": 150.0})
        assert not result.is_success

        # Test valid value
        result = validator.flext_api_validate({"score": 85.5})
        assert result.is_success

    def test_validate_enum_constraint(self) -> None:
        """Test validation with enum constraint."""
        validator = FlextApiRestValidator()

        validator.flext_api_add_rule(
            "status",
            "str",
            enum_values=["active", "inactive", "pending"],
        )

        # Test invalid enum value
        result = validator.flext_api_validate({"status": "unknown"})
        assert not result.is_success

        # Test valid enum value
        result = validator.flext_api_validate({"status": "active"})
        assert result.is_success

    def test_validate_pattern_constraint(self) -> None:
        """Test validation with pattern constraint."""
        validator = FlextApiRestValidator()

        validator.flext_api_add_rule("phone", "str", pattern=r"^\+?1?\d{9,15}$")

        # Test invalid pattern
        result = validator.flext_api_validate({"phone": "invalid-phone"})
        assert not result.is_success

        # Test valid pattern
        result = validator.flext_api_validate({"phone": "+1234567890"})
        assert result.is_success


class TestFlextApiEndpointRegistry:
    """Test endpoint registry functionality."""

    def test_create_endpoint_registry(self) -> None:
        """Test endpoint registry creation."""
        registry = flext_api_create_endpoint_registry()
        assert isinstance(registry, FlextApiEndpointRegistry)

    def test_register_endpoint(self) -> None:
        """Test endpoint registration."""
        registry = FlextApiEndpointRegistry()

        def test_handler(request_id: str, name: str = "default") -> dict:
            return {"request_id": request_id, "name": name}

        registry.flext_api_register_endpoint(
            path="/test/{id}",
            method="GET",
            handler=test_handler,
            description="Test endpoint",
            tags=["test"],
        )

        assert len(registry.endpoints) == 1
        endpoint = registry.endpoints[0]
        assert endpoint["path"] == "/test/{id}"
        assert endpoint["method"] == "GET"
        assert endpoint["description"] == "Test endpoint"
        assert endpoint["tags"] == ["test"]

    def test_get_endpoint(self) -> None:
        """Test getting registered endpoint."""
        registry = FlextApiEndpointRegistry()

        def handler() -> str:
            return "response"

        registry.flext_api_register_endpoint("/users", "POST", handler)

        endpoint = registry.flext_api_get_endpoint("/users", "POST")
        assert endpoint is not None
        assert endpoint["path"] == "/users"
        assert endpoint["method"] == "POST"

        # Test non-existent endpoint
        endpoint = registry.flext_api_get_endpoint("/users", "DELETE")
        assert endpoint is None

    def test_get_handler(self) -> None:
        """Test getting endpoint handler."""
        registry = FlextApiEndpointRegistry()

        def test_handler() -> str:
            return "test response"

        registry.flext_api_register_endpoint("/test", "GET", test_handler)

        handler = registry.flext_api_get_handler("/test", "GET")
        assert handler is not None
        assert handler() == "test response"

    def test_list_endpoints(self) -> None:
        """Test listing all endpoints."""
        registry = FlextApiEndpointRegistry()

        def handler1() -> str:
            return "1"

        def handler2() -> str:
            return "2"

        registry.flext_api_register_endpoint("/endpoint1", "GET", handler1)
        registry.flext_api_register_endpoint("/endpoint2", "POST", handler2)

        endpoints = registry.flext_api_list_endpoints()
        assert len(endpoints) == 2

    def test_generate_openapi_spec(self) -> None:
        """Test OpenAPI specification generation."""
        registry = FlextApiEndpointRegistry()

        def get_users(page: int = 1, limit: int = 10) -> list:
            return []

        def create_user(name: str, email: str) -> dict:
            return {}

        registry.flext_api_register_endpoint("/users", "GET", get_users, "Get users")
        registry.flext_api_register_endpoint(
            "/users",
            "POST",
            create_user,
            "Create user",
        )

        spec = registry.flext_api_generate_openapi_spec("Test API", "1.0.0")

        assert spec["openapi"] == "3.0.0"
        assert spec["info"]["title"] == "Test API"
        assert spec["info"]["version"] == "1.0.0"
        assert "/users" in spec["paths"]
        assert "get" in spec["paths"]["/users"]
        assert "post" in spec["paths"]["/users"]


class TestFlextApiRestPlatform:
    """Test complete REST platform functionality."""

    def test_create_rest_platform(self) -> None:
        """Test REST platform creation."""
        platform = flext_api_create_rest_platform()
        assert isinstance(platform, FlextApiRestPlatform)

    def test_add_endpoint_to_platform(self) -> None:
        """Test adding endpoint to platform."""
        platform = FlextApiRestPlatform()

        def get_health() -> dict:
            return {"status": "healthy"}

        platform.flext_api_add_endpoint("/health", "GET", get_health, "Health check")

        endpoints = platform.endpoint_registry.flext_api_list_endpoints()
        assert len(endpoints) == 1
        assert endpoints[0]["path"] == "/health"

    def test_http_method_decorators(self) -> None:
        """Test HTTP method decorators."""
        platform = FlextApiRestPlatform()

        @platform.flext_api_get("/items", "Get items")
        def get_items() -> list:
            return [{"id": 1}, {"id": 2}]

        @platform.flext_api_post("/items", "Create item")
        def create_item() -> dict:
            return {"id": 3}

        @platform.flext_api_put("/items/{id}", "Update item")
        def update_item() -> dict:
            return {"id": 1, "updated": True}

        @platform.flext_api_delete("/items/{id}", "Delete item")
        def delete_item() -> dict:
            return {"deleted": True}

        endpoints = platform.endpoint_registry.flext_api_list_endpoints()
        assert len(endpoints) == 4

        methods = [ep["method"] for ep in endpoints]
        assert "GET" in methods
        assert "POST" in methods
        assert "PUT" in methods
        assert "DELETE" in methods

    @pytest.mark.asyncio
    async def test_handle_request_success(self) -> None:
        """Test successful request handling."""
        platform = FlextApiRestPlatform()

        def test_endpoint(request: dict[str, Any]) -> dict[str, Any]:
            return {"message": "success", "data": request["body"]}

        platform.flext_api_add_endpoint("/test", "POST", test_endpoint)

        response = await platform.flext_api_handle_request(
            method="POST",
            path="/test",
            body='{"input": "test data"}',
            headers={"Content-Type": "application/json"},
        )

        assert response["status_code"] == 200
        assert response["success"] is True

    @pytest.mark.asyncio
    async def test_handle_request_not_found(self) -> None:
        """Test request handling for non-existent endpoint."""
        platform = FlextApiRestPlatform()

        response = await platform.flext_api_handle_request(
            method="GET",
            path="/nonexistent",
        )

        assert response["status_code"] == 404
        assert response["success"] is False
        assert "not found" in response["body"]["error"].lower()

    @pytest.mark.asyncio
    async def test_handle_request_invalid_json(self) -> None:
        """Test request handling with invalid JSON."""
        platform = FlextApiRestPlatform()

        def test_endpoint(request: dict[str, Any]) -> dict[str, Any]:
            return {"data": request["body"]}

        platform.flext_api_add_endpoint("/test", "POST", test_endpoint)

        response = await platform.flext_api_handle_request(
            method="POST",
            path="/test",
            body='{"invalid": json,}',  # Invalid JSON
        )

        assert response["status_code"] == 400
        assert response["success"] is False

    @pytest.mark.asyncio
    async def test_handle_async_endpoint(self) -> None:
        """Test handling async endpoint functions."""
        platform = FlextApiRestPlatform()

        async def async_endpoint(request: dict[str, Any]) -> dict[str, Any]:
            await asyncio.sleep(0.01)  # Simulate async work
            return {"async": True, "data": request["query_params"]}

        platform.flext_api_add_endpoint("/async", "GET", async_endpoint)

        response = await platform.flext_api_handle_request(
            method="GET",
            path="/async",
            query_string="param1=value1&param2=value2",
        )

        assert response["status_code"] == 200
        assert response["success"] is True

    def test_generate_platform_docs(self) -> None:
        """Test documentation generation for platform."""
        platform = FlextApiRestPlatform()

        def get_users() -> list:
            return []

        def create_user() -> dict:
            return {}

        platform.flext_api_add_endpoint("/users", "GET", get_users, "List users")
        platform.flext_api_add_endpoint("/users", "POST", create_user, "Create user")

        docs = platform.flext_api_generate_docs()

        assert "openapi" in docs
        assert "paths" in docs
        assert "/users" in docs["paths"]


class TestRestApiIntegration:
    """Test integration between REST API components."""

    @pytest.mark.asyncio
    async def test_complete_rest_workflow(self) -> None:
        """Test complete REST API workflow."""
        # Create platform
        platform = FlextApiRestPlatform()

        # Define endpoint with validation
        @platform.flext_api_post("/users", "Create user", ["users"])
        def create_user(request: dict[str, Any]) -> dict[str, Any]:
            # Validate request
            validator = FlextApiRestValidator()
            validator.flext_api_add_rule("name", "str", required=True, min_length=2)
            validator.flext_api_add_rule("email", "str", required=True)
            validator.flext_api_add_rule("age", "int", required=True, min_value=18)

            validation_result = validator.flext_api_validate(request["body"])
            if not validation_result.is_success:
                return FlextApiResponseBuilder.flext_api_validation_error_response(
                    [validation_result.error],
                )

            # Simulate user creation
            user = {
                "id": 123,
                "name": request["body"]["name"],
                "email": request["body"]["email"],
                "age": request["body"]["age"],
            }

            return FlextApiResponseBuilder.flext_api_success_response(
                user,
                status_code=201,
                message="User created successfully",
            )

        # Test valid request
        response = await platform.flext_api_handle_request(
            method="POST",
            path="/users",
            body='{"name": "John Doe", "email": "john@example.com", "age": 25}',
            headers={"Content-Type": "application/json"},
        )

        assert response["status_code"] == 201
        assert response["success"] is True

    def test_real_world_api_configuration(self) -> None:
        """Test realistic API configuration scenarios."""
        platform = FlextApiRestPlatform()

        # Define multiple endpoints
        endpoints = [
            ("/health", "GET", lambda req: {"status": "healthy"}, "Health check"),
            ("/users", "GET", lambda req: {"users": []}, "List users"),
            ("/users", "POST", lambda req: {"id": 1}, "Create user"),
            (
                "/users/{id}",
                "GET",
                lambda req: {"id": req["path_params"]["id"]},
                "Get user",
            ),
            ("/users/{id}", "PUT", lambda req: {"updated": True}, "Update user"),
            ("/users/{id}", "DELETE", lambda req: {"deleted": True}, "Delete user"),
        ]

        for path, method, handler, description in endpoints:
            platform.flext_api_add_endpoint(path, method, handler, description)

        # Verify all endpoints are registered
        registered_endpoints = platform.endpoint_registry.flext_api_list_endpoints()
        assert len(registered_endpoints) == 6

        # Generate OpenAPI documentation
        docs = platform.flext_api_generate_docs()
        assert len(docs["paths"]) == 3  # /health, /users, /users/{id}

    def test_request_response_cycle(self) -> None:
        """Test complete request-response cycle."""
        # Test request parsing
        parser = FlextApiRequestParser()
        request_result = parser.flext_api_create_request(
            method="POST",
            path="/api/users",
            query_string="include=profile",
            body='{"name": "Test User"}',
            headers={"Authorization": "Bearer token123"},
        )
        assert request_result.is_success

        # Test response building
        builder = FlextApiResponseBuilder()
        success_response = builder.flext_api_success_response(
            {"id": 1, "name": "Test User"},
            message="User created",
        )
        assert success_response["success"] is True

        error_response = builder.flext_api_error_response(
            "Validation failed",
            400,
        )
        assert error_response["success"] is False

        # Test validation
        validator = FlextApiRestValidator()
        validator.flext_api_add_rule("name", "str", required=True)

        valid_result = validator.flext_api_validate({"name": "Valid Name"})
        assert valid_result.is_success

        invalid_result = validator.flext_api_validate({})  # Missing required name
        assert not invalid_result.is_success


if __name__ == "__main__":
    # Run basic functionality tests

    # Test request parser
    parser = flext_api_create_request_parser()

    # Test query parameter parsing
    params = parser.flext_api_parse_query_params("name=John&age=30&active=true")

    # Test response builder
    builder = flext_api_create_response_builder()

    # Test success response
    response = builder.flext_api_success_response({"id": 1}, message="Success")

    # Test validator
    validator = flext_api_create_validator()
    validator.flext_api_add_rule("name", "str", required=True)

    # Test endpoint registry
    registry = flext_api_create_endpoint_registry()
    registry.flext_api_register_endpoint("/test", "GET", lambda: "test")

    # Test complete platform
    platform = flext_api_create_rest_platform()

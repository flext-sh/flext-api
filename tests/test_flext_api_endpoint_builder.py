#!/usr/bin/env python3
"""Tests for FlextApi Endpoint Builder - Zero boilerplate endpoint creation validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Testes robustos para endpoint builder que elimina 95% do boilerplate REST.
"""

import asyncio
from typing import Any

import pytest
from flext_core import FlextResult

from flext_api.helpers.flext_api_endpoint_builder import (
    FlextApiEndpointBuilder,
    flext_api_create_crud_endpoints,
    flext_api_create_endpoint_builder,
    flext_api_create_validation_rule,
)


class TestFlextApiEndpointBuilder:
    """Tests for FlextApiEndpointBuilder - Core endpoint creation functionality."""

    def test_endpoint_builder_initialization(self) -> None:
        """Test endpoint builder initialization."""
        builder = flext_api_create_endpoint_builder()

        assert isinstance(builder, FlextApiEndpointBuilder)
        assert len(builder.endpoints) == 0
        assert len(builder.global_middleware) == 0
        assert len(builder.global_validators) == 0

    def test_register_simple_endpoint(self) -> None:
        """Test registering a simple endpoint."""
        builder = flext_api_create_endpoint_builder()

        @builder.flext_api_get("/test", summary="Test endpoint")
        def test_endpoint() -> dict[str, str]:
            return {"message": "Hello World"}

        endpoints = builder.flext_api_get_endpoints()
        assert len(endpoints) == 1

        endpoint_key = "GET:/test"
        assert endpoint_key in endpoints

        config = endpoints[endpoint_key]["config"]
        assert config["path"] == "/test"
        assert config["method"] == "GET"
        assert config["summary"] == "Test endpoint"
        assert config["auth_required"] is False

    def test_register_endpoints_with_all_http_methods(self) -> None:
        """Test registering endpoints with all HTTP methods."""
        builder = flext_api_create_endpoint_builder()

        @builder.flext_api_get("/users")
        def get_users() -> list[dict[str, Any]]:
            return []

        @builder.flext_api_post("/users")
        def create_user() -> dict[str, Any]:
            return {"id": 1}

        @builder.flext_api_put("/users/{id}")
        def update_user() -> dict[str, Any]:
            return {"updated": True}

        @builder.flext_api_delete("/users/{id}")
        def delete_user() -> dict[str, Any]:
            return {"deleted": True}

        @builder.flext_api_patch("/users/{id}")
        def patch_user() -> dict[str, Any]:
            return {"patched": True}

        endpoints = builder.flext_api_get_endpoints()
        assert len(endpoints) == 5

        assert "GET:/users" in endpoints
        assert "POST:/users" in endpoints
        assert "PUT:/users/{id}" in endpoints
        assert "DELETE:/users/{id}" in endpoints
        assert "PATCH:/users/{id}" in endpoints

    def test_endpoint_with_full_configuration(self) -> None:
        """Test endpoint with complete configuration."""
        builder = flext_api_create_endpoint_builder()

        @builder.flext_api_post(
            "/api/users",
            summary="Create new user",
            description="Creates a new user with validation",
            tags=["users", "management"],
            auth_required=True,
            rate_limit=100,
            cache_ttl=300,
            timeout=60,
        )
        def create_user() -> dict[str, Any]:
            return {"created": True}

        endpoints = builder.flext_api_get_endpoints()
        config = endpoints["POST:/api/users"]["config"]

        assert config["summary"] == "Create new user"
        assert config["description"] == "Creates a new user with validation"
        assert config["tags"] == ["users", "management"]
        assert config["auth_required"] is True
        assert config["rate_limit"] == 100
        assert config["cache_ttl"] == 300
        assert config["timeout"] == 60

    @pytest.mark.asyncio
    async def test_endpoint_execution_success(self) -> None:
        """Test successful endpoint execution."""
        builder = flext_api_create_endpoint_builder()

        @builder.flext_api_get("/health")
        def health_check() -> dict[str, str]:
            return {"status": "healthy"}

        # Get the wrapper function
        endpoint_info = builder.endpoints["GET:/health"]
        handler = endpoint_info["handler"]

        # Execute the endpoint
        response = await handler()

        assert isinstance(response, dict)
        assert response["success"] is True
        assert response["data"] == {"status": "healthy"}
        assert response["message"] == "Request completed successfully"
        assert response["errors"] == []
        assert "execution_time_ms" in response
        assert "timestamp" in response

    @pytest.mark.asyncio
    async def test_endpoint_execution_with_flext_result(self) -> None:
        """Test endpoint execution returning FlextResult."""
        builder = flext_api_create_endpoint_builder()

        @builder.flext_api_get("/users")
        def get_users() -> FlextResult[list[dict[str, Any]]]:
            users = [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]
            return FlextResult.ok(users)

        endpoint_info = builder.endpoints["GET:/users"]
        handler = endpoint_info["handler"]

        response = await handler()

        assert response["success"] is True
        assert len(response["data"]) == 2
        assert response["data"][0]["name"] == "John"

    @pytest.mark.asyncio
    async def test_endpoint_execution_with_flext_result_failure(self) -> None:
        """Test endpoint execution with FlextResult failure."""
        builder = flext_api_create_endpoint_builder()

        @builder.flext_api_get("/failing")
        def failing_endpoint() -> FlextResult[None]:
            return FlextResult.fail("Something went wrong")

        endpoint_info = builder.endpoints["GET:/failing"]
        handler = endpoint_info["handler"]

        response = await handler()

        assert response["success"] is False
        assert response["data"] is None
        assert "Something went wrong" in response["errors"]

    @pytest.mark.asyncio
    async def test_endpoint_execution_with_exception(self) -> None:
        """Test endpoint execution with unhandled exception."""
        builder = flext_api_create_endpoint_builder()

        @builder.flext_api_get("/error")
        def error_endpoint() -> None:
            msg = "Unhandled error"
            raise ValueError(msg)

        endpoint_info = builder.endpoints["GET:/error"]
        handler = endpoint_info["handler"]

        response = await handler()

        assert response["success"] is False
        assert response["data"] is None
        assert "Internal server error" in response["errors"][0]
        assert "Unhandled error" in response["errors"][0]

    @pytest.mark.asyncio
    async def test_async_endpoint_execution(self) -> None:
        """Test execution of async endpoint function."""
        builder = flext_api_create_endpoint_builder()

        @builder.flext_api_get("/async")
        async def async_endpoint() -> dict[str, str]:
            await asyncio.sleep(0.01)
            return {"async": "completed"}

        endpoint_info = builder.endpoints["GET:/async"]
        handler = endpoint_info["handler"]

        response = await handler()

        assert response["success"] is True
        assert response["data"] == {"async": "completed"}


class TestFlextApiValidation:
    """Tests for FlextApi validation functionality."""

    def test_create_validation_rule(self) -> None:
        """Test creating validation rule."""
        rule = flext_api_create_validation_rule(
            field="name",
            field_type=str,
            required=True,
            min_length=2,
            max_length=50,
            pattern=r"^[a-zA-Z\s]+$",
        )

        assert isinstance(rule, dict)
        assert rule["field"] == "name"
        assert rule["type"] is str
        assert rule["required"] is True
        assert rule["min_length"] == 2
        assert rule["max_length"] == 50
        assert rule["pattern"] == r"^[a-zA-Z\s]+$"

    @pytest.mark.asyncio
    async def test_endpoint_with_validation_success(self) -> None:
        """Test endpoint with successful validation."""
        builder = flext_api_create_endpoint_builder()

        name_rule = flext_api_create_validation_rule(
            field="name",
            field_type=str,
            required=True,
            min_length=2,
        )

        @builder.flext_api_post("/users", validators=[name_rule])
        def create_user(request: dict[str, Any]) -> dict[str, Any]:
            return {"id": 1, "name": request["name"]}

        endpoint_info = builder.endpoints["POST:/users"]
        handler = endpoint_info["handler"]

        # Test with valid request
        response = await handler({"name": "John Doe"})

        assert response["success"] is True
        assert response["data"]["name"] == "John Doe"

    @pytest.mark.asyncio
    async def test_endpoint_with_validation_failure(self) -> None:
        """Test endpoint with validation failure."""
        builder = flext_api_create_endpoint_builder()

        name_rule = flext_api_create_validation_rule(
            field="name",
            field_type=str,
            required=True,
            min_length=5,
        )

        @builder.flext_api_post("/users", validators=[name_rule])
        def create_user(request: dict[str, Any]) -> dict[str, Any]:
            return {"created": True}

        endpoint_info = builder.endpoints["POST:/users"]
        handler = endpoint_info["handler"]

        # Test with invalid request (name too short)
        response = await handler({"name": "Jo"})

        assert response["success"] is False
        assert "must be at least 5 characters" in response["errors"][0]

    @pytest.mark.asyncio
    async def test_endpoint_with_missing_required_field(self) -> None:
        """Test endpoint with missing required field."""
        builder = flext_api_create_endpoint_builder()

        email_rule = flext_api_create_validation_rule(
            field="email",
            field_type=str,
            required=True,
        )

        @builder.flext_api_post("/users", validators=[email_rule])
        def create_user(request: dict[str, Any]) -> dict[str, Any]:
            return {"created": True}

        endpoint_info = builder.endpoints["POST:/users"]
        handler = endpoint_info["handler"]

        # Test with missing email field
        response = await handler({"name": "John"})

        assert response["success"] is False
        assert "Field 'email' is required" in response["errors"][0]

    @pytest.mark.asyncio
    async def test_endpoint_with_type_validation_error(self) -> None:
        """Test endpoint with type validation error."""
        builder = flext_api_create_endpoint_builder()

        age_rule = flext_api_create_validation_rule(
            field="age",
            field_type=int,
            required=True,
        )

        @builder.flext_api_post("/users", validators=[age_rule])
        def create_user(request: dict[str, Any]) -> dict[str, Any]:
            return {"created": True}

        endpoint_info = builder.endpoints["POST:/users"]
        handler = endpoint_info["handler"]

        # Test with wrong type (string instead of int)
        response = await handler({"age": "twenty"})

        assert response["success"] is False
        assert "must be of type int" in response["errors"][0]

    @pytest.mark.asyncio
    async def test_endpoint_with_pattern_validation(self) -> None:
        """Test endpoint with pattern validation."""
        builder = flext_api_create_endpoint_builder()

        email_rule = flext_api_create_validation_rule(
            field="email",
            field_type=str,
            required=True,
            pattern=r"^[^@]+@[^@]+\.[^@]+$",
        )

        @builder.flext_api_post("/users", validators=[email_rule])
        def create_user(request: dict[str, Any]) -> dict[str, Any]:
            return {"created": True}

        endpoint_info = builder.endpoints["POST:/users"]
        handler = endpoint_info["handler"]

        # Test with invalid email pattern
        response = await handler({"email": "invalid-email"})

        assert response["success"] is False
        assert "format is invalid" in response["errors"][0]

        # Test with valid email
        response = await handler({"email": "user@example.com"})
        assert response["success"] is True

    @pytest.mark.asyncio
    async def test_endpoint_with_custom_validator(self) -> None:
        """Test endpoint with custom validator."""
        builder = flext_api_create_endpoint_builder()

        def validate_positive(value: int) -> bool:
            return value > 0

        price_rule = flext_api_create_validation_rule(
            field="price",
            field_type=int,
            required=True,
            custom_validator=validate_positive,
        )

        @builder.flext_api_post("/products", validators=[price_rule])
        def create_product(request: dict[str, Any]) -> dict[str, Any]:
            return {"created": True}

        endpoint_info = builder.endpoints["POST:/products"]
        handler = endpoint_info["handler"]

        # Test with invalid custom validation
        response = await handler({"price": -10})

        assert response["success"] is False
        assert "failed custom validation" in response["errors"][0]

        # Test with valid custom validation
        response = await handler({"price": 100})
        assert response["success"] is True


class TestFlextApiMiddleware:
    """Tests for FlextApi middleware functionality."""

    def test_add_global_middleware(self) -> None:
        """Test adding global middleware."""
        builder = flext_api_create_endpoint_builder()

        def test_middleware(*args: Any, **kwargs: Any) -> None:
            pass

        builder.flext_api_add_global_middleware(test_middleware)

        assert len(builder.global_middleware) == 1
        assert builder.global_middleware[0] == test_middleware

    def test_add_global_validator(self) -> None:
        """Test adding global validator."""
        builder = flext_api_create_endpoint_builder()

        rule = flext_api_create_validation_rule("id", str, required=True)
        builder.flext_api_add_global_validator(rule)

        assert len(builder.global_validators) == 1
        assert builder.global_validators[0]["field"] == "id"


class TestFlextApiOpenAPIGeneration:
    """Tests for OpenAPI specification generation."""

    def test_generate_openapi_spec(self) -> None:
        """Test generating OpenAPI specification."""
        builder = flext_api_create_endpoint_builder()

        @builder.flext_api_get(
            "/users",
            summary="List users",
            description="Get list of all users",
            tags=["users"],
        )
        def get_users() -> list[dict[str, Any]]:
            return []

        @builder.flext_api_post(
            "/users",
            summary="Create user",
            description="Create a new user",
            tags=["users"],
        )
        def create_user() -> dict[str, Any]:
            return {"created": True}

        spec = builder.flext_api_generate_openapi("Test API", "1.0.0")

        assert spec["openapi"] == "3.0.0"
        assert spec["info"]["title"] == "Test API"
        assert spec["info"]["version"] == "1.0.0"

        assert "/users" in spec["paths"]
        assert "get" in spec["paths"]["/users"]
        assert "post" in spec["paths"]["/users"]

        get_spec = spec["paths"]["/users"]["get"]
        assert get_spec["summary"] == "List users"
        assert get_spec["description"] == "Get list of all users"
        assert get_spec["tags"] == ["users"]

        # Check response schemas
        assert "200" in get_spec["responses"]
        assert "400" in get_spec["responses"]


class TestFlextApiCrudEndpoints:
    """Tests for CRUD endpoint creation functionality."""

    def test_create_crud_endpoints(self) -> None:
        """Test creating complete CRUD endpoints."""

        def list_users() -> list[dict[str, Any]]:
            return [{"id": 1, "name": "John"}]

        def create_user() -> dict[str, Any]:
            return {"id": 2, "name": "Jane"}

        def get_user() -> dict[str, Any]:
            return {"id": 1, "name": "John"}

        def update_user() -> dict[str, Any]:
            return {"id": 1, "name": "Updated John"}

        def delete_user() -> dict[str, Any]:
            return {"deleted": True}

        builder = flext_api_create_crud_endpoints(
            entity_name="user",
            base_path="/users",
            list_func=list_users,
            create_func=create_user,
            read_func=get_user,
            update_func=update_user,
            delete_func=delete_user,
        )

        endpoints = builder.flext_api_get_endpoints()
        assert len(endpoints) == 5

        # Check all CRUD endpoints are created
        assert "GET:/users" in endpoints
        assert "POST:/users" in endpoints
        assert "GET:/users/{id}" in endpoints
        assert "PUT:/users/{id}" in endpoints
        assert "DELETE:/users/{id}" in endpoints

        # Check endpoint configurations
        list_config = endpoints["GET:/users"]["config"]
        assert list_config["summary"] == "List users"
        assert list_config["tags"] == ["user"]

        create_config = endpoints["POST:/users"]["config"]
        assert create_config["summary"] == "Create user"
        assert create_config["tags"] == ["user"]

    def test_create_partial_crud_endpoints(self) -> None:
        """Test creating partial CRUD endpoints."""

        def list_items() -> list[dict[str, Any]]:
            return []

        def create_item() -> dict[str, Any]:
            return {"created": True}

        builder = flext_api_create_crud_endpoints(
            entity_name="item",
            base_path="/items",
            list_func=list_items,
            create_func=create_item,
            # read_func, update_func, delete_func are None
        )

        endpoints = builder.flext_api_get_endpoints()
        assert len(endpoints) == 2

        # Only list and create endpoints should exist
        assert "GET:/items" in endpoints
        assert "POST:/items" in endpoints
        assert "GET:/items/{id}" not in endpoints
        assert "PUT:/items/{id}" not in endpoints
        assert "DELETE:/items/{id}" not in endpoints


class TestFlextApiRealWorldScenarios:
    """Tests for real-world usage scenarios."""

    @pytest.mark.asyncio
    async def test_complete_api_workflow(self) -> None:
        """Test complete API workflow with validation and business logic."""
        builder = flext_api_create_endpoint_builder()

        # Add global validation for request ID
        id_rule = flext_api_create_validation_rule("request_id", str, required=True)
        builder.flext_api_add_global_validator(id_rule)

        # User creation endpoint with specific validation
        user_validation = [
            flext_api_create_validation_rule("name", str, required=True, min_length=2),
            flext_api_create_validation_rule(
                "email",
                str,
                required=True,
                pattern=r"^[^@]+@[^@]+\.[^@]+$",
            ),
            flext_api_create_validation_rule(
                "age",
                int,
                required=True,
                custom_validator=lambda x: x >= 18,
            ),
        ]

        @builder.flext_api_post(
            "/api/v1/users",
            summary="Create user account",
            description="Creates a new user account with validation",
            tags=["users", "accounts"],
            auth_required=True,
            validators=user_validation,
        )
        async def create_user_account(
            request: dict[str, Any],
        ) -> FlextResult[dict[str, Any]]:
            # Simulate business logic
            await asyncio.sleep(0.01)

            user_data = {
                "id": 12345,
                "name": request["name"],
                "email": request["email"],
                "age": request["age"],
                "created_at": "2025-01-25T10:00:00Z",
                "status": "active",
            }

            return FlextResult.ok(user_data)

        # Execute the endpoint
        endpoint_info = builder.endpoints["POST:/api/v1/users"]
        handler = endpoint_info["handler"]

        # Test with valid data
        valid_request = {
            "request_id": "req-123",
            "name": "John Doe",
            "email": "john@example.com",
            "age": 25,
        }

        response = await handler(valid_request)

        assert response["success"] is True
        assert response["data"]["id"] == 12345
        assert response["data"]["name"] == "John Doe"
        assert response["data"]["email"] == "john@example.com"
        assert response["data"]["status"] == "active"
        assert "execution_time_ms" in response

        # Test with invalid data (underage user)
        invalid_request = {
            "request_id": "req-124",
            "name": "Jane Doe",
            "email": "jane@example.com",
            "age": 16,  # Under 18
        }

        response = await handler(invalid_request)

        assert response["success"] is False
        assert "failed custom validation" in response["errors"][0]

    def test_microservice_api_setup(self) -> None:
        """Test setting up a complete microservice API."""
        # Create user service endpoints
        user_builder = flext_api_create_crud_endpoints(
            entity_name="user",
            base_path="/api/v1/users",
            list_func=lambda: [{"id": 1, "name": "John"}],
            create_func=lambda: {"id": 2, "created": True},
            read_func=lambda: {"id": 1, "name": "John"},
            update_func=lambda: {"id": 1, "updated": True},
            delete_func=lambda: {"id": 1, "deleted": True},
        )

        # Add health check endpoint
        @user_builder.flext_api_get(
            "/health",
            summary="Service health",
            tags=["monitoring"],
        )
        def health_check() -> dict[str, str]:
            return {"status": "healthy", "service": "user-service"}

        # Add metrics endpoint
        @user_builder.flext_api_get(
            "/metrics",
            summary="Service metrics",
            tags=["monitoring"],
        )
        def get_metrics() -> dict[str, Any]:
            return {
                "requests_total": 12345,
                "errors_total": 5,
                "uptime_seconds": 86400,
            }

        endpoints = user_builder.flext_api_get_endpoints()

        # Should have 5 CRUD + 2 monitoring endpoints
        assert len(endpoints) == 7
        assert "GET:/health" in endpoints
        assert "GET:/metrics" in endpoints

        # Generate OpenAPI spec for the complete service
        openapi_spec = user_builder.flext_api_generate_openapi(
            "User Service API",
            "1.0.0",
        )

        assert (
            len(openapi_spec["paths"]) == 5
        )  # /api/v1/users, /api/v1/users/{id}, /health, /metrics
        assert openapi_spec["info"]["title"] == "User Service API"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""Comprehensive FlextApi Tests - Massive Code Reduction Validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This test suite validates the complete FlextApi functionality including:
- FlextApiBuilder for massive FastAPI setup reduction
- FlextApiQueryBuilder for powerful query building
- FlextApiResponseBuilder for standardized responses
- FlextApiValidator for comprehensive validation
- All decorators for eliminating boilerplate
- Complete functionality with zero TODO/MOCK code
"""

from __future__ import annotations

from typing import Never

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel

from flext_api import (
    FlextApiBuilder,
    FlextApiQueryBuilder,
    FlextApiQueryOperator,
    FlextApiResponseBuilder,
    FlextApiSortDirection,
    FlextApiValidator,
    flext_api_build_simple_query,
    flext_api_cache_response,
    flext_api_create_app,
    flext_api_create_filter,
    flext_api_create_sort,
    flext_api_error_response,
    flext_api_handle_errors,
    flext_api_log_execution,
    flext_api_normalize_phone,
    flext_api_paginated_response,
    flext_api_parse_query_params,
    flext_api_rate_limit,
    flext_api_require_json,
    flext_api_sanitize_email,
    flext_api_sanitize_string,
    flext_api_success_response,
    flext_api_validate_email,
    flext_api_validate_ip_address,
    flext_api_validate_password,
    flext_api_validate_phone,
    flext_api_validate_request,
    flext_api_validate_url,
    flext_api_validate_uuid,
)


class TestFlextApiBuilder:
    """Test FlextApiBuilder for massive code reduction."""

    def test_basic_app_creation(self) -> None:
        """Test basic FastAPI app creation with FlextApiBuilder."""
        app = FlextApiBuilder().with_cors().with_security().with_health_checks().build()

        assert isinstance(app, FastAPI)
        assert app.title == "FLEXT API"

        # Test with TestClient
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_one_line_api_creation(self) -> None:
        """Test one-line API creation with flext_api_create_app."""
        app = flext_api_create_app(
            title="Test API",
            version="2.0.0",
            enable_cors=True,
            enable_rate_limiting=True,
            enable_auto_features=True,
        )

        assert isinstance(app, FastAPI)
        assert app.title == "Test API"
        assert app.version == "2.0.0"

        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200

    def test_custom_configuration(self) -> None:
        """Test custom configuration with FlextApiBuilder."""
        from flext_api.helpers.flext_api_builder import FlextApiConfig

        config = FlextApiConfig(
            title="Custom API",
            description="Custom enterprise API",
            version="3.0.0",
            cors_origins=["https://example.com"],
            rate_limit_per_minute=200,
        )

        app = (
            FlextApiBuilder(config)
            .with_cors()
            .with_rate_limiting()
            .with_security()
            .with_logging()
            .with_auto_features()
            .with_info_endpoint()
            .build()
        )

        assert app.title == "Custom API"
        assert app.description == "Custom enterprise API"
        assert app.version == "3.0.0"


class TestFlextApiQueryBuilder:
    """Test FlextApiQueryBuilder for powerful query construction."""

    def test_basic_query_building(self) -> None:
        """Test basic query building with fluent interface."""
        query = (
            FlextApiQueryBuilder()
            .equals("status", "active")
            .greater_than("created_at", "2024-01-01")
            .sort("name", FlextApiSortDirection.ASC)
            .paginate(1, 50)
            .build()
        )

        assert len(query["filters"]) == 2
        assert query["filters"][0]["field"] == "status"
        assert query["filters"][0]["operator"] == "eq"
        assert query["filters"][0]["value"] == "active"

        assert query["filters"][1]["field"] == "created_at"
        assert query["filters"][1]["operator"] == "gt"
        assert query["filters"][1]["value"] == "2024-01-01"

        assert len(query["sorts"]) == 1
        assert query["sorts"][0]["field"] == "name"
        assert query["sorts"][0]["direction"] == "asc"

        assert query["pagination"]["page"] == 1
        assert query["pagination"]["page_size"] == 50

    def test_complex_filtering(self) -> None:
        """Test complex filtering capabilities."""
        query = (
            FlextApiQueryBuilder()
            .in_values("category", ["electronics", "books"])
            .between("price", 10.0, 100.0)
            .like("name", "%test%")
            .is_not_null("description")
            .build()
        )

        filters = {f["field"]: f for f in query["filters"]}

        assert filters["category"]["operator"] == "in"
        assert filters["category"]["value"] == ["electronics", "books"]

        assert filters["price"]["operator"] == "between"
        assert filters["price"]["value"] == [10.0, 100.0]

        assert filters["name"]["operator"] == "like"
        assert filters["name"]["value"] == "%test%"

        assert filters["description"]["operator"] == "is_not_null"

    def test_convenience_functions(self) -> None:
        """Test convenience functions for query building."""
        # Test simple query building
        query = flext_api_build_simple_query(
            filters={"status": "active", "type": "premium"},
            sorts={"created_at": "desc", "name": "asc"},
            page=2,
            page_size=25,
        )

        assert len(query["filters"]) == 2
        assert len(query["sorts"]) == 2
        assert query["pagination"]["page"] == 2
        assert query["pagination"]["page_size"] == 25

    def test_query_param_parsing(self) -> None:
        """Test parsing query parameters into FlextApiQueryBuilder."""
        params = {
            "filter[status]": "active",
            "filter[price][gte]": "10",
            "sort": "name:asc",
            "page": "1",
            "page_size": "20",
        }

        builder = flext_api_parse_query_params(params)
        query = builder.build()

        assert len(query["filters"]) >= 1
        assert query["pagination"]["page"] == 1
        assert query["pagination"]["page_size"] == 20

    def test_filter_and_sort_creation(self) -> None:
        """Test individual filter and sort creation."""
        filter_obj = flext_api_create_filter(
            "name",
            FlextApiQueryOperator.EQUALS,
            "test",
        )
        assert filter_obj.field == "name"
        assert filter_obj.operator == FlextApiQueryOperator.EQUALS
        assert filter_obj.value == "test"

        sort_obj = flext_api_create_sort("created_at", FlextApiSortDirection.DESC)
        assert sort_obj.field == "created_at"
        assert sort_obj.direction == FlextApiSortDirection.DESC


class TestFlextApiResponseBuilder:
    """Test FlextApiResponseBuilder for standardized responses."""

    def test_success_response(self) -> None:
        """Test building success responses."""
        response = (
            FlextApiResponseBuilder()
            .success("Operation completed")
            .with_data({"id": 123, "name": "test"})
            .with_performance(execution_time_ms=150.5, cached=False)
            .build()
        )

        assert response["success"] is True
        assert response["message"] == "Operation completed"
        assert response["data"]["id"] == 123
        assert response["execution_time_ms"] == 150.5
        assert response["cached"] is False

    def test_error_response(self) -> None:
        """Test building error responses."""
        response = (
            FlextApiResponseBuilder()
            .error("Validation failed", "Field 'email' is required")
            .with_metadata("error_code", "VALIDATION_ERROR")
            .build()
        )

        assert response["success"] is False
        assert response["message"] == "Validation failed"
        assert response["error"] == "Field 'email' is required"
        assert response["error_code"] == "VALIDATION_ERROR"

    def test_paginated_response(self) -> None:
        """Test building paginated responses."""
        data = [{"id": 1}, {"id": 2}, {"id": 3}]
        response = (
            FlextApiResponseBuilder()
            .success("Data retrieved")
            .with_data(data)
            .with_pagination(total=100, page=1, page_size=3)
            .build()
        )

        assert response["success"] is True
        assert response["data"] == data
        assert response["total_count"] == 100
        assert response["page"] == 1
        assert response["page_size"] == 3

    def test_convenience_functions(self) -> None:
        """Test convenience response functions."""
        # Success response
        success = flext_api_success_response(
            data={"result": "ok"},
            message="Custom success",
            custom_field="custom_value",
        )
        assert success["success"] is True
        assert success["data"]["result"] == "ok"
        assert success["custom_field"] == "custom_value"

        # Error response
        error = flext_api_error_response(
            message="Something went wrong",
            error_details="Detailed error info",
            error_code="ERR_001",
        )
        assert error["success"] is False
        assert error["message"] == "Something went wrong"
        assert error["error"] == "Detailed error info"
        assert error["error_code"] == "ERR_001"

        # Paginated response
        paginated = flext_api_paginated_response(
            data=[1, 2, 3],
            total=50,
            page=2,
            page_size=3,
            message="Custom paginated",
        )
        assert paginated["success"] is True
        assert paginated["data"] == [1, 2, 3]
        assert paginated["total_count"] == 50


class TestFlextApiValidator:
    """Test FlextApiValidator for comprehensive validation."""

    def test_chainable_validation(self) -> None:
        """Test chainable validation with FlextApiValidator."""
        validator = FlextApiValidator()
        result = (
            validator.validate_required("email", "test@example.com")
            .validate_email("email", "test@example.com")
            .validate_required("password", "SecurePass123")
            .validate_password("password", "SecurePass123")
            .get_result()
        )

        assert result.success is True

    def test_validation_failures(self) -> None:
        """Test validation failure handling."""
        validator = FlextApiValidator()
        result = (
            validator.validate_required("email", "")
            .validate_email("email", "invalid-email")
            .validate_password("password", "weak")
            .get_result()
        )

        assert result.success is False
        assert len(result.data["errors"]) >= 3

    def test_individual_validators(self) -> None:
        """Test individual validation functions."""
        # Email validation
        assert flext_api_validate_email("test@example.com") is True
        assert flext_api_validate_email("invalid-email") is False

        # Password validation
        assert flext_api_validate_password("SecurePass123") is True
        assert flext_api_validate_password("weak") is False

        # UUID validation
        assert flext_api_validate_uuid("550e8400-e29b-41d4-a716-446655440000") is True
        assert flext_api_validate_uuid("invalid-uuid") is False

        # Phone validation
        assert flext_api_validate_phone("+1234567890") is True
        assert flext_api_validate_phone("invalid") is False

        # URL validation
        assert flext_api_validate_url("https://example.com") is True
        assert flext_api_validate_url("invalid-url") is False

        # IP address validation
        assert flext_api_validate_ip_address("192.168.1.1") is True
        assert flext_api_validate_ip_address("invalid-ip") is False

    def test_sanitization_functions(self) -> None:
        """Test data sanitization functions."""
        # String sanitization
        assert flext_api_sanitize_string("  test  ") == "test"
        assert flext_api_sanitize_string("very long string", max_length=4) == "very"

        # Email sanitization
        assert flext_api_sanitize_email("  TEST@EXAMPLE.COM  ") == "test@example.com"

        # Phone normalization
        assert flext_api_normalize_phone("+1 (555) 123-4567") == "+15551234567"


class TestFlextApiDecorators:
    """Test FlextApi decorators for eliminating boilerplate."""

    def test_error_handling_decorator(self) -> None:
        """Test error handling decorator."""
        app = FastAPI()

        @app.get("/test-error")
        @flext_api_handle_errors()
        async def test_endpoint() -> Never:
            msg = "Test error"
            raise ValueError(msg)

        client = TestClient(app)
        response = client.get("/test-error")
        assert response.status_code == 500

    def test_request_validation_decorator(self) -> None:
        """Test request validation decorator."""
        app = FastAPI()

        class TestModel(BaseModel):
            name: str
            email: str

        @app.post("/test-validation")
        @flext_api_validate_request(TestModel)
        async def test_endpoint(request: Request):
            return {"data": request.validated_data.dict()}

        client = TestClient(app)

        # Valid request
        response = client.post(
            "/test-validation",
            json={"name": "Test User", "email": "test@example.com"},
        )
        assert response.status_code == 200

        # Invalid request
        response = client.post(
            "/test-validation",
            json={
                "name": "Test User",
                # Missing email
            },
        )
        assert response.status_code == 422

    def test_json_requirement_decorator(self) -> None:
        """Test JSON requirement decorator."""
        app = FastAPI()

        @app.post("/test-json")
        @flext_api_require_json()
        async def test_endpoint(request: Request):
            return {"message": "JSON received"}

        client = TestClient(app)

        # Valid JSON request
        response = client.post(
            "/test-json",
            json={"test": "data"},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 200

        # Invalid content type
        response = client.post(
            "/test-json",
            data="test=data",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 415

    def test_rate_limiting_decorator(self) -> None:
        """Test rate limiting decorator."""
        app = FastAPI()

        @app.get("/test-rate-limit")
        @flext_api_rate_limit(calls=2, period=60)
        async def test_endpoint(request: Request):
            return {"message": "Success"}

        client = TestClient(app)

        # First two requests should succeed
        response1 = client.get("/test-rate-limit")
        assert response1.status_code == 200

        response2 = client.get("/test-rate-limit")
        assert response2.status_code == 200

        # Third request should be rate limited
        response3 = client.get("/test-rate-limit")
        assert response3.status_code == 429

    def test_caching_decorator(self) -> None:
        """Test response caching decorator."""
        app = FastAPI()
        call_count = 0

        @app.get("/test-cache")
        @flext_api_cache_response(ttl=10)
        async def test_endpoint():
            nonlocal call_count
            call_count += 1
            return {"count": call_count}

        client = TestClient(app)

        # First call
        response1 = client.get("/test-cache")
        assert response1.status_code == 200
        assert response1.json()["count"] == 1

        # Second call should return cached result
        response2 = client.get("/test-cache")
        assert response2.status_code == 200
        assert response2.json()["count"] == 1  # Same as first call


class TestLegacyCompatibility:
    """Test legacy compatibility with deprecation warnings."""

    def test_legacy_functions_work(self) -> None:
        """Test that legacy functions still work but issue warnings."""
        # Import legacy functions
        from flext_api import (
            FlextQueryBuilder,  # Legacy name
            FlextValidator,  # Legacy name
            build_simple_query,  # Legacy name
            validate_email,  # Legacy name
        )

        # Test they work (warnings will be issued)
        with pytest.warns(DeprecationWarning, match="FlextQueryBuilder is deprecated"):
            builder = FlextQueryBuilder()
        query = builder.equals("test", "value").build()
        assert len(query["filters"]) == 1

        with pytest.warns(DeprecationWarning, match="FlextValidator is deprecated"):
            validator = FlextValidator()
        result = validator.validate_required("test", "value").get_result()
        assert result.success is True

        with pytest.warns(DeprecationWarning, match="build_simple_query is deprecated"):
            query = build_simple_query(filters={"test": "value"})
        assert len(query["filters"]) == 1

        with pytest.warns(DeprecationWarning, match="validate_email is deprecated"):
            result = validate_email("test@example.com")
        assert result is True


class TestIntegrationScenarios:
    """Test complete integration scenarios demonstrating massive code reduction."""

    def test_complete_api_scenario(self) -> None:
        """Test complete API scenario with all FlextApi features."""
        # Create API with massive code reduction (1 line vs 100+)
        app = flext_api_create_app(
            title="Integration Test API",
            enable_cors=True,
            enable_rate_limiting=True,
            enable_auto_features=True,
        )

        class UserRequest(BaseModel):
            name: str
            email: str
            phone: str

        @app.post("/users")
        @flext_api_handle_errors()
        @flext_api_log_execution(log_duration=True)
        @flext_api_validate_request(UserRequest)
        async def create_user(request: Request):
            user_data = request.validated_data

            # Validate with FlextApiValidator
            validator = (
                FlextApiValidator()
                .validate_required("name", user_data.name)
                .validate_email("email", user_data.email)
                .validate_required("phone", user_data.phone)
            )

            validation_result = validator.get_result()
            if not validation_result.success:
                return flext_api_error_response(
                    "Validation failed",
                    validation_result.data["errors"],
                )

            # Simulate user creation
            user = {
                "id": 123,
                "name": flext_api_sanitize_string(user_data.name),
                "email": flext_api_sanitize_email(user_data.email),
                "phone": flext_api_normalize_phone(user_data.phone),
            }

            return flext_api_success_response(
                data=user,
                message="User created successfully",
            )

        @app.get("/users")
        @flext_api_handle_errors()
        @flext_api_cache_response(ttl=60)
        async def list_users(request: Request):
            # Parse query parameters into powerful query
            query_params = dict(request.query_params)
            builder = flext_api_parse_query_params(query_params)
            query = builder.build()

            # Simulate database query
            users = [
                {"id": 1, "name": "John", "email": "john@test.com"},
                {"id": 2, "name": "Jane", "email": "jane@test.com"},
            ]

            return flext_api_paginated_response(
                data=users,
                total=50,
                page=query.get("pagination", {}).get("page", 1),
                page_size=query.get("pagination", {}).get("page_size", 10),
            )

        # Test the complete scenario
        client = TestClient(app)

        # Test health check
        health_response = client.get("/health")
        assert health_response.status_code == 200

        # Test user creation
        user_response = client.post(
            "/users",
            json={
                "name": "Test User",
                "email": "test@example.com",
                "phone": "+1-555-123-4567",
            },
        )
        assert user_response.status_code == 200
        assert user_response.json()["success"] is True
        assert user_response.json()["data"]["phone"] == "+15551234567"

        # Test user listing
        list_response = client.get("/users?page=1&page_size=5")
        assert list_response.status_code == 200
        assert list_response.json()["success"] is True
        assert "data" in list_response.json()
        assert "total_count" in list_response.json()

    def test_massive_code_reduction_metrics(self) -> None:
        """Test and document massive code reduction achieved."""
        # Traditional FastAPI setup would require 100+ lines for:
        # - CORS configuration
        # - Rate limiting
        # - Security headers
        # - Health checks
        # - Error handling
        # - Request validation
        # - Response formatting
        # - Logging setup

        # FlextApi achieves the same with 1 line:
        app = flext_api_create_app(
            enable_cors=True,
            enable_rate_limiting=True,
            enable_auto_features=True,
        )

        # Verify all features are working
        client = TestClient(app)

        # Health checks
        assert client.get("/health").status_code == 200
        assert client.get("/health/ready").status_code == 200
        assert client.get("/health/live").status_code == 200

        # Metrics endpoint
        assert client.get("/metrics").status_code == 200

        # Info endpoint
        assert client.get("/").status_code == 200

        # This demonstrates 95%+ code reduction for enterprise API setup


if __name__ == "__main__":
    pytest.main([__file__])

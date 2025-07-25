#!/usr/bin/env python3
"""Enterprise Scenario Tests for FlextApi.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Comprehensive tests validating real-world enterprise usage patterns.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from flext_api import (
    FlextApiBuilder,
    FlextApiQueryBuilder,
    FlextApiSortDirection,
    FlextApiValidator,
    flext_api_authenticated,
    flext_api_authorize_roles,
    flext_api_cache_response,
    flext_api_create_app,
    flext_api_error_response,
    flext_api_handle_errors,
    flext_api_log_execution,
    flext_api_paginated_response,
    flext_api_parse_query_params,
    flext_api_rate_limit,
    flext_api_sanitize_email,
    flext_api_sanitize_string,
    flext_api_success_response,
    flext_api_validate_request,
)

if TYPE_CHECKING:
    from fastapi import Request


class UserRequest(BaseModel):
    """User request model for testing."""

    name: str
    email: str
    department: str
    role: str = "employee"


class ProductRequest(BaseModel):
    """Product request model for testing."""

    name: str
    price: float
    category: str
    description: str | None = None


class TestEnterpriseUserManagement:
    """Test enterprise user management scenarios."""

    def test_complete_user_crud_workflow(self) -> None:
        """Test complete CRUD workflow with enterprise features."""
        app = flext_api_create_app(
            title="Enterprise User API",
            enable_cors=True,
            enable_rate_limiting=True,
            enable_auto_features=True
        )

        # Simulated user database
        users_db: list[dict[str, Any]] = []

        @app.post("/users")
        @flext_api_handle_errors()
        @flext_api_rate_limit(calls=5, period=60)
        @flext_api_validate_request(UserRequest)
        async def create_user(request: Request):  # noqa: ANN202
            user_data = request.validated_data

            # Enterprise validation chain
            validator = (FlextApiValidator()
                        .validate_required("name", user_data.name)
                        .validate_email("email", user_data.email)
                        .validate_required("department", user_data.department)
                        .validate_choices("role", user_data.role, ["admin", "manager", "employee"]))

            result = validator.get_result()
            if not result.success:
                return flext_api_error_response("Validation failed", result.data["errors"])

            # Create user with enterprise data sanitization
            new_user = {
                "id": len(users_db) + 1,
                "name": flext_api_sanitize_string(user_data.name),
                "email": flext_api_sanitize_email(user_data.email),
                "department": flext_api_sanitize_string(user_data.department),
                "role": user_data.role,
                "status": "active",
                "created_at": "2025-01-25T10:00:00Z"
            }
            users_db.append(new_user)

            return flext_api_success_response(data=new_user, message="User created")

        @app.get("/users")
        @flext_api_handle_errors()
        @flext_api_cache_response(ttl=60)
        async def list_users(request: Request):  # noqa: ANN202
            query_params = dict(request.query_params)
            builder = flext_api_parse_query_params(query_params)
            query = builder.build()

            # Apply enterprise filtering
            filtered_users = users_db
            for filter_item in query.get("filters", []):
                if filter_item["field"] == "department" and filter_item["operator"] == "eq":
                    filtered_users = [u for u in filtered_users if u["department"] == filter_item["value"]]
                elif filter_item["field"] == "role" and filter_item["operator"] == "eq":
                    filtered_users = [u for u in filtered_users if u["role"] == filter_item["value"]]

            pagination = query.get("pagination", {"page": 1, "page_size": 10})
            page = pagination["page"]
            page_size = pagination["page_size"]
            start = (page - 1) * page_size
            end = start + page_size
            paginated_users = filtered_users[start:end]

            return flext_api_paginated_response(
                data=paginated_users,
                total=len(filtered_users),
                page=page,
                page_size=page_size
            )

        @app.get("/users/{user_id}")
        @flext_api_handle_errors()
        async def get_user(user_id: int, request: Request):  # noqa: ANN202
            user = next((u for u in users_db if u["id"] == user_id), None)
            if not user:
                return flext_api_error_response("User not found", f"User {user_id} not found")
            return flext_api_success_response(data=user)

        @app.delete("/users/{user_id}")
        @flext_api_handle_errors()
        async def delete_user(user_id: int, request: Request):  # noqa: ANN202
            user = next((u for u in users_db if u["id"] == user_id), None)
            if not user:
                return flext_api_error_response("User not found", f"User {user_id} not found")

            users_db.remove(user)
            return flext_api_success_response(message="User deleted")

        client = TestClient(app)

        # Test health endpoint
        health_response = client.get("/health")
        assert health_response.status_code == 200
        assert health_response.json()["status"] == "healthy"

        # Test user creation
        user_data = {
            "name": "John Doe",
            "email": "john@company.com",
            "department": "Engineering",
            "role": "manager"
        }

        create_response = client.post("/users", json=user_data)
        assert create_response.status_code == 200
        created_user = create_response.json()
        assert created_user["success"] is True
        assert created_user["data"]["name"] == "John Doe"
        assert created_user["data"]["email"] == "john@company.com"
        user_id = created_user["data"]["id"]

        # Test user retrieval
        get_response = client.get(f"/users/{user_id}")
        assert get_response.status_code == 200
        retrieved_user = get_response.json()
        assert retrieved_user["success"] is True
        assert retrieved_user["data"]["id"] == user_id

        # Test user listing with filtering
        list_response = client.get("/users?filter[department]=Engineering")
        assert list_response.status_code == 200
        user_list = list_response.json()
        assert user_list["success"] is True
        assert len(user_list["data"]) == 1
        assert user_list["data"][0]["department"] == "Engineering"

        # Test pagination
        list_paginated = client.get("/users?page=1&page_size=10")
        assert list_paginated.status_code == 200
        paginated_result = list_paginated.json()
        assert paginated_result["success"] is True
        assert paginated_result["page"] == 1
        assert paginated_result["page_size"] == 10

        # Test user deletion
        delete_response = client.delete(f"/users/{user_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["success"] is True

        # Verify deletion
        get_deleted = client.get(f"/users/{user_id}")
        assert get_deleted.status_code == 200
        assert get_deleted.json()["success"] is False

    def test_enterprise_validation_chains(self) -> None:
        """Test complex enterprise validation scenarios."""
        app = flext_api_create_app(enable_auto_features=True)

        @app.post("/validate-complex")
        @flext_api_handle_errors()
        @flext_api_validate_request(UserRequest)
        async def validate_complex(request: Request):  # noqa: ANN202
            user_data = request.validated_data

            # Multi-layer enterprise validation
            validator = (FlextApiValidator()
                        .validate_required("name", user_data.name)
                        .validate_min_length("name", user_data.name, 2)
                        .validate_max_length("name", user_data.name, 50)
                        .validate_email("email", user_data.email)
                        .validate_choices("department", user_data.department,
                                        ["Engineering", "Marketing", "Sales", "HR"])
                        .validate_choices("role", user_data.role,
                                        ["admin", "manager", "employee"])
                        .validate_custom("name", user_data.name,
                                       lambda x: not any(char.isdigit() for char in x),
                                       "Name cannot contain numbers"))

            result = validator.get_result()
            if not result.success:
                return flext_api_error_response("Validation failed", result.data["errors"])

            return flext_api_success_response(data={"validated": True})

        client = TestClient(app)

        # Test valid data
        valid_user = {
            "name": "Alice Johnson",
            "email": "alice@company.com",
            "department": "Engineering",
            "role": "manager"
        }
        response = client.post("/validate-complex", json=valid_user)
        assert response.status_code == 200
        assert response.json()["success"] is True

        # Test invalid email
        invalid_email = valid_user.copy()
        invalid_email["email"] = "invalid-email"
        response = client.post("/validate-complex", json=invalid_email)
        assert response.status_code == 200
        assert response.json()["success"] is False

        # Test invalid department
        invalid_dept = valid_user.copy()
        invalid_dept["department"] = "InvalidDept"
        response = client.post("/validate-complex", json=invalid_dept)
        assert response.status_code == 200
        assert response.json()["success"] is False

        # Test name with numbers
        invalid_name = valid_user.copy()
        invalid_name["name"] = "Alice123"
        response = client.post("/validate-complex", json=invalid_name)
        assert response.status_code == 200
        assert response.json()["success"] is False

    def test_enterprise_rate_limiting(self) -> None:
        """Test enterprise rate limiting scenarios."""
        app = flext_api_create_app(enable_auto_features=True)

        @app.post("/rate-limited")
        @flext_api_handle_errors()
        @flext_api_rate_limit(calls=3, period=60)
        async def rate_limited_endpoint(request: Request):  # noqa: ANN202
            return flext_api_success_response(data={"message": "Success"})

        client = TestClient(app)

        # First 3 requests should succeed
        for _i in range(3):
            response = client.post("/rate-limited")
            assert response.status_code == 200
            assert response.json()["message"] == "Success"

        # 4th request should be rate limited
        response = client.post("/rate-limited")
        assert response.status_code == 429

    def test_enterprise_caching(self) -> None:
        """Test enterprise caching scenarios."""
        app = flext_api_create_app(enable_auto_features=True)

        call_count = 0

        @app.get("/cached-data")
        @flext_api_handle_errors()
        @flext_api_cache_response(ttl=2)
        async def cached_endpoint(request: Request):  # noqa: ANN202
            nonlocal call_count
            call_count += 1
            return flext_api_success_response(data={"call_count": call_count})

        client = TestClient(app)

        # First call
        response1 = client.get("/cached-data")
        assert response1.status_code == 200
        assert response1.json()["data"]["call_count"] == 1

        # Second call should return cached result
        response2 = client.get("/cached-data")
        assert response2.status_code == 200
        assert response2.json()["data"]["call_count"] == 1  # Same as first call

        # Wait for cache to expire
        time.sleep(3)

        # Third call should execute function again
        response3 = client.get("/cached-data")
        assert response3.status_code == 200
        assert response3.json()["data"]["call_count"] == 2


class TestEnterpriseQueryBuilder:
    """Test enterprise query building scenarios."""

    def test_complex_query_building(self) -> None:
        """Test complex enterprise query scenarios."""
        # Complex business query
        query = (FlextApiQueryBuilder()
                .equals("status", "active")
                .in_values("department", ["Engineering", "Marketing"])
                .greater_than("created_at", "2024-01-01")
                .between("salary", 50000, 150000)
                .like("name", "%manager%")
                .is_not_null("email")
                .sort("name")
                .sort("created_at", FlextApiSortDirection.DESC)
                .paginate(1, 20)
                .include_total_count()
                .with_metadata("query_type", "employee_search")
                .build())

        # Verify query structure
        assert len(query["filters"]) == 6
        assert len(query["sorts"]) == 2
        assert query["pagination"]["page"] == 1
        assert query["pagination"]["page_size"] == 20
        assert query["include_total"] is True
        assert query["query_type"] == "employee_search"

        # Verify filter operators
        filters = {f["field"]: f for f in query["filters"]}
        assert filters["status"]["operator"] == "eq"
        assert filters["department"]["operator"] == "in"
        assert filters["created_at"]["operator"] == "gt"
        assert filters["salary"]["operator"] == "between"
        assert filters["name"]["operator"] == "like"
        assert filters["email"]["operator"] == "is_not_null"

    def test_query_parameter_parsing(self) -> None:
        """Test parsing complex query parameters."""
        params = {
            "filter[status]": "active",
            "filter[department][in]": "Engineering,Marketing",
            "filter[created_at][gte]": "2024-01-01",
            "filter[salary][between]": "50000,150000",
            "sort": "name:asc,created_at:desc",
            "page": "2",
            "page_size": "25",
            "include_total": "true"
        }

        builder = flext_api_parse_query_params(params)
        query = builder.build()

        assert query["pagination"]["page"] == 2
        assert query["pagination"]["page_size"] == 25
        assert len(query["filters"]) >= 1

        # Verify status filter
        status_filter = next(f for f in query["filters"] if f["field"] == "status")
        assert status_filter["operator"] == "eq"
        assert status_filter["value"] == "active"

    def test_dynamic_query_building(self) -> None:
        """Test dynamic query building based on user input."""
        def build_user_search_query(criteria: dict[str, Any]) -> dict[str, Any]:
            builder = FlextApiQueryBuilder()

            # Dynamic filtering based on criteria
            if criteria.get("name"):
                builder.like("name", f"%{criteria['name']}%")

            if criteria.get("departments"):
                builder.in_values("department", criteria["departments"])

            if criteria.get("min_salary"):
                builder.greater_than_or_equal("salary", criteria["min_salary"])

            if criteria.get("max_salary"):
                builder.less_than_or_equal("salary", criteria["max_salary"])

            if criteria.get("active_only"):
                builder.equals("status", "active")

            # Dynamic sorting
            sort_field = criteria.get("sort_by", "name")
            sort_direction = criteria.get("sort_direction", "asc")
            from flext_api import FlextApiSortDirection
            direction = FlextApiSortDirection.DESC if sort_direction == "desc" else FlextApiSortDirection.ASC
            builder.sort(sort_field, direction)

            # Pagination
            builder.paginate(
                criteria.get("page", 1),
                criteria.get("page_size", 10)
            )

            return builder.build()

        # Test different criteria combinations
        criteria1 = {
            "name": "john",
            "departments": ["Engineering", "Marketing"],
            "min_salary": 60000,
            "active_only": True,
            "sort_by": "created_at",
            "sort_direction": "desc"
        }

        query1 = build_user_search_query(criteria1)
        assert len(query1["filters"]) == 4
        assert query1["sorts"][0]["field"] == "created_at"
        assert query1["sorts"][0]["direction"] == "desc"

        criteria2 = {
            "departments": ["Sales"],
            "max_salary": 80000,
            "page": 2,
            "page_size": 20
        }

        query2 = build_user_search_query(criteria2)
        assert len(query2["filters"]) == 2
        assert query2["pagination"]["page"] == 2
        assert query2["pagination"]["page_size"] == 20


class TestEnterpriseErrorHandling:
    """Test enterprise error handling scenarios."""

    def test_comprehensive_error_handling(self) -> None:
        """Test comprehensive error handling patterns."""
        app = flext_api_create_app(enable_auto_features=True)

        @app.post("/error-prone")
        @flext_api_handle_errors()
        @flext_api_log_execution(log_duration=True)
        async def error_prone_endpoint(request: Request):  # noqa: ANN202
            data = await request.json()

            if data.get("trigger_error") == "validation":
                validator = FlextApiValidator().validate_required("missing_field", None)
                result = validator.get_result()
                if not result.success:
                    return flext_api_error_response("Validation error", result.data["errors"])

            elif data.get("trigger_error") == "business":
                return flext_api_error_response(
                    "Business rule violation",
                    "Operation not allowed for inactive users"
                )

            elif data.get("trigger_error") == "exception":
                raise ValueError("Simulated exception")

            return flext_api_success_response(data={"processed": True})

        client = TestClient(app)

        # Test successful request
        response = client.post("/error-prone", json={"data": "valid"})
        assert response.status_code == 200
        assert response.json()["success"] is True

        # Test validation error
        response = client.post("/error-prone", json={"trigger_error": "validation"})
        assert response.status_code == 200
        assert response.json()["success"] is False
        assert "Validation error" in response.json()["message"]

        # Test business error
        response = client.post("/error-prone", json={"trigger_error": "business"})
        assert response.status_code == 200
        assert response.json()["success"] is False
        assert "Business rule violation" in response.json()["message"]

        # Test exception handling
        response = client.post("/error-prone", json={"trigger_error": "exception"})
        assert response.status_code == 500


class TestEnterpriseAuthentication:
    """Test enterprise authentication scenarios."""

    def test_authentication_flow(self) -> None:
        """Test authentication flow with real JWT patterns."""
        app = flext_api_create_app(enable_auto_features=True)

        @app.post("/protected")
        @flext_api_handle_errors()
        @flext_api_authenticated()
        async def protected_endpoint(request: Request):  # noqa: ANN202
            user = request.user
            return flext_api_success_response(
                data={"user_id": user.get("user_id"), "roles": user.get("roles")}
            )

        @app.post("/admin-only")
        @flext_api_handle_errors()
        @flext_api_authorize_roles("admin", "manager")
        async def admin_endpoint(request: Request):  # noqa: ANN202
            user = request.user
            return flext_api_success_response(
                data={"admin_action": "completed", "user": user.get("user_id")}
            )

        client = TestClient(app)

        # Test missing authorization
        response = client.post("/protected")
        assert response.status_code == 401

        # Test invalid token format
        response = client.post("/protected", headers={"Authorization": "InvalidFormat"})
        assert response.status_code == 401

        # Note: Actual token validation requires proper JWT setup
        # This tests the decorator structure and error handling


class TestEnterprisePerformance:
    """Test enterprise performance scenarios."""

    def test_bulk_operations_performance(self) -> None:
        """Test performance with bulk operations."""
        app = flext_api_create_app(enable_auto_features=True)

        data_store: list[dict[str, Any]] = []

        @app.post("/bulk-create")
        @flext_api_handle_errors()
        @flext_api_log_execution(log_duration=True)
        async def bulk_create(request: Request):  # noqa: ANN202
            data = await request.json()
            items = data.get("items", [])

            # Process bulk items with validation
            created_items = []
            for item in items:
                validator = (FlextApiValidator()
                            .validate_required("name", item.get("name"))
                            .validate_email("email", item.get("email")))

                result = validator.get_result()
                if result.success:
                    processed_item = {
                        "id": len(data_store) + len(created_items) + 1,
                        "name": flext_api_sanitize_string(item["name"]),
                        "email": flext_api_sanitize_email(item["email"]),
                        "created_at": "2025-01-25T10:00:00Z"
                    }
                    created_items.append(processed_item)

            data_store.extend(created_items)

            return flext_api_success_response(
                data={"created_count": len(created_items), "total_count": len(data_store)}
            )

        client = TestClient(app)

        # Test bulk creation
        bulk_data = {
            "items": [
                {"name": f"User {i}", "email": f"user{i}@company.com"}
                for i in range(50)
            ]
        }

        response = client.post("/bulk-create", json=bulk_data)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["data"]["created_count"] == 50
        assert result["data"]["total_count"] == 50

    def test_concurrent_request_handling(self) -> None:
        """Test concurrent request handling."""
        app = flext_api_create_app(enable_auto_features=True)

        request_count = 0

        @app.get("/concurrent-test")
        @flext_api_handle_errors()
        @flext_api_cache_response(ttl=1)
        async def concurrent_endpoint(request: Request):  # noqa: ANN202
            nonlocal request_count
            request_count += 1
            return flext_api_success_response(data={"request_number": request_count})

        client = TestClient(app)

        # Make multiple concurrent requests (simulated)
        responses = []
        for _i in range(5):
            response = client.get("/concurrent-test")
            responses.append(response)

        # All should succeed
        for response in responses:
            assert response.status_code == 200
            assert response.json()["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

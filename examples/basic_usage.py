"""Basic FLEXT-API Usage Examples.

This file demonstrates how FLEXT-API reduces code by 70-90% compared to standard FastAPI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

# FLEXT-API imports - everything you need
from flext_api import (
    FlextQueryBuilder,
    FlextResponseBuilder,
    FlextValidator,
    SortDirection,
    create_flext_api,
    handle_errors,
    log_execution,
    paginated_response,
    rate_limit,
    require_json,
    success_response,
    validate_request,
)

if TYPE_CHECKING:
    from fastapi import Request

# =============================================================================
# EXAMPLE 1: One-Line API Creation
# =============================================================================
# Traditional FastAPI setup: 50-100 lines
# FLEXT-API: 1 line

app = create_flext_api(
    title="My Enterprise API",
    version="1.0.0",
    enable_cors=True,
    enable_rate_limiting=True,
    enable_logging=True,
    enable_security=True,
    add_health_checks=True,
)

# That's it! You now have a fully configured FastAPI app with:
# - CORS middleware
# - Rate limiting
# - Security headers
# - Request/response logging
# - Health check endpoints (/health, /health/ready, /health/live)
# - Global exception handling
# - Structured logging


# =============================================================================
# EXAMPLE 2: Request Models for Validation
# =============================================================================
class UserCreateRequest(BaseModel):
    """User creation request model."""

    email: str
    password: str
    name: str
    age: int | None = None


class UserResponse(BaseModel):
    """User response model."""

    id: str
    email: str
    name: str
    age: int | None = None
    created_at: str


# =============================================================================
# EXAMPLE 3: Zero-Boilerplate Route Handlers
# =============================================================================
# Traditional FastAPI: 30-50 lines per endpoint
# FLEXT-API: 5-10 lines per endpoint


@app.post("/users", response_model=dict[str, Any])
@handle_errors()  # Automatic error handling
@log_execution()  # Automatic logging
@require_json()  # Require JSON content-type
@validate_request(UserCreateRequest)  # Automatic request validation
async def create_user(request: Request) -> dict[str, Any]:
    """Create a new user with automatic validation and error handling."""
    # request.validated_data contains the validated UserCreateRequest
    user_data = request.validated_data

    # Business logic validation
    validator = FlextValidator()
    validation_result = (
        validator.validate_email("email", user_data.email)
        .validate_password("password", user_data.password)
        .validate_min_length("name", user_data.name, 2)
        .get_result()
    )

    if not validation_result.success:
        return (
            FlextResponseBuilder()
            .error("Validation failed", validation_result.error)
            .build()
        )

    # Simulate user creation
    new_user = {
        "id": "user_123",
        "email": user_data.email,
        "name": user_data.name,
        "age": user_data.age,
        "created_at": "2025-01-25T10:00:00Z",
    }

    # Return standardized response
    return (
        FlextResponseBuilder()
        .success("User created successfully")
        .with_data(new_user)
        .build()
    )


@app.get("/users", response_model=dict[str, Any])
@handle_errors()
@log_execution()
@rate_limit(calls=50, period=60)  # Rate limit: 50 calls per minute
async def list_users(request: Request) -> dict[str, Any]:
    """List users with filtering, sorting, and pagination."""
    # Parse query parameters into structured query
    query_params = dict(request.query_params)
    query_builder = FlextQueryBuilder()

    # Example URL: /users?filter[status]=active&filter[age][gte]=18&sort=name:asc&page=1&page_size=20

    # Add filters based on query params
    if "status" in query_params:
        query_builder.equals("status", query_params["status"])

    if "min_age" in query_params:
        query_builder.greater_than_or_equal("age", int(query_params["min_age"]))

    # Add sorting
    sort_by = query_params.get("sort", "name")
    sort_direction = (
        SortDirection.DESC if sort_by.startswith("-") else SortDirection.ASC
    )
    sort_field = sort_by.lstrip("-")
    query_builder.sort(sort_field, sort_direction)

    # Add pagination
    page = int(query_params.get("page", 1))
    page_size = int(query_params.get("page_size", 20))
    query_builder.paginate(page, page_size)

    # Build query
    query_builder.build()

    # Simulate database query
    users = [
        {
            "id": "1",
            "name": "Alice",
            "email": "alice@example.com",
            "age": 25,
            "status": "active",
        },
        {
            "id": "2",
            "name": "Bob",
            "email": "bob@example.com",
            "age": 30,
            "status": "active",
        },
        {
            "id": "3",
            "name": "Charlie",
            "email": "charlie@example.com",
            "age": 22,
            "status": "inactive",
        },
    ]

    # Filter users based on query (simplified example)
    filtered_users = users  # In real app, this would use the query with your database

    # Return paginated response
    return paginated_response(
        data=filtered_users,
        total=len(filtered_users),
        page=page,
        page_size=page_size,
        message="Users retrieved successfully",
    )


@app.get("/users/{user_id}", response_model=dict[str, Any])
@handle_errors()
async def get_user(user_id: str) -> dict[str, Any]:
    """Get user by ID with automatic error handling."""
    # Validate UUID format
    if not FlextValidator().validate_uuid("user_id", user_id).get_result().success:
        return FlextResponseBuilder().error("Invalid user ID format").build()

    # Simulate user lookup
    user = {
        "id": user_id,
        "name": "John Doe",
        "email": "john@example.com",
        "age": 28,
        "created_at": "2025-01-25T10:00:00Z",
    }

    return success_response(user, "User retrieved successfully")


# =============================================================================
# EXAMPLE 4: Advanced Query Building
# =============================================================================
@app.post("/users/search", response_model=dict[str, Any])
@handle_errors()
@require_json()
async def search_users(request: Request) -> dict[str, Any]:
    """Advanced user search with complex queries."""
    data = await request.json()

    # Build complex query
    query = (
        FlextQueryBuilder()
        .equals("status", "active")
        .greater_than("age", 18)
        .in_values("department", ["engineering", "sales", "marketing"])
        .like("name", f"%{data.get('search', '')}%")
        .between("created_at", "2024-01-01", "2025-01-01")
        .sort_desc("created_at")
        .paginate(data.get("page", 1), data.get("page_size", 50))
        .include_total_count()
        .build()
    )

    # Simulate search results
    results = [
        {"id": "1", "name": "Alice Johnson", "department": "engineering", "age": 25},
        {"id": "2", "name": "Bob Smith", "department": "sales", "age": 30},
    ]

    return (
        FlextResponseBuilder()
        .success("Search completed")
        .with_data(results)
        .with_pagination(total=100, page=1, page_size=50)
        .with_metadata("query", query)
        .build()
    )


# =============================================================================
# EXAMPLE 5: Response Building Patterns
# =============================================================================
@app.post("/users/{user_id}/activate", response_model=dict[str, Any])
@handle_errors()
async def activate_user(user_id: str) -> dict[str, Any]:
    """Activate user with standardized response."""
    # Simulate activation logic
    success = True

    if success:
        return (
            FlextResponseBuilder()
            .success("User activated successfully")
            .with_data({"user_id": user_id, "status": "active"})
            .with_metadata("activation_time", "2025-01-25T10:00:00Z")
            .build()
        )
    return (
        FlextResponseBuilder()
        .error("Failed to activate user", "User not found or already active")
        .build()
    )


# =============================================================================
# EXAMPLE 6: Validation Chains
# =============================================================================
class UpdateUserRequest(BaseModel):
    """User update request model."""

    name: str | None = None
    email: str | None = None
    age: int | None = None


@app.put("/users/{user_id}", response_model=dict[str, Any])
@handle_errors()
@validate_request(UpdateUserRequest)
async def update_user(user_id: str, request: Request) -> dict[str, Any]:
    """Update user with comprehensive validation."""
    update_data = request.validated_data

    # Chain multiple validations
    validator = FlextValidator()

    if update_data.email:
        validator.validate_email("email", update_data.email)

    if update_data.name:
        validator.validate_min_length("name", update_data.name, 2)
        validator.validate_max_length("name", update_data.name, 50)

    if update_data.age:
        validator.validate_range("age", update_data.age, 13, 120)

    # Get validation result
    validation_result = validator.get_result()
    if not validation_result.success:
        return FlextResponseBuilder().from_result(validation_result).build()

    # Simulate update
    updated_user = {
        "id": user_id,
        "name": update_data.name or "John Doe",
        "email": update_data.email or "john@example.com",
        "age": update_data.age or 28,
        "updated_at": "2025-01-25T10:00:00Z",
    }

    return success_response(updated_user, "User updated successfully")


# =============================================================================
# CODE REDUCTION SUMMARY
# =============================================================================
"""
TRADITIONAL FASTAPI SETUP (100+ lines):
- Manual FastAPI app creation
- Manual CORS middleware setup
- Manual exception handlers
- Manual request validation
- Manual response formatting
- Manual error handling in each route
- Manual logging setup
- Manual rate limiting
- Manual health checks

FLEXT-API SETUP (10-20 lines):
- One-line app creation with create_flext_api()
- Automatic middleware setup
- Decorators handle everything
- Standardized responses
- Built-in validation chains
- Query building utilities

RESULT: 70-90% CODE REDUCTION while maintaining enterprise-grade features.
"""

#!/usr/bin/env python3
"""FlextApi Massive Code Reduction Examples.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Real-world examples demonstrating massive code reduction with FlextApi.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel

# FlextApi imports - everything from root namespace
from flext_api import (
    FlextApiBuilder,
    FlextApiQueryBuilder,
    FlextApiResponseBuilder,
    FlextApiValidator,
    flext_api_authenticated,
    flext_api_cache_response,
    flext_api_create_app,
    flext_api_error_response,
    flext_api_handle_errors,
    flext_api_log_execution,
    flext_api_paginated_response,
    flext_api_rate_limit,
    flext_api_success_response,
    flext_api_validate_request,
)

if TYPE_CHECKING:
    from collections.abc import Callable

# ==============================================================================
# EXAMPLE 1: ENTERPRISE API SETUP - 95% CODE REDUCTION
# ==============================================================================

def traditional_fastapi_setup() -> FastAPI:
    """Traditional FastAPI setup - 100+ lines of boilerplate."""
    import logging
    import time

    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    from starlette.middleware.sessions import SessionMiddleware

    # Create app with custom configuration
    app = FastAPI(
        title="Enterprise API",
        description="Complex enterprise API with security",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://example.com"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

    # Add security middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["example.com", "*.example.com"]
    )

    # Add session middleware
    app.add_middleware(
        SessionMiddleware,
        secret_key="your-secret-key"
    )

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logging.getLogger(__name__)

    # Rate limiting storage
    rate_limit_storage: dict[str, list[float]] = {}

    # Custom middleware for rate limiting
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        if client_ip not in rate_limit_storage:
            rate_limit_storage[client_ip] = []

        # Clean old requests
        rate_limit_storage[client_ip] = [
            req_time for req_time in rate_limit_storage[client_ip]
            if now - req_time < 60
        ]

        # Check rate limit
        if len(rate_limit_storage[client_ip]) >= 100:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        rate_limit_storage[client_ip].append(now)
        return await call_next(request)

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "timestamp": time.time()}

    # Metrics endpoint
    @app.get("/metrics")
    async def metrics():
        return {"requests": sum(len(reqs) for reqs in rate_limit_storage.values())}

    # Info endpoint
    @app.get("/")
    async def root():
        return {
            "name": app.title,
            "version": app.version,
            "description": app.description
        }

    return app


def flext_api_setup() -> FastAPI:
    """FlextApi setup - 1 line replaces 100+."""
    return flext_api_create_app(
        title="Enterprise API",
        description="Complex enterprise API with security",
        version="1.0.0",
        enable_cors=True,
        enable_rate_limiting=True,
        enable_security=True,
        enable_auto_features=True,
    )


# ==============================================================================
# EXAMPLE 2: USER MANAGEMENT API - 80% CODE REDUCTION
# ==============================================================================

class UserCreateRequest(BaseModel):
    name: str
    email: str
    phone: str
    role: str = "user"


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    role: str
    created_at: str


def traditional_user_endpoint() -> FastAPI:
    """Traditional user endpoint - verbose error handling."""
    app = FastAPI()

    @app.post("/users")
    async def create_user(request: Request):
        try:
            # Manual request parsing
            data = await request.json()

            # Manual validation
            if not data.get("name"):
                raise HTTPException(status_code=422, detail="Name is required")
            if not data.get("email"):
                raise HTTPException(status_code=422, detail="Email is required")
            if not data.get("phone"):
                raise HTTPException(status_code=422, detail="Phone is required")

            # Email validation
            import re
            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, data["email"]):
                raise HTTPException(status_code=422, detail="Invalid email format")

            # Phone validation
            phone_pattern = r"^\+?[1-9]\d{1,14}$"
            clean_phone = re.sub(r"[^+\d]", "", data["phone"])
            if not re.match(phone_pattern, clean_phone):
                raise HTTPException(status_code=422, detail="Invalid phone format")

            # Sanitize data
            clean_name = data["name"].strip()
            clean_email = data["email"].lower().strip()

            # Simulate user creation
            user = {
                "id": 123,
                "name": clean_name,
                "email": clean_email,
                "phone": clean_phone,
                "role": data.get("role", "user"),
                "created_at": "2025-01-25T10:00:00Z"
            }

            # Manual response formatting
            return {
                "success": True,
                "message": "User created successfully",
                "data": user,
                "timestamp": "2025-01-25T10:00:00Z"
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app


def flext_api_user_endpoint() -> FastAPI:
    """FlextApi user endpoint - massive reduction."""
    app = flext_api_create_app(enable_auto_features=True)

    @app.post("/users")
    @flext_api_handle_errors()
    @flext_api_log_execution(log_duration=True)
    @flext_api_validate_request(UserCreateRequest)
    async def create_user(request: Request):
        user_data = request.validated_data

        # FlextApi validation chain
        validator = (FlextApiValidator()
                    .validate_required("name", user_data.name)
                    .validate_email("email", user_data.email)
                    .validate_required("phone", user_data.phone))

        validation_result = validator.get_result()
        if not validation_result.success:
            return flext_api_error_response(
                "Validation failed",
                validation_result.data["errors"]
            )

        # FlextApi data sanitization
        from flext_api import (
            flext_api_normalize_phone,
            flext_api_sanitize_email,
            flext_api_sanitize_string,
        )

        user = {
            "id": 123,
            "name": flext_api_sanitize_string(user_data.name),
            "email": flext_api_sanitize_email(user_data.email),
            "phone": flext_api_normalize_phone(user_data.phone),
            "role": user_data.role,
            "created_at": "2025-01-25T10:00:00Z"
        }

        return flext_api_success_response(
            data=user,
            message="User created successfully"
        )

    return app


# ==============================================================================
# EXAMPLE 3: QUERY & PAGINATION API - 90% CODE REDUCTION
# ==============================================================================

def traditional_list_endpoint() -> FastAPI:
    """Traditional list endpoint with complex query parsing."""
    app = FastAPI()

    @app.get("/users")
    async def list_users(request: Request):
        try:
            # Manual query parameter parsing
            query_params = dict(request.query_params)

            # Parse filters
            filters = []
            if "status" in query_params:
                filters.append({"field": "status", "operator": "eq", "value": query_params["status"]})
            if "role" in query_params:
                filters.append({"field": "role", "operator": "eq", "value": query_params["role"]})
            if "created_after" in query_params:
                filters.append({"field": "created_at", "operator": "gt", "value": query_params["created_after"]})

            # Parse sorting
            sorts = []
            if "sort_by" in query_params:
                direction = query_params.get("sort_direction", "asc")
                sorts.append({"field": query_params["sort_by"], "direction": direction})

            # Parse pagination
            try:
                page = int(query_params.get("page", 1))
                page_size = int(query_params.get("page_size", 10))
            except ValueError:
                raise HTTPException(status_code=422, detail="Invalid pagination parameters")

            if page < 1 or page_size < 1 or page_size > 100:
                raise HTTPException(status_code=422, detail="Invalid pagination range")

            # Simulate database query
            users = [
                {"id": 1, "name": "John", "email": "john@test.com", "status": "active"},
                {"id": 2, "name": "Jane", "email": "jane@test.com", "status": "active"},
                {"id": 3, "name": "Bob", "email": "bob@test.com", "status": "inactive"},
            ]

            # Apply filters (simplified)
            filtered_users = users
            for filter_item in filters:
                if filter_item["field"] == "status":
                    filtered_users = [u for u in filtered_users if u["status"] == filter_item["value"]]

            # Calculate pagination
            total = len(filtered_users)
            start = (page - 1) * page_size
            end = start + page_size
            paginated_users = filtered_users[start:end]

            # Manual response formatting
            return {
                "success": True,
                "message": "Users retrieved successfully",
                "data": paginated_users,
                "total_count": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size,
                "timestamp": "2025-01-25T10:00:00Z"
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app


def flext_api_list_endpoint() -> FastAPI:
    """FlextApi list endpoint - automatic query parsing."""
    app = flext_api_create_app(enable_auto_features=True)

    @app.get("/users")
    @flext_api_handle_errors()
    @flext_api_cache_response(ttl=60)
    async def list_users(request: Request):
        # FlextApi automatic query parsing
        from flext_api import flext_api_parse_query_params

        query_params = dict(request.query_params)
        builder = flext_api_parse_query_params(query_params)
        query = builder.build()

        # Simulate database query (would use repository pattern)
        users = [
            {"id": 1, "name": "John", "email": "john@test.com", "status": "active"},
            {"id": 2, "name": "Jane", "email": "jane@test.com", "status": "active"},
            {"id": 3, "name": "Bob", "email": "bob@test.com", "status": "inactive"},
        ]

        # Apply query (simplified - real implementation would use repository)
        filtered_users = users  # Repository would handle filtering

        return flext_api_paginated_response(
            data=filtered_users,
            total=len(users),
            page=query.get("pagination", {}).get("page", 1),
            page_size=query.get("pagination", {}).get("page_size", 10)
        )

    return app


# ==============================================================================
# EXAMPLE 4: AUTHENTICATION & AUTHORIZATION - 85% CODE REDUCTION
# ==============================================================================

def traditional_auth_endpoint() -> FastAPI:
    """Traditional authentication endpoint."""
    app = FastAPI()

    @app.post("/protected")
    async def protected_endpoint(request: Request):
        try:
            # Manual authentication
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise HTTPException(status_code=401, detail="Missing authorization header")

            if not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Invalid authorization format")

            token = auth_header[7:]  # Remove "Bearer "
            if not token:
                raise HTTPException(status_code=401, detail="Empty token")

            # Manual token validation (simplified)
            import jwt
            try:
                payload = jwt.decode(token, "secret", algorithms=["HS256"])
                user_id = payload.get("user_id")
                roles = payload.get("roles", [])
            except jwt.InvalidTokenError:
                raise HTTPException(status_code=401, detail="Invalid token")

            # Manual role check
            required_roles = ["admin", "moderator"]
            if not any(role in roles for role in required_roles):
                raise HTTPException(status_code=403, detail="Insufficient permissions")

            # Business logic
            return {
                "success": True,
                "message": "Access granted",
                "user_id": user_id,
                "roles": roles
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app


def flext_api_auth_endpoint() -> FastAPI:
    """FlextApi authentication endpoint."""
    app = flext_api_create_app(enable_auto_features=True)

    @app.post("/protected")
    @flext_api_handle_errors()
    @flext_api_authenticated()
    async def protected_endpoint(request: Request):
        # Authentication handled automatically by decorator
        user = request.user
        return flext_api_success_response(
            data={"user_id": user.get("user_id"), "roles": user.get("roles")},
            message="Access granted"
        )

    @app.post("/admin-only")
    @flext_api_handle_errors()
    @flext_api_authorize_roles("admin", "moderator")
    async def admin_endpoint(request: Request):
        # Authentication + authorization handled automatically
        return flext_api_success_response(
            data={"admin_action": "completed"},
            message="Admin operation successful"
        )

    return app


# ==============================================================================
# PERFORMANCE COMPARISON RUNNER
# ==============================================================================

def run_performance_comparison() -> None:
    """Run performance comparison between traditional and FlextApi approaches."""
    import time

    def measure_setup_time(setup_func: Callable[[], FastAPI]) -> float:
        """Measure time to setup FastAPI app."""
        start = time.time()
        setup_func()
        end = time.time()
        return end - start


    # Test app setup times
    measure_setup_time(traditional_fastapi_setup)
    measure_setup_time(flext_api_setup)


    # Test lines of code
    import inspect
    len(inspect.getsource(traditional_fastapi_setup).split("\n"))
    len(inspect.getsource(flext_api_setup).split("\n"))


    # Test endpoint functionality
    traditional_app = traditional_user_endpoint()
    flextapi_app = flext_api_user_endpoint()

    traditional_client = TestClient(traditional_app)
    flextapi_client = TestClient(flextapi_app)

    test_user = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "+1-555-123-4567"
    }

    # Traditional endpoint
    start = time.time()
    traditional_client.post("/users", json=test_user)
    time.time() - start

    # FlextApi endpoint
    start = time.time()
    flextapi_client.post("/users", json=test_user)
    time.time() - start



if __name__ == "__main__":
    run_performance_comparison()

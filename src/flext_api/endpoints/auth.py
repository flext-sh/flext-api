"""Authentication endpoints for FLEXT API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the authentication endpoints for the FLEXT API.
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.security import HTTPBearer

from flext_api.base import FlextAPIResponse
from flext_api.models.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    UserAPI,
)

auth_router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
security = HTTPBearer()


@auth_router.post("/login")
async def login(login_data: LoginRequest, request: Request) -> LoginResponse:
    """Login endpoint.

    Args:
        login_data: LoginRequest,
        request: Request,

    Returns:
        LoginResponse

    """
    from flext_api.dependencies import get_flext_auth_service

    auth_service = get_flext_auth_service()

    # Use real authentication service
    auth_result = await auth_service.authenticate_user(
        username=login_data.username, password=login_data.password
    )

    if not auth_result.success:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT token for authenticated user
    token = auth_service.generate_token(
        {"username": login_data.username, "roles": ["user"]}
    )

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        expires_in=3600,
        user=UserAPI(
            username=login_data.username,
            roles=["user"],
            is_active=True,
            is_REDACTED_LDAP_BIND_PASSWORD=False,
        ),
    )


@auth_router.post("/register")
async def register(register_data: RegisterRequest) -> RegisterResponse:
    """Register endpoint.

    Args:
        register_data: RegisterRequest,

    Returns:
        RegisterResponse

    """
    # Implementation placeholder - will be connected to actual auth service
    return RegisterResponse(
        user=UserAPI(
            username=register_data.username,
            roles=register_data.roles or ["user"],
            is_active=True,
            is_REDACTED_LDAP_BIND_PASSWORD=False,
        ),
        created=True,
    )


@auth_router.post("/logout")
async def logout(_request: Request) -> FlextAPIResponse[dict[str, str]]:
    """Logout endpoint.

    Args:
        _request: Request,

    Returns:
        FlextAPIResponse

    """
    return FlextAPIResponse.success({"message": "Logged out successfully"})


@auth_router.get("/profile")
async def get_profile(_request: Request) -> UserAPI:
    """Get profile endpoint.

    Args:
        _request: Request,

    Returns:
        UserAPI

    """
    # Implementation placeholder - will extract from JWT token
    return UserAPI(
        username="current_user",
        roles=["user"],
        is_active=True,
        is_REDACTED_LDAP_BIND_PASSWORD=False,
    )

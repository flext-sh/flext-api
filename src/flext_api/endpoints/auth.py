"""Authentication endpoints for FLEXT API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the authentication endpoints for the FLEXT API.
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.security import HTTPBearer

from flext_api.models.auth import (
    APIResponse,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    UserAPI,
)

auth_router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


@auth_router.post("/login")
async def login(login_data: LoginRequest) -> LoginResponse:
    """Login endpoint.

    Args:
        login_data: LoginRequest

    Returns:
        LoginResponse

    """
    # Implementation placeholder - will be connected to actual auth service
    placeholder_token = "placeholder_token"
    bearer_type = "bearer"
    return LoginResponse(
        access_token=placeholder_token,
        token_type=bearer_type,
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
        register_data: RegisterRequest

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
async def logout(_request: Request) -> APIResponse:
    """Logout endpoint.

    Args:
        _request: Request

    Returns:
        APIResponse

    """
    return APIResponse()


@auth_router.get("/profile")
async def get_profile(_request: Request) -> UserAPI:
    """Get profile endpoint.

    Args:
        _request: Request

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

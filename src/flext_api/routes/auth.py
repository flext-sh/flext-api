"""Authentication routes for FLEXT API using clean architecture.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides REST endpoints for authentication using
the application services and clean architecture patterns.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

# Use centralized logger from flext-observability - ELIMINATE DUPLICATION
from flext_observability.logging import get_logger

from flext_api.dependencies import get_auth_service, get_current_user
from flext_api.models.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    UserAPI,
)

if TYPE_CHECKING:
    from flext_api.application.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()
logger = get_logger(__name__)


@router.post("/register")
async def register_user(
    request: RegisterRequest,
    _auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> RegisterResponse:
    """Register a new user.

    Args:
        request: The registration request.
        auth_service: The authentication service.

    Returns:
        The registration response.

    """
    # For development, just return success
    # In production, this would create a real user
    logger.info("Registration attempt for user: %s", request.username)

    # Create user object
    user = UserAPI(
        username=request.username,
        roles=request.roles,
        is_active=True,
        is_admin="admin" in request.roles,
    )

    return RegisterResponse(
        user=user,
        created=True,
    )


@router.post("/login")
async def login_user(
    request: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> LoginResponse:
    """Login a user.

    Args:
        request: The login request.
        auth_service: The authentication service.

    Raises:
        HTTPException: If login fails.

    Returns:
        The login response.

    """
    try:
        # Use username for login (request has username field, not email)
        username = request.username

        result = await auth_service.login(username, request.password)

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.error or "Invalid credentials",
            )

        token_data = result.data

        # Type guard: ensure token_data is not None
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login failed: No token data returned",
            )

        # Create user object
        user = UserAPI(
            username=token_data["username"],
            roles=token_data.get("roles", ["user"]),
            is_active=True,
            is_admin="admin" in token_data.get("roles", []),
        )

        return LoginResponse(
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token", token_data["access_token"]),
            token_type=token_data.get("token_type", "bearer"),
            expires_in=token_data.get("expires_in", 3600),
            user=user,
            session_id=f"session-{hash(token_data['username'])}",
            permissions=(
                ["read", "write"]
                if "admin" in token_data.get("roles", [])
                else ["read"]
            ),
            roles=token_data.get("roles", ["user"]),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Login failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed",
        ) from e


@router.post("/refresh")
async def refresh_tokens(
    refresh_token: str,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> LoginResponse:
    """Refresh authentication tokens.

    Args:
        refresh_token: The refresh token.
        auth_service: The authentication service.

    Raises:
        HTTPException: If token refresh fails.

    Returns:
        The login response with new tokens.

    """
    try:
        # For simplicity, validate the refresh token as a regular token
        result = await auth_service.validate_token(refresh_token)

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        user = result.data

        # Type guard: ensure user data is not None
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token: No user data",
            )

        # Create new token using existing login method
        token_result = await auth_service.login(user.username, "refresh")

        if not token_result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create new token",
            )

        token_data = token_result.data

        # Type guard: ensure token_data is not None
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create new token: No token data returned",
            )

        # Create user object
        user_obj = UserAPI(
            username=user.username,
            roles=getattr(user, "roles", ["user"]),
            is_active=True,
            is_admin=getattr(user, "is_admin", False),
        )

        return LoginResponse(
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token", token_data["access_token"]),
            token_type=token_data.get("token_type", "bearer"),
            expires_in=token_data.get("expires_in", 3600),
            user=user_obj,
            session_id=f"session-{hash(user.username)}",
            permissions=["read", "write"] if user_obj.is_admin else ["read"],
            roles=user_obj.roles,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed",
        ) from e


@router.post("/logout")
async def logout_user(
    _token: Annotated[str, Depends(security)],
    _auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> dict[str, str]:
    """Logout a user.

    Args:
        token: The authentication token.
        auth_service: The authentication service.

    Returns:
        The logout confirmation.

    """
    # For simplicity, just return success
    # In production, would invalidate the token
    logger.info("User logged out")
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user_info(
    current_user: Annotated[dict[str, object], Depends(get_current_user)],
) -> dict[str, object]:
    """Get current user information.

    Args:
        current_user: The current authenticated user.

    Returns:
        The current user information.

    """
    return current_user

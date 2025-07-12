"""Authentication routes for FLEXT API using clean architecture.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides REST endpoints for authentication using
the application services and clean architecture patterns.
"""

from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import HTTPBearer

from flext_api.application.services.auth_service import AuthService
from flext_api.dependencies import get_auth_service
from flext_api.dependencies import get_current_user
from flext_api.models.auth import LoginRequest
from flext_api.models.auth import LoginResponse
from flext_api.models.auth import RegisterRequest
from flext_api.models.auth import RegisterResponse

# Use centralized logger from flext-observability - ELIMINATE DUPLICATION
from flext_observability.logging import get_logger

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()
logger = get_logger(__name__)


@router.post("/register")
async def register_user(
    request: RegisterRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
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
    logger.info(f"Registration attempt for user: {request.username}")

    return RegisterResponse(
        message="User registered successfully",
        user_id="dev-user-id",
        username=request.username,
        email=request.email,
        role=request.role or "viewer",
        created_at="2025-07-09T00:00:00Z",
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
        # Use email as username for login
        username = (
            request.email.split("@")[0] if "@" in request.email else request.email
        )

        result = await auth_service.login(username, request.password)

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.error or "Invalid credentials",
            )

        token_data = result.unwrap()

        return LoginResponse(
            access_token=token_data["access_token"],
            refresh_token=token_data["access_token"],  # Same as access for simplicity
            token_type=token_data["token_type"],
            expires_in=token_data["expires_in"],
            user={
                "username": token_data["username"],
                "email": f"{token_data['username']}@flext.local",
            },
            session_id=f"session-{hash(token_data['username'])}",
            permissions=(
                ["read", "write"] if "admin" in token_data["roles"] else ["read"]
            ),
            roles=token_data["roles"],
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

        user = result.unwrap()

        # Create new token
        token_result = await auth_service.create_token(user.username)

        if not token_result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create new token",
            )

        token_data = token_result.unwrap()

        return LoginResponse(
            access_token=token_data["access_token"],
            refresh_token=token_data["access_token"],
            token_type=token_data["token_type"],
            expires_in=token_data["expires_in"],
            user={"username": user.username, "email": user.email},
            session_id=f"session-{hash(user.username)}",
            permissions=["read", "write"] if user.is_admin else ["read"],
            roles=user.roles,
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
    token: Annotated[str, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
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
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    """Get current user information.

    Args:
        current_user: The current authenticated user.

    Returns:
        The current user information.

    """
    return current_user

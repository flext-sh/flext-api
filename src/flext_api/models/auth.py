"""Authentication models for FLEXT API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides Pydantic models for authentication.
"""

from __future__ import annotations

from flext_core import APIRequest, APIResponse, Field

__all__ = [
    "APIResponse",  # Re-export from flext_core
    "LoginRequest",
    "LoginResponse",
    "LogoutRequest",
    "RefreshTokenRequest",
    "RegisterRequest",
    "RegisterResponse",
    "SessionListResponse",
    "SessionResponse",
    "UserAPI",
]


class UserAPI(APIResponse):
    """API User model for authentication with role-based access control.

    Represents an authenticated user with roles and authorization capabilities
    for secure API access and resource management.

    Attributes
    ----------
        username: User identification string.
        roles: List of user roles for authorization.
        is_active: Whether the user account is active.
        is_admin: Whether the user has administrative privileges.

    Methods
    -------
        has_role(): Check if user has a specific role.
        is_authorized(): Check if user is authorized for required roles.

    Examples
    --------
        Basic usage of the class:

        ```python
        user = UserAPI(username="admin", roles=["admin"])
        result = user.is_authorized(["admin"])
        ```

    """

    username: str = Field(..., description="Username")
    roles: list[str] = Field(default_factory=list, description="User roles")
    is_active: bool = Field(default=True, description="Whether user is active")
    is_admin: bool = Field(default=False, description="Whether user is admin")

    def has_role(self, role: str) -> bool:
        """Check if user has specific role."""
        return role in self.roles or "admin" in self.roles

    def is_authorized(self, required_roles: list[str] | None = None) -> bool:
        """Check if user is authorized for required roles."""
        if not self.is_active:
            return False

        if self.is_admin:
            return True

        if not required_roles:
            return True

        return any(self.has_role(role) for role in required_roles)


class LoginRequest(APIRequest):
    """Request model for user login."""

    username: str = Field(..., description="Username or email")
    password: str = Field(..., min_length=1, description="User password")
    device_info: dict[str, str] | None = Field(
        default=None,
        description="Optional device information",
    )


class LoginResponse(APIResponse):
    """Response model for user login."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str | None = Field(default=None, description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    user: UserAPI = Field(..., description="User information")
    session_id: str | None = Field(default=None, description="Session identifier")
    permissions: list[str] = Field(
        default_factory=list,
        description="User permissions",
    )
    roles: list[str] = Field(default_factory=list, description="User roles")


class RegisterRequest(APIRequest):
    """Request model for user registration."""

    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password")
    roles: list[str] = Field(default_factory=lambda: ["user"], description="User roles")


class RegisterResponse(APIResponse):
    """Response model for user registration."""

    user: UserAPI = Field(..., description="Created user information")
    created: bool = Field(default=True, description="Whether user was created")


class TokenRefreshRequest(APIRequest):
    """Request model for token refresh."""

    refresh_token: str = Field(..., description="Refresh token")


class TokenRefreshResponse(APIResponse):
    """Response model for token refresh."""

    access_token: str = Field(..., description="New access token")
    refresh_token: str = Field(..., description="New refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")


class RefreshTokenRequest(APIRequest):
    """Request model for token refresh."""

    refresh_token: str = Field(..., description="Refresh token")


class LogoutRequest(APIRequest):
    """Request model for user logout."""

    session_id: str | None = Field(default=None, description="Session to terminate")
    all_sessions: bool = Field(default=False, description="Terminate all sessions")


class UserProfileResponse(APIResponse):
    """Response model for user profile."""

    user: UserAPI = Field(..., description="User information")
    permissions: list[str] = Field(
        default_factory=list,
        description="User permissions",
    )
    last_login: str | None = Field(default=None, description="Last login timestamp")
    session_count: int = Field(default=0, description="Active session count")


class SessionResponse(APIResponse):
    """Response model for session information."""

    session_id: str = Field(..., description="Session identifier")
    user_id: str = Field(..., description="User identifier")
    ip_address: str | None = Field(default=None, description="Client IP address")
    user_agent: str | None = Field(default=None, description="User agent string")
    device_info: dict[str, str] = Field(
        default_factory=dict,
        description="Device information",
    )
    created_at: str = Field(..., description="Session creation timestamp")
    last_accessed: str = Field(..., description="Last access timestamp")
    expires_at: str = Field(..., description="Session expiration timestamp")
    is_current: bool = Field(
        default=False,
        description="Whether this is the current session",
    )
    roles: list[str] = Field(default_factory=list, description="User roles")
    permissions: list[str] = Field(default_factory=list, description="User permissions")


class SessionListResponse(APIResponse):
    """Response model for session list."""

    sessions: list[SessionResponse] = Field(
        default_factory=list,
        description="List of sessions",
    )
    total_count: int = Field(default=0, description="Total number of sessions")

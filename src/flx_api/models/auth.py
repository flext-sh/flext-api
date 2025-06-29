"""Authentication models for FLX API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class UserAPI(BaseModel):
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

        if not required_roles:
            return True

        return any(self.has_role(role) for role in required_roles)


class LoginRequest(BaseModel):
    """Login request model for user authentication.

    Captures user credentials for authentication processing with validation
    and security for secure login operations.

    Attributes
    ----------
        email: User email for authentication.
        password: User password for authentication.
        device_info: Optional device information for tracking.

    Examples
    --------
        Basic usage of the class:

        ```python
        request = LoginRequest(email="user@example.com", password="your_secure_password")
        ```

    """

    email: str = Field(..., description="User email address")
    password: str = Field(..., description="Password")
    device_info: dict[str, str] | None = Field(
        default=None,
        description="Device information",
    )


class LoginResponse(BaseModel):
    """Login response model containing authentication tokens and user information.

    Returns JWT authentication tokens and user profile information after
    successful login for secure API access.

    Attributes
    ----------
        access_token: JWT access token for API authentication.
        refresh_token: JWT refresh token for token renewal.
        token_type: Type of authentication token (default: bearer).
        expires_in: Token expiration time in seconds.
        user: User information and profile data.
        session_id: Session identifier for tracking.
        permissions: User permissions for authorization.
        roles: User roles for RBAC.

    Examples
    --------
        Basic usage of the class:

        ```python
        constants = get_domain_constants()
        response = LoginResponse(
            access_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.example",
            refresh_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.refresh",
            expires_in=constants.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_instance,
            session_id="session-123",
            permissions=["read", "write"],
            roles=["user"]
        )
        ```

    """

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    user: UserAPI | dict[str, str] = Field(..., description="User information")
    session_id: str = Field(..., description="Session identifier")
    permissions: list[str] = Field(default_factory=list, description="User permissions")
    roles: list[str] = Field(default_factory=list, description="User roles")


class TokenData(BaseModel):
    """Token payload data model for JWT authentication.

    Represents the decoded JWT token payload containing user identity and
    authorization information for request processing.

    Attributes
    ----------
        username: User identification from token payload.
        roles: List of user roles extracted from token.
        exp: Token expiration timestamp.

    Examples
    --------
        Basic usage of the class:

        ```python
        token_data = TokenData(
            username="user",
            roles=["admin"],
            exp=1234567890
        )
        ```

    """

    username: str = Field(..., description="Username")
    roles: list[str] = Field(default_factory=list, description="User roles")
    exp: int = Field(..., description="Expiration timestamp")


class RefreshTokenRequest(BaseModel):
    """Token refresh request model."""

    refresh_token: str = Field(..., description="JWT refresh token")


class LogoutRequest(BaseModel):
    """User logout request model."""

    session_id: str | None = Field(
        default=None,
        description="Specific session to terminate",
    )
    all_sessions: bool = Field(default=False, description="Terminate all user sessions")


class SessionResponse(BaseModel):
    """Session information response model."""

    session_id: str = Field(..., description="Session unique identifier")
    user_id: str = Field(..., description="User identifier")
    ip_address: str | None = Field(description="Client IP address")
    user_agent: str | None = Field(description="Client user agent")
    device_info: dict[str, str] = Field(
        default_factory=dict,
        description="Device information",
    )
    created_at: str = Field(..., description="Session creation timestamp")
    last_accessed: str = Field(..., description="Last access timestamp")
    expires_at: str = Field(..., description="Session expiration timestamp")
    is_current: bool = Field(..., description="Whether this is the current session")
    roles: list[str] = Field(
        default_factory=list,
        description="User roles in this session",
    )
    permissions: list[str] = Field(
        default_factory=list,
        description="Effective permissions",
    )


class SessionListResponse(BaseModel):
    """List of user sessions response model."""

    sessions: list[SessionResponse] = Field(..., description="List of user sessions")
    total_count: int = Field(..., description="Total number of sessions")


class RegisterRequest(BaseModel):
    """User registration request model with validation.

    Captures user registration data with validation for creating new
    user accounts with appropriate security and data validation.

    Attributes
    ----------
        username: Desired username for the new account.
        password: Secure password for account protection.
        email: Valid email address for account verification.
        role: Optional role to assign to user.

    Examples
    --------
        Basic usage of the class:

        ```python
        request = RegisterRequest(
            username="newuser",
            password="secure_password",
            email="user@example.com"
        )
        ```

    """

    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="Password")
    email: str = Field(..., description="Email address")
    role: str | None = Field(default=None, description="User role")


class RegisterResponse(BaseModel):
    """User registration response model with account creation confirmation.

    Returns confirmation of successful user account creation with
    basic user information for registration confirmation.

    Attributes
    ----------
        user_id: User unique identifier.
        username: Username.
        email: User email address.
        role: User role.
        created_at: Account creation timestamp.
        message: Confirmation message for successful registration.

    Examples
    --------
        Basic usage of the class:

        ```python
        response = RegisterResponse(
            user_id="123",
            username="newuser",
            email="user@example.com",
            role="user",
            created_at="2024-01-01T00: 00:00Z",
            message="User created successfully"
        )
        ```

    """

    user_id: str = Field(..., description="User unique identifier")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="User email address")
    role: str = Field(..., description="User role")
    created_at: str = Field(..., description="Account creation timestamp")
    message: str = Field(..., description="Registration confirmation message")

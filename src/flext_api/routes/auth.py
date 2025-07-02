"""Authentication routes for FLEXT API."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from flext_auth.service import (
    AuthenticationService,
    ServiceInMemoryRoleRepository,
    ServiceInMemoryUserRepository,
)

from flext_api.models.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


def get_auth_service() -> AuthenticationService:
    """Dependency to get authentication service."""
    user_repo = ServiceInMemoryUserRepository()
    role_repo = ServiceInMemoryRoleRepository()
    return AuthenticationService(user_repository=user_repo, role_repository=role_repo)


@router.post("/register", response_model=RegisterResponse)
async def register_user(
    request: RegisterRequest,
    auth_service: AuthenticationService = Depends(get_auth_service),
) -> RegisterResponse:
    """Register a new user."""
    try:
        user = await auth_service.register(
            username=request.username,
            email=request.email,
            password=request.password,
            roles=[request.role] if request.role else ["viewer"],
        )

        return RegisterResponse(
            message="User registered successfully",
            user_id=str(user.user_id),
            username=user.username,
            email=user.email,
            role=request.role or "viewer",
            created_at="2024-01-01T00:00:00Z",  # Would use actual timestamp in production
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=LoginResponse)
async def login_user(
    request: LoginRequest,
    auth_service: AuthenticationService = Depends(get_auth_service),
) -> LoginResponse:
    """Authenticate user and return tokens."""
    try:
        token_pair = await auth_service.authenticate(
            username_or_email=request.email,
            password=request.password,
            ip_address=None,  # Would be extracted from request in production
        )

        return LoginResponse(
            access_token=token_pair.access_token,
            refresh_token=token_pair.refresh_token,
            token_type="bearer",
            expires_in=3600,
            user={"username": "test_user", "email": request.email},
            session_id="session-123",
            permissions=["read", "write"],
            roles=["user"],
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_tokens(
    refresh_token: str,
    auth_service: AuthenticationService = Depends(get_auth_service),
) -> LoginResponse:
    """Refresh access token using refresh token."""
    try:
        token_pair = await auth_service.refresh_tokens(
            refresh_token=refresh_token, ip_address=None
        )

        return LoginResponse(
            access_token=token_pair.access_token,
            refresh_token=token_pair.refresh_token,
            token_type="bearer",
            expires_in=3600,
            user={"username": "refresh_user", "email": "refresh@example.com"},
            session_id="session-456",
            permissions=["read", "write"],
            roles=["user"],
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )


@router.post("/logout")
async def logout_user(
    token: str = Depends(security),
    auth_service: AuthenticationService = Depends(get_auth_service),
) -> dict[str, str]:
    """Logout user by revoking token."""
    try:
        await auth_service.revoke_token(token.credentials)
        return {"message": "Logged out successfully"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Logout failed"
        )

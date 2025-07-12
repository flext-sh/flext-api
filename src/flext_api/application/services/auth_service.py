"""Authentication application service using flext-core patterns.

This module provides the application service for authentication management,
implementing business logic using domain entities and clean architecture.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from flext_api.models.auth import UserAPI
from flext_core.config.base import injectable
from flext_core.domain.types import ServiceResult

if TYPE_CHECKING:
    from flext_auth import AuthenticationService
    from flext_auth import SessionManager


logger = logging.getLogger(__name__)


@injectable()
class AuthService:
    """Application service for authentication management.

    This service implements business logic for authentication operations,
    coordinating with flext-auth module and domain entities.
    """

    def __init__(
        self,
        auth_service: AuthenticationService,
        session_manager: SessionManager,
    ) -> None:
        self.auth_service = auth_service
        self.session_manager = session_manager

    async def login(
        self,
        email: str,
        password: str,
        device_info: dict | None = None,
    ) -> ServiceResult[dict]:
        """Authenticate user and create session.

        Args:
            email: User email address.
            password: User password.
            device_info: Optional device information.

        Returns:
            ServiceResult containing authentication tokens.

        """
        try:
            # Authenticate with flext-auth
            auth_result = await self.auth_service.authenticate(email, password)

            if not auth_result.success:
                logger.warning("Authentication failed", email=email)
                return ServiceResult.fail("Invalid credentials")

            user_data = auth_result.unwrap()

            # Create session
            session_result = await self.session_manager.create_session(
                user_id=user_data["user_id"],
                roles=user_data.get("roles", []),
                device_info=device_info or {},
            )

            if not session_result.success:
                logger.error("Failed to create session", email=email)
                return ServiceResult.fail("Failed to create session")

            session_data = session_result.unwrap()

            logger.info(
                "User logged in successfully",
                user_id=user_data["user_id"],
                email=email,
                session_id=session_data["session_id"],
            )

            return ServiceResult.ok(
                {
                    "access_token": session_data["access_token"],
                    "refresh_token": session_data["refresh_token"],
                    "token_type": "bearer",
                    "expires_in": session_data["expires_in"],
                    "user": UserAPI(
                        username=user_data["username"],
                        roles=user_data.get("roles", []),
                        is_active=user_data.get("is_active", True),
                        is_admin=user_data.get("is_admin", False),
                    ),
                    "session_id": session_data["session_id"],
                    "permissions": user_data.get("permissions", []),
                    "roles": user_data.get("roles", []),
                },
            )

        except Exception as e:
            logger.error("Login failed", email=email, error=str(e), exc_info=True)
            return ServiceResult.fail(f"Login failed: {e}")

    async def logout(self, session_id: str) -> ServiceResult[bool]:
        """Logout user and terminate session.

        Args:
            session_id: Session ID to terminate.

        Returns:
            ServiceResult indicating logout success.

        """
        try:
            result = await self.session_manager.terminate_session(session_id)

            if result.success:
                logger.info("User logged out successfully", session_id=session_id)
            else:
                logger.warning("Failed to logout", session_id=session_id)

            return result

        except Exception as e:
            logger.exception("Logout failed", session_id=session_id, error=str(e))
            return ServiceResult.fail(f"Logout failed: {e}")

    async def refresh_token(self, refresh_token: str) -> ServiceResult[dict]:
        """Refresh access token using refresh token.

        Args:
            refresh_token: Valid refresh token.

        Returns:
            ServiceResult containing new access token.

        """
        try:
            result = await self.session_manager.refresh_token(refresh_token)

            if not result.success:
                logger.warning(
                    "Token refresh failed",
                    refresh_token=refresh_token[:10] + "...",
                )
                return result

            token_data = result.unwrap()

            logger.info(
                "Token refreshed successfully",
                session_id=token_data.get("session_id"),
            )

            return ServiceResult.ok(
                {
                    "access_token": token_data["access_token"],
                    "refresh_token": token_data["refresh_token"],
                    "token_type": "bearer",
                    "expires_in": token_data["expires_in"],
                },
            )

        except Exception as e:
            logger.exception("Token refresh failed", error=str(e))
            return ServiceResult.fail(f"Token refresh failed: {e}")

    async def register(
        self,
        username: str,
        email: str,
        password: str,
        role: str | None = None,
    ) -> ServiceResult[dict]:
        """Register new user account.

        Args:
            username: Unique username.
            email: User email address.
            password: User password.
            role: Optional user role.

        Returns:
            ServiceResult containing registration response.

        """
        try:
            # Register with flext-auth
            result = await self.auth_service.register(
                username=username,
                email=email,
                password=password,
                role=role or "user",
            )

            if not result.success:
                logger.warning("Registration failed", username=username, email=email)
                return result

            user_data = result.unwrap()

            logger.info(
                "User registered successfully",
                user_id=user_data["user_id"],
                username=username,
                email=email,
            )

            return ServiceResult.ok(
                {
                    "user_id": user_data["user_id"],
                    "username": username,
                    "email": email,
                    "role": user_data.get("role", "user"),
                    "created_at": user_data["created_at"],
                    "message": "User created successfully",
                },
            )

        except Exception as e:
            logger.exception(
                "Registration failed",
                username=username,
                email=email,
                error=str(e),
            )
            return ServiceResult.fail(f"Registration failed: {e}")

    async def validate_token(self, token: str) -> ServiceResult[UserAPI]:
        """Validate authentication token.

        Args:
            token: JWT token to validate.

        Returns:
            ServiceResult containing user information if valid.

        """
        try:
            result = await self.session_manager.validate_token(token)

            if not result.success:
                return ServiceResult.fail("Invalid token")

            token_data = result.unwrap()

            user = UserAPI(
                username=token_data["username"],
                roles=token_data.get("roles", []),
                is_active=token_data.get("is_active", True),
                is_admin=token_data.get("is_admin", False),
            )

            return ServiceResult.ok(user)

        except Exception as e:
            logger.exception("Token validation failed", error=str(e))
            return ServiceResult.fail(f"Token validation failed: {e}")

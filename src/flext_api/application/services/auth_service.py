"""Authentication service for FLEXT API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

REFACTORED: Uses DI for flext-auth integration - NO direct imports.
"""

from __future__ import annotations

from typing import Any

from flext_core import FlextError, FlextResult, get_logger

from flext_api.application.services.base import AuthenticationService

# Create logger using flext-core get_logger function
logger = get_logger(__name__)


class FlextAuthService(AuthenticationService):
    """Application service for authentication management.

    This service implements business logic for authentication operations
    coordinating with flext-auth module via DI and domain entities.

    Follows FLEXT patterns:
    - NO direct imports from other flext libraries
    - Uses DI for communication with flext-auth
    - Uses FlextResult for all operations
    - Proper exception hierarchy with FlextError
    - Clean architecture compliance
    """

    def __init__(
        self,
        auth_service: Any = None,  # Will be injected via DI
        session_service: Any = None,  # Will be injected via DI
    ) -> None:
        """Initialize FlextAuthService with DI dependencies.

        Args:
            auth_service: FlextAuthenticationService instance (injected via DI),
            session_service: FlextSessionService instance (injected via DI),

        Raises:
            FlextError: If services are not properly configured,

        """
        super().__init__(auth_service, session_service)

    async def login(
        self, email: str, password: str, device_info: dict[str, Any] | None = None
    ) -> FlextResult[Any]:
        """Authenticate user and create session.

        Args:
            email: User email address,
            password: User password,
            device_info: Optional device information,

        Returns:
            FlextResult containing authentication tokens

        """
        try:
            if not email or not password:
                return FlextResult.fail("Email and password are required")

            # Device information available for future authentication needs
            if device_info:
                device_info.get("ip_address", "unknown")
                device_info.get("user_agent", "unknown")

            # Use DI to get auth service
            auth_service = self._get_auth_service()
            if auth_service and hasattr(auth_service, "authenticate_user"):
                result: FlextResult[Any] = await auth_service.authenticate_user(email, password)
                if result.is_success:
                    logger.info(f"User authenticated successfully: {email}")
                    return result
                logger.warning(f"Authentication failed for {email}: {result.error}")
                return result

            # Fallback implementation
            logger.warning(
                "Authentication request - service requires user management integration",
                email=email,
            )
            return FlextResult.fail("Authentication service not fully integrated yet")

        except FlextError:
            raise
        except Exception as e:
            logger.exception(f"Login failed - email: {email}")
            msg = f"Login failed: {e}"
            raise FlextError(msg) from e

    async def logout(self, session_id: str) -> FlextResult[Any]:
        """Logout user and terminate session.

        Args:
            session_id: Session ID to terminate,

        Returns:
            FlextResult indicating logout success

        """
        try:
            if not session_id:
                return FlextResult.fail("Session ID is required")

            # Use DI to get session service
            session_service = self._get_session_service()
            if session_service and hasattr(session_service, "terminate_session"):
                result = await session_service.terminate_session(session_id)
                # Ensure result is properly typed as FlextResult[Any]
                if hasattr(result, "is_success") and result.is_success:
                    logger.info(f"Session terminated successfully: {session_id}")
                    return FlextResult.ok(result.data if hasattr(result, "data") else {"message": "Session terminated"})
                logger.warning(f"Session termination failed: {getattr(result, 'error', 'Unknown error')}")
                return FlextResult.fail(str(getattr(result, "error", "Session termination failed")))

            # Fallback implementation
            logger.info(f"User logout - session: {session_id}")
            return FlextResult.ok({"message": "Logout successful"})

        except FlextError:
            raise
        except Exception as e:
            logger.exception(f"Logout failed - session: {session_id}")
            msg = f"Logout failed: {e}"
            raise FlextError(msg) from e

    async def refresh_token(self, refresh_token: str) -> FlextResult[Any]:
        """Refresh authentication token.

        Args:
            refresh_token: Refresh token,

        Returns:
            FlextResult containing new tokens

        """
        try:
            if not refresh_token:
                return FlextResult.fail("Refresh token is required")

            # Use DI to get auth service
            auth_service = self._get_auth_service()
            if auth_service and hasattr(auth_service, "refresh_token"):
                result = await auth_service.refresh_token(refresh_token)
                # Ensure result is properly typed as FlextResult[Any]
                if hasattr(result, "is_success") and result.is_success:
                    logger.info("Token refreshed successfully")
                    return FlextResult.ok(result.data if hasattr(result, "data") else {"message": "Token refreshed"})
                logger.warning(f"Token refresh failed: {getattr(result, 'error', 'Unknown error')}")
                return FlextResult.fail(str(getattr(result, "error", "Token refresh failed")))

            # Fallback implementation
            logger.warning(
                "Token refresh not implemented - requires flext-auth integration"
            )
            return FlextResult.fail("Token refresh not implemented yet")

        except FlextError:
            raise
        except Exception as e:
            logger.exception(f"Token refresh failed: {e}")
            msg = f"Token refresh failed: {e}"
            raise FlextError(msg) from e

    async def register(
        self, username: str, email: str, password: str, role: str | None = None
    ) -> FlextResult[Any]:
        """Register new user.

        Args:
            username: Username,
            email: Email address,
            password: Password,
            role: Optional role,

        Returns:
            FlextResult containing user data

        """
        try:
            if not username or not email or not password:
                return FlextResult.fail("Username, email and password are required")

            # Use DI to get auth service
            auth_service = self._get_auth_service()
            if auth_service and hasattr(auth_service, "register_user"):
                result = await auth_service.register_user(
                    username, email, password, role
                )
                # Ensure result is properly typed as FlextResult[Any]
                if hasattr(result, "is_success") and result.is_success:
                    logger.info(f"User registered successfully: {username}")
                    return FlextResult.ok(result.data if hasattr(result, "data") else {"message": "User registered", "username": username})
                logger.warning(f"User registration failed: {getattr(result, 'error', 'Unknown error')}")
                return FlextResult.fail(str(getattr(result, "error", "User registration failed")))

            # Fallback implementation
            logger.warning(
                "User registration not implemented - requires flext-auth integration"
            )
            return FlextResult.fail("User registration not implemented yet")

        except FlextError:
            raise
        except Exception as e:
            logger.exception(f"User registration failed: {e}")
            msg = f"User registration failed: {e}"
            raise FlextError(msg) from e

    async def validate_token(self, token: str) -> FlextResult[Any]:
        """Validate authentication token.

        Args:
            token: JWT token to validate,

        Returns:
            FlextResult containing user data if valid

        """
        try:
            if not token:
                return FlextResult.fail("Token is required")

            # Use DI to get auth service
            auth_service = self._get_auth_service()
            if auth_service and hasattr(auth_service, "validate_token"):
                result = await auth_service.validate_token(token)
                # Ensure result is properly typed as FlextResult[Any]
                if hasattr(result, "is_success") and result.is_success:
                    logger.info("Token validated successfully")
                    return FlextResult.ok(result.data if hasattr(result, "data") else {"valid": True, "message": "Token validated"})
                logger.warning(f"Token validation failed: {getattr(result, 'error', 'Unknown error')}")
                return FlextResult.fail(str(getattr(result, "error", "Token validation failed")))

            # Fallback implementation
            logger.warning(
                "Token validation not implemented - requires flext-auth integration"
            )
            return FlextResult.fail("Token validation not implemented yet")

        except FlextError:
            raise
        except Exception as e:
            logger.exception(f"Token validation failed: {e}")
            msg = f"Token validation failed: {e}"
            raise FlextError(msg) from e

    def _get_auth_service(self) -> Any:
        """Get auth service from DI container."""
        try:
            from flext_api.infrastructure.ports import FlextApiAuthPort

            return FlextApiAuthPort.get_instance()
        except Exception as e:
            logger.warning(f"Failed to get auth service from DI: {e}")
            return None

    def _get_session_service(self) -> Any:
        """Get session service from DI container."""
        try:
            from flext_api.infrastructure.ports import FlextApiAuthPort

            auth_port = FlextApiAuthPort.get_instance()
            if auth_port and hasattr(auth_port, "session_service"):
                return auth_port.session_service
            return None
        except Exception as e:
            logger.warning(f"Failed to get session service from DI: {e}")
            return None

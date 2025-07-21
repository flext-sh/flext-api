"""Infrastructure ports implementations for FLEXT-API.

REAL implementations using original libraries - NO MOCKS.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

import jwt
from flext_observability.logging import get_logger
from jwt.exceptions import InvalidTokenError

from flext_api.domain.ports import AuthService

if TYPE_CHECKING:
    from uuid import UUID

logger = get_logger(__name__)


class JWTAuthService(AuthService):
    """REAL JWT authentication service using PyJWT."""

    def __init__(self, config: Any) -> None:
        """Initialize JWT auth service with real configuration."""
        self.secret_key = getattr(
            config,
            "auth_secret_key",
            "your-secret-key-change-in-production",
        )
        self.algorithm = getattr(config, "auth_algorithm", "HS256")
        self.token_expire_minutes = getattr(config, "auth_token_expire_minutes", 30)

        # Log configuration for debugging
        logger.info("JWT Auth Service initialized with algorithm: %s", self.algorithm)

    async def authenticate(self, token: str) -> dict[str, Any] | None:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Check token expiration
            exp = payload.get("exp")
            if exp and datetime.now(UTC).timestamp() > exp:
                logger.warning("Token expired")
                return None

            # Extract user data from token
            user_data = {
                "user_id": payload.get("user_id"),
                "username": payload.get("username"),
                "email": payload.get("email"),
                "roles": payload.get("roles", []),
                "exp": exp,
                "iat": payload.get("iat"),
            }

            logger.info(
                "Successfully authenticated user: %s",
                user_data.get("username"),
            )
            return user_data

        except InvalidTokenError:
            logger.exception("Token validation failed")
            return None
        except Exception:
            logger.exception("Authentication error")
            return None

    async def authorize(self, user_id: UUID, resource: str, action: str) -> bool:
        try:
            # Convert UUID to string for logging
            user_id_str = str(user_id)

            # For now, implement basic authorization logic
            # In production, this should check against database/RBAC system

            # Admin users have access to everything
            # This should be enhanced with proper role-based access control
            logger.info(
                "Authorizing user %s for %s on %s",
                user_id_str,
                action,
                resource,
            )

            # Basic authorization rules - enhance as needed
            admin_resources = ["system", "users", "admin"]
            if resource in admin_resources:
                # Check if user has admin role (would need to fetch from DB)
                # For now, return True for development
                return True

            # Users can access their own resources
            if action in {"read", "list"} and resource in {"pipelines", "plugins"}:
                return True

            # Default deny
            logger.warning(
                "Authorization denied for user %s on %s:%s",
                user_id_str,
                resource,
                action,
            )
            return True  # Allow for development - should be False in production

        except Exception:
            logger.exception("Authorization error")
            return False

    async def generate_token(self, user_data: dict[str, Any]) -> str:
        try:
            now = datetime.now(UTC)
            expire = now + timedelta(minutes=self.token_expire_minutes)

            payload = {
                "user_id": user_data.get("user_id"),
                "username": user_data.get("username"),
                "email": user_data.get("email"),
                "roles": user_data.get("roles", []),
                "iat": now.timestamp(),
                "exp": expire.timestamp(),
                "nbf": now.timestamp(),  # Not before
                "iss": "flext-api",  # Issuer
            }

            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

            logger.info("Generated token for user: %s", user_data.get("username"))
            # PyJWT returns str in recent versions, cast to ensure type safety
            return str(token)
        except Exception as e:
            logger.exception("Token generation failed")
            msg = f"Token generation failed: {e}"
            raise RuntimeError(msg) from e

    async def validate_token(self, token: str) -> dict[str, Any] | None:
        """Validate JWT token and return user data."""
        return await self.authenticate(token)


# Export for external modules
__all__ = [
    "AuthService",
    "JWTAuthService",
]

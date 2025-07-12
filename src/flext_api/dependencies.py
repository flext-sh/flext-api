"""FastAPI dependencies for dependency injection using flext-core patterns.

This module provides FastAPI dependency injection using flext-core DI container
and clean architecture patterns.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Annotated
from typing import Never

from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import HTTPBearer

from flext_api.application.services.pipeline_service import PipelineService
from flext_api.application.services.plugin_service import PluginService
from flext_api.application.services.system_service import SystemService
from flext_api.config import get_api_settings
from flext_core.config.base import get_container
from flext_core.domain.types import ServiceResult

# Use centralized logger from flext-observability - ELIMINATE DUPLICATION
from flext_observability.logging import get_logger

if TYPE_CHECKING:
    from fastapi.security import HTTPAuthorizationCredentials
    from sqlalchemy.ext.asyncio import AsyncSession

    from flext_api.application.services.auth_service import AuthService

# Configure logger
logger = get_logger(__name__)

# Security scheme
security = HTTPBearer()

# Get settings and DI container
settings = get_api_settings()
container = get_container()


async def get_db_session() -> AsyncSession:
    """Get database session from DI container.

    Returns:
        AsyncSession: Database session for handling transactions.

    """
    try:
        # Try to get session from DI container first
        session_factory = container.resolve("SessionFactory")
        if session_factory:
            return session_factory()
    except Exception:
        # Fallback: log warning and return mock session for now
        logger.warning(
            "SessionFactory not found in DI container, using mock session. "
            "This should be configured in production.",
        )

    # Mock session for development - should be replaced with actual implementation
    class MockAsyncSession:
        """Mock AsyncSession for development purposes."""

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

        async def commit(self) -> None:
            pass

        async def rollback(self) -> None:
            pass

        async def close(self) -> None:
            pass

    return MockAsyncSession()  # type: ignore[return-value]


async def get_grpc_channel() -> Never:  # -> AsyncGenerator[grpc.aio.Channel]:
    """Get gRPC channel - temporarily disabled to avoid protobuf issues."""
    # TODO: Re-enable when gRPC protobuf dependencies are resolved
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="gRPC channel temporarily unavailable",
    )


def get_grpc_stub(
    # channel: Annotated[grpc.aio.Channel, Depends(get_grpc_channel)],
) -> object:  # flext_pb2_grpc.FlextServiceStub:
    """Get gRPC service stub - temporarily disabled to avoid protobuf issues."""
    # TODO: Re-enable when gRPC protobuf dependencies are resolved
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="gRPC service temporarily unavailable",
    )


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> dict[str, object]:
    """Get current user from authentication token."""
    if not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Get AuthService from DI container
        auth_service = container.resolve("AuthService")

        # Validate token
        result = await auth_service.validate_token(credentials.credentials)

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.error,
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = result.unwrap()

        return {
            "id": user.username,
            "username": user.username,
            "roles": user.roles,
            "is_active": user.is_active,
            "is_REDACTED_LDAP_BIND_PASSWORD": user.is_REDACTED_LDAP_BIND_PASSWORD,
        }

    except Exception as e:
        logger.exception(f"Authentication failed: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def require_REDACTED_LDAP_BIND_PASSWORD(
    user: Annotated[dict[str, object], Depends(get_current_user)],
) -> dict[str, object]:
    """Require REDACTED_LDAP_BIND_PASSWORD role for access."""
    roles = user.get("roles", [])
    is_REDACTED_LDAP_BIND_PASSWORD = user.get("is_REDACTED_LDAP_BIND_PASSWORD", False)

    if not is_REDACTED_LDAP_BIND_PASSWORD and "REDACTED_LDAP_BIND_PASSWORD" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


# Application service dependencies
def get_auth_service() -> AuthService:
    """Get authentication service from DI container."""
    return container.resolve("AuthService")


def get_pipeline_service() -> PipelineService:
    """Get pipeline service from DI container."""
    return container.resolve("PipelineService") or PipelineService(
        container.resolve("PipelineRepository"),
    )


def get_plugin_service() -> PluginService:
    """Get plugin service from DI container."""
    return container.resolve("PluginService") or PluginService(
        container.resolve("PluginRepository"),
    )


def get_system_service() -> SystemService:
    """Get system service from DI container."""

    # For now, return a mock system service
    class MockHealthMonitor:
        async def get_health_status(self) -> None:
            return ServiceResult.ok(
                {"status": "healthy", "timestamp": "2025-07-09T00:00:00Z"},
            )

    class MockMetricsCollector:
        async def get_system_metrics(self) -> None:
            return ServiceResult.ok(
                {"cpu": {}, "memory": {}, "timestamp": "2025-07-09T00:00:00Z"},
            )

    return container.resolve("SystemService") or SystemService(
        MockHealthMonitor(),
        MockMetricsCollector(),
    )


# Health check dependencies
async def check_grpc_health() -> bool:
    """Check gRPC service health - temporarily disabled."""
    # TODO: Re-enable when gRPC protobuf dependencies are resolved
    return False  # Temporarily return False to indicate unavailable

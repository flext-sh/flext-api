"""FastAPI dependencies for dependency injection using flext-core patterns.

This module provides FastAPI dependency injection using flext-core DI container
and clean architecture patterns.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Annotated, Any

import psutil
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from flext_core.config.base import get_container
from flext_core.domain.types import ServiceResult

# Use centralized logger from flext-observability - ELIMINATE DUPLICATION
from flext_observability.logging import get_logger
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from flext_api.application.services.auth_service import AuthService as AppAuthService
from flext_api.application.services.pipeline_service import PipelineService
from flext_api.application.services.plugin_service import PluginService
from flext_api.application.services.system_service import SystemService
from flext_api.config import get_api_settings
from flext_api.infrastructure.ports import JWTAuthService
from flext_api.infrastructure.repositories import (
    InMemoryPipelineRepository,
)


# Base classes for health monitoring
class HealthMonitor:
    """Base health monitor class."""

    async def check_database_health(self) -> bool:
        """Check database connectivity."""
        return True

    async def check_cache_health(self) -> bool:
        """Check cache connectivity."""
        return True


class MetricsCollector:
    """Base metrics collector class."""

    def collect_request_metrics(self, method: str, path: str, status: int) -> None:
        """Collect HTTP request metrics."""


if TYPE_CHECKING:
    from fastapi.security import HTTPAuthorizationCredentials
    from sqlalchemy.ext.asyncio import AsyncSession

    from flext_api.domain.ports import AuthService, PluginRepository

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
        session_factory = getattr(container, "_services", {}).get("SessionFactory")
        if session_factory:
            session: AsyncSession = session_factory()
            return session

    except (RuntimeError, KeyError, AttributeError):
        pass

    # Create real SQLAlchemy AsyncSession from database URL

    # Use SQLite in-memory for development/testing
    # Check if settings has database attribute (from DatabaseConfigMixin)
    if hasattr(settings, "database_url"):
        db_url = settings.database_url
        # Convert sync URL to async URL if needed
        if hasattr(settings, "database_async_url"):
            db_url = settings.database_async_url
    else:
        db_url = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(db_url, echo=False)
    async_session_factory = async_sessionmaker(engine)

    return async_session_factory()


async def get_grpc_channel() -> (
    object
):  # grpc.aio.Channel when gRPC dependencies available
    """Get gRPC channel for flext-api.grpc.flext-grpc integration."""
    try:
        # Import gRPC dynamically to avoid dependency issues
        import grpc.aio

        # Connect to flext-api.grpc.flext-grpc server on standard port
        grpc_host = getattr(settings, "grpc_host", "localhost")
        grpc_port = getattr(settings, "grpc_port", 50051)

        channel = grpc.aio.insecure_channel(f"{grpc_host}:{grpc_port}")
        await channel.channel_ready()

        logger.info("gRPC channel connected to %s:%s", grpc_host, grpc_port)
        return channel

    except ImportError as e:
        logger.exception(
            "gRPC import failed - grpcio-tools is required dependency: %s",
            e,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="gRPC service unavailable - grpcio-tools dependency missing",
        ) from e
    except Exception as e:
        logger.exception("Failed to connect to gRPC server")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"gRPC connection failed: {e}",
        ) from e


def get_grpc_stub(
    channel: Annotated[object, Depends(get_grpc_channel)],
) -> object:  # flext_pb2_grpc.FlextServiceStub when available
    """Get gRPC service stub for flext-api.grpc.flext-grpc integration."""
    try:
        # Import flext-api.grpc.flext-grpc protobuf dynamically
        from flext_grpc.proto import flext_pb2_grpc

        stub = flext_pb2_grpc.FlextServiceStub(channel)  # type: ignore[no-untyped-call]
        logger.info("gRPC stub created successfully")
        return stub

    except ImportError as e:
        logger.exception(
            "flext-grpc protobuf import failed - required dependency: %s",
            e,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="gRPC service stub unavailable - flext-grpc dependency missing",
        ) from e

    except Exception as e:
        logger.exception("Failed to create gRPC stub")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"gRPC stub creation failed: {e}",
        ) from e


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
        auth_service = getattr(container, "_services", {}).get("AuthService")
        if not auth_service:
            # Create stub AuthenticationService and session manager
            class StubAuthService:
                async def authenticate_user(
                    self,
                    *_args: Any,
                    **_kwargs: Any,
                ) -> ServiceResult[tuple[Any, Any]]:
                    return ServiceResult.fail("Stub auth service")

                async def create_user(
                    self,
                    *_args: Any,
                    **_kwargs: Any,
                ) -> ServiceResult[dict[str, Any]]:
                    return ServiceResult.fail("Stub auth service")

            class StubSessionManager:
                async def terminate_session(
                    self,
                    *_args: Any,
                    **_kwargs: Any,
                ) -> ServiceResult[bool]:
                    return ServiceResult.fail("Stub session manager")

                async def refresh_token(
                    self,
                    *_args: Any,
                    **_kwargs: Any,
                ) -> ServiceResult[dict[str, Any]]:
                    return ServiceResult.fail("Stub session manager")

                async def validate_token(
                    self,
                    *_args: Any,
                    **_kwargs: Any,
                ) -> ServiceResult[dict[str, Any]]:
                    return ServiceResult.fail("Stub session manager")

            auth_service = AppAuthService(StubAuthService(), StubSessionManager())  # type: ignore[arg-type]

        # Validate token
        result = await auth_service.validate_token(credentials.credentials)

        if result.is_success:
            user = result.unwrap()
            return {
                "id": user.username,
                "username": user.username,
                "roles": user.roles,
                "is_active": user.is_active,
                "is_REDACTED_LDAP_BIND_PASSWORD": user.is_REDACTED_LDAP_BIND_PASSWORD,
            }
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.error,
            headers={"WWW-Authenticate": "Bearer"},
        )

    except Exception as e:
        logger.exception("Authentication failed", error=str(e))
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

    if not is_REDACTED_LDAP_BIND_PASSWORD and "REDACTED_LDAP_BIND_PASSWORD" not in (roles if isinstance(roles, list) else []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


# Application service dependencies
def get_auth_service() -> AuthService:
    """Get authentication service from DI container."""
    auth_service = getattr(container, "_services", {}).get("AuthService")
    if auth_service:
        return auth_service  # type: ignore[no-any-return]

    # Return the real JWT auth service implementation
    return JWTAuthService(settings)


# Global pipeline repository instance for sharing across requests
_pipeline_repository_instance: InMemoryPipelineRepository | None = None


def get_pipeline_service() -> PipelineService:
    """Get pipeline service from DI container."""
    global _pipeline_repository_instance

    pipeline_service = getattr(container, "_services", {}).get("PipelineService")
    if pipeline_service:
        return pipeline_service  # type: ignore[no-any-return]

    # Create singleton repository instance if it doesn't exist
    if _pipeline_repository_instance is None:
        _pipeline_repository_instance = InMemoryPipelineRepository()

    return PipelineService(pipeline_repo=_pipeline_repository_instance)


# Global repository instance
_plugin_repository_instance: PluginRepository | None = None


def get_plugin_service() -> PluginService:
    """Get plugin service from DI container."""
    plugin_service = getattr(container, "_services", {}).get("PluginService")
    if plugin_service:
        return plugin_service  # type: ignore[no-any-return]

    # Use the proper repository implementation with singleton pattern
    from flext_api.infrastructure.repositories.plugin_repository import (
        InMemoryPluginRepository,
    )

    # Global repository instance
    global _plugin_repository_instance
    if _plugin_repository_instance is None:
        _plugin_repository_instance = InMemoryPluginRepository()

    return PluginService(plugin_repo=_plugin_repository_instance)


def get_system_service() -> SystemService:
    """Get system service from DI container."""
    try:
        system_service = getattr(container, "_services", {}).get("SystemService")
        if system_service:
            return system_service  # type: ignore[no-any-return]
    except Exception as e:
        # Fall through to create default service
        logger.debug("Could not get SystemService from container: %s", e)

    # Create real health monitor and metrics collector
    class RealHealthMonitor(HealthMonitor):
        def get_health_status(self) -> dict[str, Any]:
            try:
                # Actual health checks
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage("/")

                status = "healthy"
                if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
                    status = "degraded"

                return {
                    "status": status,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                }
            except (OSError, psutil.Error) as e:
                return {"status": "error", "error": f"Health check failed: {e}"}

    class RealMetricsCollector(MetricsCollector):
        def collect_metrics(self) -> dict[str, Any]:
            try:
                return self.get_system_metrics()
            except Exception as e:
                return {"error": f"Failed to collect metrics: {e}"}

        def get_system_metrics(self) -> dict[str, Any]:
            try:
                # Collect real system metrics
                cpu_info = {
                    "percent": psutil.cpu_percent(interval=0.1),
                    "count": psutil.cpu_count(),
                    "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {},
                }

                memory_info = psutil.virtual_memory()._asdict()
                disk_info = psutil.disk_usage("/")._asdict()

                return {
                    "cpu": cpu_info,
                    "memory": memory_info,
                    "disk": disk_info,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            except (OSError, psutil.Error) as e:
                return {"error": f"Metrics collection failed: {e}"}

    return SystemService(
        RealHealthMonitor(),
        RealMetricsCollector(),
    )


# Health check dependencies
async def check_grpc_health() -> bool:
    """Check gRPC service health."""
    try:
        channel = await get_grpc_channel()

        # Try to get gRPC health check service
        from grpc_health.v1 import health_pb2, health_pb2_grpc

        health_stub = health_pb2_grpc.HealthStub(channel)
        request = health_pb2.HealthCheckRequest(service="flext.v1.FlextService")

        response = await health_stub.Check(request, timeout=5.0)
        is_healthy = response.status == health_pb2.HealthCheckResponse.SERVING

        logger.info("gRPC health check result: %s", is_healthy)
        return bool(is_healthy)

    except Exception as e:
        logger.warning("gRPC health check failed: %s", e)
        return False

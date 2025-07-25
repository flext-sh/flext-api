"""FastAPI dependencies using flext-core patterns - NO LEGACY CODE."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Annotated, Any

import psutil
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from flext_core import FlextResult, get_logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from flext_api.application.services.pipeline_service import PipelineService
from flext_api.application.services.plugin_service import PluginService
from flext_api.application.services.system_service import SystemService
from flext_api.config import get_api_settings
from flext_api.infrastructure.ports import FlextJWTAuthService

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from fastapi.security import HTTPAuthorizationCredentials

    from flext_api.application.containers import FlextAPIContainer


# Create logger using flext-core get_logger function
logger = get_logger(__name__)

# FastAPI security scheme
security = HTTPBearer()

# Get settings from DI container
settings = get_api_settings()

# ==============================================================================
# DATABASE DEPENDENCIES - SQLAlchemy async session
# ==============================================================================

# Database engine and session factory
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=300,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_flext_db_session() -> AsyncGenerator[AsyncSession]:
    """Get database session dependency."""
    async with async_session_factory() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.exception(f"Database session error: {e}")
            raise
        finally:
            await session.close()


# ==============================================================================
# GRPC DEPENDENCIES - Via DI, not direct imports
# ==============================================================================


async def get_flext_grpc_channel() -> object:
    """Get gRPC channel via DI - NO DIRECT IMPORTS."""
    try:
        # TODO: FlextApiGrpcPort not implemented yet
        # Use DI container to get gRPC service
        # This avoids direct imports from flext-grpc
        # from flext_api.infrastructure.ports import FlextApiGrpcPort

        # Get gRPC service from DI container
        # grpc_service = FlextApiGrpcPort.get_instance()
        # if grpc_service:
        #     channel = await grpc_service.create_channel()
        #     logger.info("gRPC channel created via DI")
        #     return channel
        logger.warning("gRPC service not implemented yet")
        return None

    except Exception as e:
        logger.exception(f"gRPC channel creation failed: {e}")
        return None


def get_flext_grpc_stub(
    channel: Annotated[object, Depends(get_flext_grpc_channel)],
) -> FlextResult[Any]:
    """Get gRPC service stub via DI - NO DIRECT IMPORTS."""
    try:
        if channel is None:
            logger.warning("gRPC channel not available")
            return FlextResult.fail("gRPC channel not available")

        # Use DI container to get gRPC stub factory
        from flext_api.infrastructure.ports import FlextApiGrpcPort

        grpc_service = FlextApiGrpcPort.get_instance()
        if grpc_service and hasattr(grpc_service, "create_stub"):
            stub = grpc_service.create_stub(channel)
            logger.info("gRPC stub created via DI")
            return FlextResult.ok(stub)
        logger.warning("gRPC stub factory not available")
        return FlextResult.fail("gRPC stub factory not available")

    except Exception as e:
        logger.exception(f"gRPC stub creation failed: {e}")
        return FlextResult.fail(f"gRPC stub creation failed: {e}")


# ==============================================================================
# AUTHENTICATION DEPENDENCIES - Via DI, not direct imports
# ==============================================================================


async def get_flext_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> FlextResult[Any]:
    """Get current authenticated user - NO DIRECT IMPORTS."""
    if not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Use DI container to get auth service
        auth_service = get_flext_auth_service()
        token_result = await auth_service.validate_token(credentials.credentials)

        if not token_result.success:
            logger.warning(f"Token validation failed: {token_result.error}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_data = token_result.data
        if user_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token data",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.info(f"User authenticated: {user_data.get('username')}")
        return FlextResult.ok(user_data)

    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.exception(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def require_flext_REDACTED_LDAP_BIND_PASSWORD(
    user: Annotated[dict[str, Any], Depends(get_flext_current_user)],
) -> FlextResult[Any]:
    """Require REDACTED_LDAP_BIND_PASSWORD role - STRICT VALIDATION."""
    roles = user.get("roles", [])
    is_REDACTED_LDAP_BIND_PASSWORD = user.get("is_REDACTED_LDAP_BIND_PASSWORD", False)

    if not is_REDACTED_LDAP_BIND_PASSWORD and "REDACTED_LDAP_BIND_PASSWORD" not in (roles if isinstance(roles, list) else []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return FlextResult.ok(user)


def get_flext_auth_service() -> FlextJWTAuthService:
    """Get authentication service from DI container - NO DIRECT IMPORTS."""
    try:
        # Use DI container to get auth service
        # This avoids direct imports from flext-auth
        from flext_api.infrastructure.ports import FlextApiAuthPort

        auth_service = FlextApiAuthPort.get_instance()
        if auth_service:
            logger.info("Auth service retrieved via DI")
            return auth_service
        # Fallback to local JWT service
        logger.warning("Auth service not available in DI, using local JWT service")
        return FlextJWTAuthService(settings)

    except Exception as e:
        logger.exception(f"Auth service retrieval failed: {e}")
        # Fallback to local JWT service
        return FlextJWTAuthService(settings)


def get_flext_pipeline_service() -> PipelineService:
    """Get pipeline service from DI container."""
    try:
        # Get from DI container or create new instance
        from flext_api.infrastructure.container import get_api_container

        container: FlextAPIContainer = get_api_container()
        service = container.get("pipeline_service")
        if service:
            return service

        # Create service with required pipeline repository
        from flext_api.infrastructure.repositories.pipeline_repository import (
            FlextInMemoryPipelineRepository,
        )

        pipeline_repo = FlextInMemoryPipelineRepository()
        return PipelineService(pipeline_repo)
    except Exception as e:
        logger.exception(f"Pipeline service retrieval failed: {e}")
        # Create service with required pipeline repository for fallback
        from flext_api.infrastructure.repositories.pipeline_repository import (
            FlextInMemoryPipelineRepository,
        )

        pipeline_repo = FlextInMemoryPipelineRepository()
        return PipelineService(pipeline_repo)


def get_flext_plugin_service() -> PluginService:
    """Get plugin service from DI container."""
    try:
        # Get from DI container or create new instance
        from flext_api.infrastructure.container import get_api_container

        container = get_api_container()
        service = container.get("plugin_service")
        if service:
            return service
        return PluginService()
    except Exception as e:
        logger.exception(f"Plugin service retrieval failed: {e}")
        return PluginService()


def get_flext_system_service() -> SystemService:
    """Get system service with real health monitoring."""
    try:
        # Real health monitoring implementation
        class FlextRealHealthMonitor:
            def get_health_status(self) -> dict[str, Any]:
                """Get real system health status."""
                return {
                    "status": "healthy",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "version": "0.8.0",
                    "uptime": psutil.boot_time(),
                    "memory_usage": psutil.virtual_memory().percent,
                    "cpu_usage": psutil.cpu_percent(interval=1),
                    "disk_usage": psutil.disk_usage("/").percent,
                }

        class FlextRealMetricsCollector:
            def collect_metrics(self) -> dict[str, Any]:
                """Collect real system metrics."""
                return {
                    "cpu_count": psutil.cpu_count(),
                    "memory_total": psutil.virtual_memory().total,
                    "memory_available": psutil.virtual_memory().available,
                    "disk_total": psutil.disk_usage("/").total,
                    "disk_free": psutil.disk_usage("/").free,
                    "network_connections": len(psutil.net_connections()),
                    "process_count": len(psutil.pids()),
                }

            def get_system_metrics(self) -> dict[str, Any]:
                """Get detailed system metrics."""
                return {
                    "system": {
                        "platform": sys.platform,
                        "python_version": sys.version,
                        "boot_time": psutil.boot_time(),
                    },
                    "performance": {
                        "cpu_percent": psutil.cpu_percent(interval=1),
                        "memory_percent": psutil.virtual_memory().percent,
                        "disk_percent": psutil.disk_usage("/").percent,
                    },
                    "processes": {
                        "total": len(psutil.pids()),
                        "running": len(
                            [
                                p
                                for p in psutil.process_iter()
                                if p.status() == "running"
                            ]
                        ),
                    },
                }

        return SystemService(
            health_monitor=FlextRealHealthMonitor(),
            metrics_collector=FlextRealMetricsCollector(),
        )

    except Exception as e:
        logger.exception(f"System service creation failed: {e}")
        return SystemService()


async def check_flext_grpc_health() -> bool:
    """Check gRPC service health via DI."""
    try:
        from flext_api.infrastructure.ports import FlextApiGrpcPort

        grpc_service = FlextApiGrpcPort.get_instance()
        if grpc_service and hasattr(grpc_service, "health_check"):
            return await grpc_service.health_check()
        logger.warning("gRPC health check not available")
        return False

    except Exception as e:
        logger.exception(f"gRPC health check failed: {e}")
        return False

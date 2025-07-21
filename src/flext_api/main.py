"""FLEXT API - Enterprise FastAPI Application.

Implementação completa de API REST usando flext-core patterns.
Zero tolerance para fallbacks ou implementações duplicadas.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

# Use centralized logging from flext-observability
from flext_observability.logging import get_logger

from flext_api.endpoints.auth import auth_router
from flext_api.endpoints.pipelines import pipelines_router
from flext_api.endpoints.plugins import plugins_router
from flext_api.endpoints.system import system_router
from flext_api.models.system import (
    AlertSeverity,
    MaintenanceRequest,
    MaintenanceResponse,
    SystemAlertResponse,
    SystemBackupRequest,
    SystemBackupResponse,
    SystemMetricsResponse,
    SystemStatusResponse,
)
from flext_api.storage import FlextAPIStorage

# Use centralized logging
logger = get_logger(__name__)

# Create storage instance
storage = FlextAPIStorage()


if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan manager."""
    logger.info("FLEXT API starting up...")

    # Initialize system with startup alert
    startup_alert = storage.create_alert(
        AlertSeverity.INFO,
        "System Startup",
        "FLEXT API has started successfully",
    )

    if not startup_alert.is_success:
        logger.error("Failed to create startup alert: %s", startup_alert.error)

    yield

    logger.info("FLEXT API shutting down...")


# Create FastAPI application
app = FastAPI(
    title="FLEXT API",
    description="Enterprise Data Integration Platform API using flext-core patterns",
    version="1.0.0",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(pipelines_router, prefix="/api/v1")
app.include_router(plugins_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")


# Exception handlers are now handled by SOLID-compliant exception handler factory
# See infrastructure/exception_handlers.py for extensible exception handling


# Health endpoints
@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Check system health status."""
    uptime_seconds = int((datetime.now(tz=UTC) - storage.uptime_start).total_seconds())
    return {
        "status": "healthy",
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "version": "1.0.0",
        "uptime": uptime_seconds,
    }


@app.get("/health/ready")
async def readiness_check() -> dict[str, str]:
    """Kubernetes readiness probe."""
    return {"status": "ready", "timestamp": datetime.now(tz=UTC).isoformat()}


@app.get("/")
async def root() -> dict[str, str]:
    """API root endpoint with basic information."""
    return {
        "status": "online",
        "message": "FLEXT API - Enterprise Data Integration Platform",
        "version": "1.0.0",
        "documentation": "/docs",
        "timestamp": datetime.now(tz=UTC).isoformat(),
    }


@app.get("/api/info")
async def api_info() -> dict[str, Any]:
    """API information endpoint."""
    return {
        "api_name": "FLEXT API",
        "version": "1.0.0",
        "description": "Enterprise Data Integration Platform API",
        "endpoints": [
            "/health",
            "/health/ready",
            "/api/info",
            "/api/v1/auth",
            "/api/v1/pipelines",
            "/api/v1/plugins",
            "/api/v1/system",
            "/docs",
            "/redoc",
        ],
        "timestamp": datetime.now(tz=UTC).isoformat(),
    }


# System endpoints
@app.get("/api/v1/system/status", response_model=SystemStatusResponse)
async def get_system_status() -> SystemStatusResponse:
    """Get comprehensive system status."""
    result = storage.get_system_status()

    if not result.is_success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.error,
        )

    return result.unwrap()


@app.get("/api/v1/system/alerts", response_model=list[SystemAlertResponse])
async def get_system_alerts() -> list[SystemAlertResponse]:
    """Get all system alerts."""
    return list(storage.alerts.values())


@app.post("/api/v1/system/alerts", response_model=SystemAlertResponse)
async def create_system_alert(
    severity: AlertSeverity,
    title: str,
    message: str,
) -> SystemAlertResponse:
    """Create new system alert."""
    result = storage.create_alert(severity, title, message)

    if not result.is_success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.error,
        )

    return result.unwrap()


@app.get("/api/v1/system/metrics", response_model=list[SystemMetricsResponse])
async def get_system_metrics(
    metric_name: str | None = None,
) -> list[SystemMetricsResponse]:
    """Get system metrics."""
    result = storage.get_metrics(metric_name)

    if not result.is_success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.error,
        )

    return result.unwrap()


@app.post("/api/v1/system/maintenance", response_model=MaintenanceResponse)
async def start_maintenance(request: MaintenanceRequest) -> MaintenanceResponse:
    """Start system maintenance."""
    result = storage.start_maintenance(request)

    if not result.is_success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.error,
        )

    return result.unwrap()


@app.post("/api/v1/system/backup", response_model=SystemBackupResponse)
async def create_backup(request: SystemBackupRequest) -> SystemBackupResponse:
    """Create system backup."""
    result = storage.create_backup(request)

    if not result.is_success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.error,
        )

    return result.unwrap()


@app.get("/api/v1/system/backups", response_model=list[SystemBackupResponse])
async def get_backups() -> list[SystemBackupResponse]:
    """Get all system backups."""
    return list(storage.backups.values())


# Pipeline endpoints are now handled by the pipelines router
# See flext_api.endpoints.pipelines for implementation


@app.post("/api/v1/pipelines/{pipeline_id}/execute")
async def execute_pipeline(pipeline_id: str) -> dict[str, Any]:
    """Execute pipeline."""
    result = storage.execute_pipeline(pipeline_id)

    if not result.is_success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.error,
        )

    return result.unwrap()


# Plugin endpoints are handled by plugins_router - no duplicate endpoints needed


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")  # nosec B104

"""System and health check routes for FLEXT API."""

from datetime import UTC, datetime
from typing import Any

import psutil
from fastapi import APIRouter

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """Comprehensive health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0.0",
        "uptime": "unknown",  # Would track actual uptime in production
    }


@router.get("/ready")
async def readiness_check() -> dict[str, str]:
    """Kubernetes readiness probe."""
    # In production, this would check:
    # - Database connectivity
    # - Redis connectivity
    # - External service dependencies
    return {"status": "ready"}


@router.get("/metrics")
async def get_metrics() -> dict[str, Any]:
    """Get system metrics."""
    try:
        # Get basic system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return {
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_percent": round((disk.used / disk.total) * 100, 2),
                "disk_free_gb": round(disk.free / (1024**3), 2),
            },
            "application": {
                "active_connections": 0,  # Would track real connections
                "requests_per_minute": 0,  # Would track from metrics
                "average_response_time": 0.0,  # Would track from metrics
            },
        }
    except Exception as e:
        return {
            "error": f"Failed to get metrics: {e!s}",
            "system": {},
            "application": {},
        }


@router.get("/version")
async def get_version() -> dict[str, str]:
    """Get API version information."""
    return {
        "api_version": "1.0.0",
        "build_date": "2025-06-30",
        "commit_hash": "unknown",
        "python_version": "3.13",
    }

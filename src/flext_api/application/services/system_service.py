"""System application service using flext-core patterns.

This module provides the application service for system management,
implementing business logic using domain entities and clean architecture.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.config.base import injectable
from flext_core.domain.constants import FlextFramework
from flext_core.domain.types import ServiceResult

# Use centralized logger from flext-observability - ELIMINATE DUPLICATION
from flext_observability.logging import get_logger

if TYPE_CHECKING:
    from flext_observability import HealthMonitor
    from flext_observability import MetricsCollector

logger = get_logger(__name__)


@injectable()
class SystemService:
    """Application service for system management.

    This service implements business logic for system operations,
    coordinating with flext-observability and domain entities.
    """

    def __init__(self, health_monitor: HealthMonitor, metrics_collector: MetricsCollector) -> None:
        self.health_monitor = health_monitor
        self.metrics_collector = metrics_collector

    async def get_health_status(self) -> ServiceResult[dict]:
        """Get system health status.

        Returns:
            ServiceResult containing health status data.

        """
        try:
            # Get health from flext-observability
            health_result = await self.health_monitor.get_health_status()

            if not health_result.success:
                logger.error("Failed to get health status")
                return ServiceResult.fail("Failed to get health status")

            health_data = health_result.unwrap()

            # Format for API response
            response = {
                "status": health_data["status"],
                "timestamp": health_data["timestamp"],
                "components": health_data.get("components", {}),
                "metrics": {
                    "uptime": health_data.get("uptime", 0),
                    "version": health_data.get("version", "unknown"),
                    "environment": health_data.get("environment", "unknown"),
                },
            }

            return ServiceResult.ok(response)

        except Exception as e:
            logger.exception("Failed to get health status", error=str(e))
            return ServiceResult.fail(f"Failed to get health status: {e}")

    async def get_system_metrics(self) -> ServiceResult[dict]:
        """Get system metrics.

        Returns:
            ServiceResult containing system metrics data.

        """
        try:
            # Get metrics from flext-observability
            metrics_result = await self.metrics_collector.get_system_metrics()

            if not metrics_result.success:
                logger.error("Failed to get system metrics")
                return ServiceResult.fail("Failed to get system metrics")

            metrics_data = metrics_result.unwrap()

            # Format for API response
            response = {
                "cpu": metrics_data.get("cpu", {}),
                "memory": metrics_data.get("memory", {}),
                "disk": metrics_data.get("disk", {}),
                "network": metrics_data.get("network", {}),
                "processes": metrics_data.get("processes", {}),
                "timestamp": metrics_data["timestamp"],
            }

            return ServiceResult.ok(response)

        except Exception as e:
            logger.exception("Failed to get system metrics", error=str(e))
            return ServiceResult.fail(f"Failed to get system metrics: {e}")

    async def get_system_status(self) -> ServiceResult[dict]:
        """Get combined system status including health and metrics.

        Returns:
            ServiceResult containing combined health and metrics data.

        """
        try:
            # Get both health and metrics
            health_result = await self.get_health_status()
            metrics_result = await self.get_system_metrics()

            # Combine results
            response = {
                "health": (
                    health_result.data
                    if health_result.success
                    else {"status": "unknown"}
                ),
                "metrics": metrics_result.data if metrics_result.success else {},
                "overall_status": "healthy" if health_result.success else "unhealthy",
            }

            return ServiceResult.ok(response)

        except Exception as e:
            logger.exception("Failed to get system status", error=str(e))
            return ServiceResult.fail(f"Failed to get system status: {e}")

    async def backup_system(self, backup_type: str = "full") -> ServiceResult[dict]:
        """Create system backup.

        Args:
            backup_type: Type of backup to create (full or incremental).

        Returns:
            ServiceResult containing backup operation details.

        """
        try:
            logger.info("Starting system backup", backup_type=backup_type)

            # This would integrate with actual backup system
            # For now, return mock response
            backup_id = f"backup_{backup_type}_{hash(backup_type)}"

            response = {
                "backup_id": backup_id,
                "type": backup_type,
                "status": "completed",
                "started_at": "2025-07-09T00:00:00Z",
                "completed_at": "2025-07-09T00:01:00Z",
                "size": "1.2GB",
                "location": f"/backups/{backup_id}",
            }

            logger.info("System backup completed", backup_id=backup_id)

            return ServiceResult.ok(response)

        except Exception as e:
            logger.exception("System backup failed", error=str(e))
            return ServiceResult.fail(f"System backup failed: {e}")

    async def maintenance_mode(self, enabled: bool, message: str | None = None) -> ServiceResult[dict]:
        """Update system maintenance mode.

        Args:
            enabled: Whether maintenance mode should be enabled.
            message: Optional maintenance message.

        Returns:
            ServiceResult containing maintenance mode status.

        """
        try:
            logger.info("Maintenance mode change requested", enabled=enabled)

            # This would integrate with actual maintenance system
            # For now, return mock response
            response = {
                "enabled": enabled,
                "message": message
                or (
                    "Maintenance mode enabled"
                    if enabled
                    else "Maintenance mode disabled"
                ),
                "timestamp": "2025-07-09T00:00:00Z",
            }

            logger.info("Maintenance mode updated", enabled=enabled)

            return ServiceResult.ok(response)

        except Exception as e:
            logger.exception("Failed to update maintenance mode", error=str(e))
            return ServiceResult.fail(f"Failed to update maintenance mode: {e}")

    async def get_system_configuration(self) -> ServiceResult[dict]:
        """Get system configuration.

        Returns:
            ServiceResult containing system configuration data.

        """
        try:
            # This would return actual system configuration
            # For now, return mock response
            response = {
                "version": FlextFramework.VERSION,
                "environment": "production",
                "features": {
                    "auth": True,
                    "monitoring": True,
                    "backup": True,
                    "maintenance": True,
                },
                "limits": {
                    "max_pipelines": 1000,
                    "max_plugins": 100,
                    "max_concurrent_jobs": 50,
                },
            }

            return ServiceResult.ok(response)

        except Exception as e:
            logger.exception("Failed to get system configuration", error=str(e))
            return ServiceResult.fail(f"Failed to get system configuration: {e}")

    async def update_system_configuration(self, config: dict) -> ServiceResult[dict]:
        """Update system configuration.

        Args:
            config: Configuration dictionary with updates.

        Returns:
            ServiceResult containing update operation details.

        """
        try:
            logger.info("System configuration update requested", config=config)

            # This would update actual system configuration
            # For now, return mock response
            response = {
                "updated": True,
                "timestamp": "2025-07-09T00:00:00Z",
                "applied_changes": list(config.keys()),
            }

            logger.info("System configuration updated", changes=list(config.keys()))

            return ServiceResult.ok(response)

        except Exception as e:
            logger.exception("Failed to update system configuration", error=str(e))
            return ServiceResult.fail(f"Failed to update system configuration: {e}")

"""Service Status constants for flext-api domain.

Single responsibility module containing only service status constants.
"""

from __future__ import annotations

from flext_core import FlextConstants


class FlextApiServiceStatus(FlextConstants):
    """Service status constants for API operations."""

    class ServiceStatus:
        """Service status values."""

        STOPPED = "stopped"
        STARTING = "starting"
        RUNNING = "running"
        STOPPING = "stopping"
        ERROR = "error"
        MAINTENANCE = "maintenance"


__all__ = ["FlextApiServiceStatus"]

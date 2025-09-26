"""Logging Constants for flext-api domain.

Single responsibility module containing only logging constants.
"""

from __future__ import annotations

from flext_core import FlextConstants


class FlextApiLoggingConstants(FlextConstants):
    """Logging constants for API operations."""

    class ApiLogging:  # Renamed to avoid override conflict
        """API-specific logging configuration values."""

        DEFAULT_LEVEL = "INFO"
        DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        DEFAULT_FILE = "flext_api.log"
        MAX_FILE_SIZE = 10485760  # 10MB
        BACKUP_COUNT = 5


__all__ = ["FlextApiLoggingConstants"]

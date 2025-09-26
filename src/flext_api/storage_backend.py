"""Storage Backend constants for flext-api domain.

Single responsibility module containing only storage backend constants.
"""

from __future__ import annotations

from flext_core import FlextConstants


class FlextApiStorageBackend(FlextConstants):
    """Storage backend constants for API operations."""

    class StorageBackend:
        """Storage backend values."""

        MEMORY = "memory"
        FILE = "file"
        DATABASE = "database"
        REDIS = "redis"
        S3 = "s3"


__all__ = ["FlextApiStorageBackend"]

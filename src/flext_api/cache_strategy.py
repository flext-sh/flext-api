"""Cache Strategy constants for flext-api domain.

Single responsibility module containing only cache strategy constants.
"""

from __future__ import annotations

from flext_core import FlextConstants


class FlextApiCacheStrategy(FlextConstants):
    """Cache strategy constants for API operations."""

    class CacheStrategy:
        """Cache strategy values."""

        NONE = "none"
        MEMORY = "memory"
        REDIS = "redis"
        FILE = "file"


__all__ = ["FlextApiCacheStrategy"]

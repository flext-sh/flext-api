"""Legacy service_base module - DEPRECATED.

This module provides backward compatibility for removed base_service.py.
Following FLEXT refactoring patterns, all base services have been moved to flext-core.

DEPRECATED: Use flext_core.FlextDomainService directly instead.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "flext_api.service_base is deprecated. Use flext_core.FlextDomainService instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Legacy compatibility
try:
    from flext_core import FlextDomainService

    FlextApiBaseService = FlextDomainService  # type: ignore[assignment]
except ImportError:
    # Fallback if flext-core has import issues
    class FlextApiBaseService:  # type: ignore[no-redef]
        """Legacy compatibility class - replaced by FlextDomainService."""

        def __init__(self, **kwargs: object) -> None:
            pass


__all__ = ["FlextApiBaseService"]

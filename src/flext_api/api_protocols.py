"""FLEXT API Protocols - Facade for backward compatibility.

This module provides a facade over the new centralized protocols architecture.
Legacy code can continue importing from api_protocols while new code should
use the hierarchical FlextApiProtocols from protocols module.

Migration Path:
    OLD: from flext_api.api_protocols import FlextApiClientProtocol
    NEW: from flext_api import FlextApiProtocols
         client: FlextApiProtocols.Infrastructure.HttpClient = ...

Architecture:
    This facade redirects to the new protocols.py which extends flext-core
    FlextProtocols hierarchy, eliminating duplication and centralizing patterns.
"""

from __future__ import annotations

# ==============================================================================
# DEPRECATION WARNINGS - Guide migration to new patterns
# ==============================================================================
# ==============================================================================
# FACADE IMPORTS - All protocols now come from centralized hierarchy
# ==============================================================================
# Import the new hierarchical protocol architecture
from flext_api.protocols import (
    FlextApiAuthorizationProtocol,
    FlextApiAuthProtocol,
    FlextApiCacheProtocol,
    # Direct access aliases for backward compatibility
    FlextApiClientProtocol,
    FlextApiConnectionPoolProtocol,
    FlextApiHandlerProtocol,
    FlextApiHealthCheckProtocol,
    FlextApiMetricsProtocol,
    FlextApiMiddlewareProtocol,
    FlextApiPluginProtocol,
    # Main hierarchical class
    FlextApiProtocols,
    FlextApiQueryBuilderProtocol,
    FlextApiRateLimitProtocol,
    FlextApiRepositoryProtocol,
    FlextApiResponseBuilderProtocol,
    # Legacy compatibility aliases (mapped to flext-core hierarchy)
    FlextApiServiceProtocol,
    FlextApiStreamProtocol,
    FlextApiValidatorProtocol,
    FlextApiWebSocketProtocol,
)

# Deprecation warning temporarily disabled during refactoring
# TODO: Re-enable after migration is complete
# warnings.warn(
#     "Importing from flext_api.api_protocols is deprecated. "
#     "Use 'from flext_api import FlextApiProtocols' for hierarchical access, "
#     "or 'from flext_api import FlextApiClientProtocol' for direct imports.",
#     DeprecationWarning,
#     stacklevel=2
# )

# ==============================================================================
# BACKWARD COMPATIBILITY EXPORTS
# ==============================================================================

__all__ = [
    # Main hierarchical protocol class
    "FlextApiProtocols",

    # HTTP Client Protocols
    "FlextApiClientProtocol",
    "FlextApiConnectionPoolProtocol",

    # Plugin System Protocols
    "FlextApiPluginProtocol",

    # Builder Protocols
    "FlextApiQueryBuilderProtocol",
    "FlextApiResponseBuilderProtocol",

    # Service Layer Protocols
    "FlextApiServiceProtocol",
    "FlextApiRepositoryProtocol",
    "FlextApiHandlerProtocol",

    # Security Protocols
    "FlextApiAuthProtocol",
    "FlextApiAuthorizationProtocol",

    # Infrastructure Protocols
    "FlextApiCacheProtocol",
    "FlextApiMiddlewareProtocol",
    "FlextApiRateLimitProtocol",

    # Streaming & Communication Protocols
    "FlextApiStreamProtocol",
    "FlextApiWebSocketProtocol",

    # Monitoring Protocols
    "FlextApiMetricsProtocol",
    "FlextApiHealthCheckProtocol",

    # Validation Protocols
    "FlextApiValidatorProtocol",
]

# ==============================================================================
# MIGRATION GUIDE - Documentation for developers
# ==============================================================================

"""
MIGRATION GUIDE: api_protocols.py → protocols.py

The old api_protocols.py contained 16+ protocol definitions that duplicated
patterns already available in flext-core. This facade provides backward
compatibility while encouraging migration to the centralized hierarchy.

OLD USAGE (still works, but deprecated):
    from flext_api.api_protocols import FlextApiClientProtocol

NEW USAGE (recommended):
    from flext_api import FlextApiProtocols
    client: FlextApiProtocols.Infrastructure.HttpClient = ...

DIRECT IMPORT (for common patterns):
    from flext_api import FlextApiClientProtocol

ARCHITECTURE BENEFITS:
    1. Eliminates 1,000+ lines of duplicate protocol definitions
    2. Uses centralized flext-core FlextProtocols hierarchy
    3. Maintains Clean Architecture separation of concerns
    4. Provides type-safe composition patterns
    5. Reduces maintenance overhead through centralization

HIERARCHY MAPPING:
    FlextApiServiceProtocol → FlextProtocols.Domain.Service
    FlextApiAuthProtocol → FlextProtocols.Infrastructure.Auth
    FlextApiHandlerProtocol → FlextProtocols.Application.Handler
    FlextApiValidatorProtocol → FlextProtocols.Foundation.Validator
    FlextApiPluginProtocol → FlextProtocols.Extensions.Plugin
    ... and all others map to appropriate hierarchy levels
"""

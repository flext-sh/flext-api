"""FLEXT API - Enterprise FastAPI Gateway with simplified imports.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Version 0.1.0 - Simplified public API with backward compatibility:
- All common imports available from root: from flext_api import ServiceResult
- Deprecation warnings for internal imports
- 100% backward compatibility maintained
"""

from __future__ import annotations

import warnings

# Import ONLY from flext-core - NO FALLBACKS (ZERO TOLERANCE)
from flext_core import (
    BaseSettings as APIBaseConfig,  # Configuration base class
    DomainBaseModel as BaseModel,  # Base for all API models
    DomainError,  # Business logic errors
    ServiceResult,  # Result pattern for API endpoints
    ValidationError,  # Validation errors
)

__version__ = "0.1.0"


class FlextAPIDeprecationWarning(DeprecationWarning):
    """Custom deprecation warning for FLEXT API import changes."""


def _show_deprecation_warning(old_import: str, new_import: str) -> None:
    """Show deprecation warning for import paths."""
    message_parts = [
        f"⚠️  DEPRECATED IMPORT: {old_import}",
        f"✅ USE INSTEAD: {new_import}",
        "🔗 This will be removed in version 1.0.0",
        "📖 See FLEXT API docs for migration guide",
    ]
    warnings.warn(
        "\n".join(message_parts),
        FlextAPIDeprecationWarning,
        stacklevel=3,
    )


# ================================
# PUBLIC API EXPORTS
# ================================

__all__ = [
    "APIBaseConfig",       # from flext_api import APIBaseConfig
    "BaseModel",           # from flext_api import BaseModel
    "DomainError",         # from flext_api import DomainError
    # Deprecation utilities
    "FlextAPIDeprecationWarning",
    # Core Patterns (from flext-core)
    "ServiceResult",        # from flext_api import ServiceResult
    "ValidationError",     # from flext_api import ValidationError
    # Version
    "__version__",
]

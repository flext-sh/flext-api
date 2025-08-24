"""Legacy compatibility facade for base_service -> service_base migration.

DEPRECATED: Use service_base module instead.
This facade maintains backward compatibility during PEP8 migration.
"""

from __future__ import annotations

import warnings

# Facade import - redirect to PEP8 module
from flext_api.service_base import *  # type: ignore[misc] # noqa: F403,F401

# Deprecation warning for legacy usage
warnings.warn(
    "base_service is deprecated. Use service_base instead.",
    DeprecationWarning,
    stacklevel=2,
)
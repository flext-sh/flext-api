"""Legacy facade for types - DEPRECATED.

Use flext_api.typings.FlextTypes instead.
This module exists only for backward compatibility during migration.
"""

from __future__ import annotations

import warnings

# Import everything from the consolidated typings module
from flext_api.typings import *  # type: ignore[assignment] # noqa: F403,F401

# Deprecation warning for legacy usage
warnings.warn(
    "flext_api.types is deprecated, use flext_api.typings.FlextTypes instead",
    DeprecationWarning,
    stacklevel=2,
)

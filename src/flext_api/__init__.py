"""High-performance REST API library for FLEXT ecosystem.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

# ruff: noqa: F403
# Import all from each module following flext-core pattern
from flext_api.api import *
from flext_api.app import *

# builders.py eliminated - functionality consolidated into client.py
from flext_api.client import *
from flext_api.config import *
from flext_api.constants import *
from flext_api.exceptions import *
from flext_api.models import *
from flext_api.plugins import *
from flext_api.protocols import *
from flext_api.storage import *
from flext_api.types import *
from flext_api.typings import *  # type: ignore[assignment]
from flext_api.utilities import *

# Legacy aliases for backward compatibility with removed base_service.py
# Note: FlextApiBaseService was removed following FLEXT consolidation patterns
# Tests should migrate to use flext_core.FlextDomainService or object directly
try:
    from flext_core import FlextDomainService

    FlextApiBaseService = FlextDomainService  # type: ignore[misc]
except ImportError:
    # Fallback if flext-core has import issues
    class FlextApiBaseService:  # type: ignore[no-redef]
        """Legacy compatibility class - replaced by FlextDomainService."""

        def __init__(self, **kwargs: object) -> None:
            pass


# Version information
__version__ = FLEXT_API_VERSION

# Note: __all__ is constructed dynamically at runtime from imported modules
# This pattern is necessary for library aggregation but causes pyright warnings
__all__: list[str] = [
    # Legacy aliases
    "FlextApiBaseService",
    # Version
    "__version__",
]

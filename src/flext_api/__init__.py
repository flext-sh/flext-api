"""FLEXT API - HTTP Foundation Library.

Streamlined HTTP client and API foundation for FLEXT ecosystem.
Direct usage of flext-core patterns without over-engineering.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.client import FlextApiClient
from flext_api.config import FlextApiConfig
from flext_api.constants import FlextApiConstants
from flext_api.exceptions import FlextApiExceptions
from flext_api.models import FlextApiModels
from flext_api.storage import FlextApiStorage
from flext_api.utilities import FlextApiUtilities

# Backward compatibility exports for ecosystem integration
MIN_PORT = FlextApiConstants.MIN_PORT
MAX_PORT = FlextApiConstants.MAX_PORT
FlextApiEndpoints = FlextApiConstants.FlextApiEndpoints
FlextApiFieldType = FlextApiConstants.FlextApiFieldType
FlextApiStatus = FlextApiConstants.FlextApiStatus

# Version information
__version__ = "0.9.0"

__all__ = [
    "MAX_PORT",
    "MIN_PORT",
    "FlextApiClient",
    "FlextApiConfig",
    "FlextApiConstants",
    "FlextApiEndpoints",
    "FlextApiExceptions",
    "FlextApiFieldType",
    "FlextApiModels",
    "FlextApiStatus",
    "FlextApiStorage",
    "FlextApiUtilities",
    "__version__",
]

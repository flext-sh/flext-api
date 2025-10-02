"""FLEXT API - HTTP Foundation Library.

Streamlined HTTP client and API foundation for FLEXT ecosystem.
Direct usage of flext-core patterns without over-engineering.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.api import FlextApi
from flext_api.app import FlextApiApp
from flext_api.client import FlextApiClient
from flext_api.config import FlextApiConfig
from flext_api.constants import FlextApiConstants
from flext_api.exceptions import FlextApiExceptions
from flext_api.models import FlextApiModels
from flext_api.protocols import FlextApiProtocols
from flext_api.storage import FlextApiStorage
from flext_api.typings import FlextApiTypes
from flext_api.utilities import FlextApiUtilities

__version__ = "0.9.0"

__all__ = [
    "FlextApi",
    "FlextApiApp",
    "FlextApiClient",
    "FlextApiConfig",
    "FlextApiConstants",
    "FlextApiExceptions",
    "FlextApiModels",
    "FlextApiProtocols",
    "FlextApiStorage",
    "FlextApiTypes",
    "FlextApiUtilities",
    "__version__",
]

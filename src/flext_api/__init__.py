"""FLEXT API - HTTP Foundation Library for FLEXT Ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.client import FlextApiClient
from flext_api.config import FlextApiConfig
from flext_api.constants import FlextApiConstants
from flext_api.enums import StorageBackend
from flext_api.exceptions import FlextApiExceptions
from flext_api.factory import create_flext_api
from flext_api.models import FlextApiModels
from flext_api.protocols import FlextApiProtocols
from flext_api.storage import FlextApiStorage
from flext_api.typings import FlextApiTypes
from flext_api.utilities import FlextApiUtilities

# Version information
__version__ = "0.9.0"

# Re-export classes from models for convenience
HttpRequest = FlextApiModels.HttpRequest
HttpResponse = FlextApiModels.HttpResponse
PaginationConfig = FlextApiModels.PaginationConfig

# Explicit __all__ definition
__all__ = [
    "FlextApiClient",
    "FlextApiConfig",
    "FlextApiConstants",
    "FlextApiExceptions",
    "FlextApiModels",
    "FlextApiProtocols",
    "FlextApiStorage",
    "FlextApiTypes",
    "FlextApiUtilities",
    "HttpRequest",
    "HttpResponse",
    "PaginationConfig",
    "StorageBackend",
    "__version__",
    "create_flext_api",
]

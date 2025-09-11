"""FLEXT API - HTTP Foundation Library for FLEXT Ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from enum import StrEnum

# Explicit imports from each module
from flext_api.client import FlextApiClient
from flext_api.config import FlextApiConfig
from flext_api.constants import FlextApiConstants
from flext_api.exceptions import FlextApiExceptions
from flext_api.models import FlextApiModels
from flext_api.protocols import FlextApiProtocols
from flext_api.storage import FlextApiStorage
from flext_api.typings import FlextApiTypes
from flext_api.utilities import FlextApiUtilities

# Version information
__version__ = "0.9.0"


# Add additional exports that are not automatically collected
class StorageBackend(StrEnum):
    """Storage backend types for flext-api."""

    MEMORY = "memory"
    FILE = "file"
    REDIS = "redis"
    DATABASE = "database"


# Re-export classes from models for convenience
StorageConfig = FlextApiModels.StorageConfig
URL = FlextApiModels.URL
ApiRequest = FlextApiModels.ApiRequest


def create_flext_api() -> FlextApiClient:
    """Create and return a new FlextApiClient instance.

    Returns:
        FlextApiClient: A configured HTTP client instance.

    """
    return FlextApiClient(base_url="https://api.example.com")


# Explicit __all__ definition
__all__ = [
    "URL",
    "ApiRequest",
    # Main classes from modules
    "FlextApiClient",
    "FlextApiConfig",
    "FlextApiConstants",
    "FlextApiExceptions",
    "FlextApiModels",
    "FlextApiProtocols",
    "FlextApiStorage",
    "FlextApiTypes",
    "FlextApiUtilities",
    # Additional exports
    "StorageBackend",
    "StorageConfig",
    # Version
    "__version__",
    "create_flext_api",
]

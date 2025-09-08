"""FLEXT API - HTTP Foundation Library for FLEXT Ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations
from flext_core import FlextTypes

from enum import StrEnum


# Import all modules with proper type handling
from flext_api.models import *
from flext_api.models import FlextApiModels
from flext_api.client import *
from flext_api.client import FlextApiClient
from flext_api.storage import *
from flext_api.config import *
from flext_api.constants import *
from flext_api.constants import FlextApiConstants
from flext_api.exceptions import *
from flext_api.utilities import *
from flext_api.protocols import *
from flext_api.typings import *

# Collect all exports from modules dynamically - FLEXT Pattern
import flext_api.client as _client
import flext_api.storage as _storage
import flext_api.models as _models
import flext_api.config as _config
import flext_api.constants as _constants
import flext_api.exceptions as _exceptions
import flext_api.utilities as _utilities
import flext_api.protocols as _protocols
import flext_api.typings as _typings

# Version information
__version__ = "0.9.0"

# Build __all__ from actual module exports - FLEXT Pattern
_export_modules = [
    _client,
    _storage,
    _models,
    _config,
    _constants,
    _exceptions,
    _utilities,
    _protocols,
    _typings,
]
_collected: FlextTypes.Core.StringList = []
for _m in _export_modules:
    names = getattr(_m, "__all__", [])
    if isinstance(names, (list, tuple)):
        _collected.extend(str(n) for n in names)


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
    return FlextApiClient()


# Add manually exported items to __all__
_manual_exports = [
    "StorageBackend",
    "StorageConfig",
    "URL",
    "ApiRequest",
    "FlextApiConstants",
    "FlextApiModels",
    "create_flext_api",
]

__all__ = tuple(sorted(set(_collected + _manual_exports)))

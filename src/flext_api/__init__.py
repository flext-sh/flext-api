"""FLEXT API - HTTP Foundation Library with acknowledged complexity.

Note: Implementation includes comprehensive features that may be
over-engineered for simple HTTP scenarios. Consider basic Python
httpx/requests for simple applications.

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
    "StorageBackend",
    "__version__",
    "create_flext_api",
]

"""FLEXT API - HTTP Foundation Library.

Streamlined HTTP client and API foundation for FLEXT ecosystem.
Direct usage of flext-core patterns without over-engineering.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Final

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
from flext_api.version import VERSION, FlextApiVersion

PROJECT_VERSION: Final[FlextApiVersion] = VERSION

__version__: str = VERSION.version
__version_info__: tuple[int | str, ...] = VERSION.version_info

__all__ = [
    "PROJECT_VERSION",
    "VERSION",
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
    "FlextApiVersion",
    "__version__",
    "__version_info__",
]

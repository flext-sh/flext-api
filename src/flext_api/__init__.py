"""FLEXT API - HTTP Foundation Library.

FlextApi provides a streamlined HTTP client and API foundation for the FLEXT ecosystem,
offering enterprise-grade HTTP operations with flext-core patterns. This library serves
as the HTTP foundation for 33+ FLEXT projects, eliminating implementation duplication
while maintaining enterprise-grade patterns.

The library provides:
    - HTTP client with automatic retry and timeout handling
    - FastAPI application factory with flext-core integration
    - Request/response models with Pydantic v2 validation
    - Configuration management with environment integration
    - Storage abstraction for various backends
    - Protocol definitions for extensible HTTP operations

All components follow flext-core patterns including:
    - FlextResult for railway-oriented error handling
    - FlextService for dependency injection
    - FlextModels for type-safe data validation
    - Structured logging throughout

Args:
    None

Returns:
    None

Example:
    >>>
    >>> # Configure HTTP client
    >>> config = FlextApiConfig(base_url="https://api.example.com")
    >>>
    >>> # Make HTTP requests with automatic error handling
    >>> result = client.get("/users")
    >>> if result.is_success:
    >>>     users = result.unwrap()
    >>>
    >>> # Create FastAPI application
    >>> from flext_api import FlextApiApp
    >>> app = FlextApiApp()
    >>> # Add routes and middleware...

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_api import client as _client_module
from flext_api.__version__ import __version__, __version_info__
from flext_api.api import FlextWebApi
from flext_api.app import FlextApiApp
from flext_api.client import FlextApiClient
from flext_api.config import FlextWebConfig
from flext_api.config_manager import HttpConfigManager
from flext_api.constants import FlextApiConstants
from flext_api.exceptions import FlextApiExceptions
from flext_api.http_operations import HttpOperations
from flext_api.lifecycle_manager import HttpLifecycleManager
from flext_api.models import FlextApiModels
from flext_api.protocols import HttpProtocols
from flext_api.server_factory import FlextApiServerFactory
from flext_api.storage import FlextApiStorage
from flext_api.typings import FlextApiTypes
from flext_api.utilities import FlextApiUtilities

__all__ = [
    "FlextApiApp",
    "FlextApiClient",
    "FlextApiConstants",
    "FlextApiExceptions",
    "FlextApiServerFactory",
    "FlextApiStorage",
    "FlextApiTypes",
    "FlextApiUtilities",
    "FlextWebApi",
    "FlextWebConfig",
    "HttpConfigManager",
    "HttpLifecycleManager",
    "FlextApiModels",
    "HttpOperations",
    "HttpProtocols",
    "__version__",
    "__version_info__",
    "_client_module",
]

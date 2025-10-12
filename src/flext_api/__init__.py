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
    - FlextCore.Result for railway-oriented error handling
    - FlextCore.Service for dependency injection
    - FlextCore.Models for type-safe data validation
    - Structured logging throughout

Args:
    None

Returns:
    None

Example:
    >>> from flext_api import FlextApiClient, FlextApiConfig
    >>>
    >>> # Configure HTTP client
    >>> config = FlextApiConfig(base_url="https://api.example.com")
    >>> client = FlextApiClient(config)
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
from flext_api.adapters import FlextApiAdapters
from flext_api.api import FlextApi
from flext_api.app import FlextApiApp
from flext_api.config import FlextApiConfig
from flext_api.constants import FlextApiConstants
from flext_api.exceptions import FlextApiExceptions
from flext_api.handlers import FlextApiHandlers
from flext_api.models import FlextApiModels
from flext_api.protocols import FlextApiProtocols
from flext_api.storage import FlextApiStorage
from flext_api.typings import FlextApiTypes
from flext_api.utilities import FlextApiUtilities

__all__ = [
    "FlextApi",
    "FlextApiAdapters",
    "FlextApiApp",
    "FlextApiClient",
    "FlextApiConfig",
    "FlextApiConstants",
    "FlextApiExceptions",
    "FlextApiHandlers",
    "FlextApiModels",
    "FlextApiProtocols",
    "FlextApiStorage",
    "FlextApiTypes",
    "FlextApiUtilities",
    "__version__",
    "__version_info__",
    "_client_module",
]

# Make FlextApiClient available at package level
# Import the client module which contains the FlextApiClient class
# Import FlextApiClient directly from the client module to avoid circular imports
try:
    from flext_api.client.client import FlextApiClient
except ImportError:
    # Fallback for development
    FlextApiClient = None

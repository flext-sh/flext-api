"""FLEXT API - HTTP Foundation Library.

Unified HTTP API facade for FLEXT ecosystem.

Provides unified HTTP operations serving as single entry point for
HTTP functionality across projects with consistent patterns.

Architecture Layer: Application API Layer (Layer 3+)
- Single Entry Point: FlextApi unified facade
- Models: FlextApiModels extending flext-core FlextModels
- Foundation: Uses flext-core r, FlextService, FlextModels

Core Features:
    - Unified FlextApi facade (single entry point)
    - Railway-oriented error handling (r[T])
    - HTTP client abstraction with retry/timeout
    Pydantic v2 models with validation (Value Objects)
    Clean Architecture with domain-driven design
    FastAPI application factory
    Zero tolerance for custom HTTP implementations

Critical Rule - Zero Tolerance:
    🔴 NO direct httpx imports outside flext-api infrastructure
    🔴 NO custom HTTP implementations in ecosystem
    🔴 🟢 ALL HTTP operations through FlextApi facade
    🟢 ALL models use FlextApiModels (extends FlextModels)
    🟢 ALL errors return r[T] (railway pattern)

Import Pattern (Root imports only):

Correct - Always use root imports:
    from flext_api import (
        FlextApi,              # Main facade
        FlextApiModels,        # HTTP domain models
        FlextApiSettings,        # Configuration
        FlextApiConstants,     # Constants
        FlextApiProtocols,     # Protocol definitions
    )

Forbidden - Never use internal imports:
    from flext_api import FlextApi  # Wrong - use root import
    from flext_api import FlextApiModels  # Wrong - use root import

Why: 33+ ecosystem projects rely on root imports. Internal imports break
the entire ecosystem by creating circular dependencies and import order issues.

USAGE EXAMPLES:

Example 1: Simple HTTP GET:
    >>> from flext_api import FlextApi
    >>> api = FlextApi()
    >>> result = api.get("https://api.example.com/users")
    >>> if result.is_success:
    ...     response = result.value
    ...     print(f"Status: {response.status_code}")

Example 2: HTTP POST with data:
    >>> result = api.post(
    ...     "https://api.example.com/users",
    ...     data={"name": "John", "email": "john@example.com"},
    ...     headers={"Content-Type": "application/json"},
    ... )

Example 3: Using models with validation:
    >>> request = api.Models.HttpRequest(
    ...     method="GET",
    ...     url="https://api.example.com/users",
    ...     timeout=c.Api.DEFAULT_TIMEOUT,
    ... )
    >>> result = api.request(request)

Example 4: Configuration:
    >>> config = api.Models.ClientConfig(
    ...     base_url="https://api.example.com",
    ...     timeout=c.Api.DEFAULT_TIMEOUT,
    ...     max_retries=c.Api.DEFAULT_MAX_RETRIES,
    ... )
    >>> api.reconfigure(api.Config(base_url="https://api.example.com"))

FLEXT ECOSYSTEM INTEGRATION:
    - Foundation: FlextApi (unified facade)
    - Models: FlextApiModels extending flext-core
    - Patterns: Railway-oriented (r[T])
    - Architecture: Clean Architecture, SOLID principles

**19 EXPORTED CLASSES** (organized by responsibility):

1. Main Facade:
   - FlextApi - Unified HTTP API entry point

2. Domain Models:
   - FlextApiModels - HTTP domain models (Value Objects)

3. Configuration:
   - FlextApiSettings - HTTP configuration
   - FlextApiConstants - HTTP constants
   - FlextApiSettingsManager - Configuration management

4. Infrastructure:
   - FlextApiClient - HTTP client implementation
   - FlextApiApp - FastAPI application factory
   - FlextApiLifecycleManager - Resource lifecycle
   - (FlextApiOperations removed - use FlextApi or FlextApiClient directly)
   - FlextApiStorage - Storage abstraction
   - FlextApiAdapters - Protocol adapters

5. Type System:
   - FlextApiTypes - Type definitions
   - FlextApiProtocols - Protocol definitions

6. Utilities:
   - FlextApiUtilities - HTTP utilities

7. Exceptions:
   - FlextHttpError - HTTP exceptions

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_api._lazy_exports import (
    __dir__ as __dir__,
    __getattr__ as __getattr__,
)

__all__ = [
    "AsyncAPISchemaValidator",
    "BaseProtocolImplementation",
    "FlextApi",
    "FlextApiAdapters",
    "FlextApiApp",
    "FlextApiClient",
    "FlextApiConstants",
    "FlextApiLifecycleManager",
    "FlextApiModels",
    "FlextApiPlugins",
    "FlextApiProtocols",
    "FlextApiServerFactory",
    "FlextApiSettings",
    "FlextApiSettingsManager",
    "FlextApiStorage",
    "FlextApiTypes",
    "FlextApiUtilities",
    "FlextWebClientImplementation",
    "FlextWebProtocolPlugin",
    "HttpError",
    "JSONSchemaValidator",
    "OpenAPISchemaValidator",
    "RFCProtocolImplementation",
    "SSEProtocolPlugin",
    "StorageBackendImplementation",
    "WebSocketProtocolPlugin",
    "__version__",
    "__version_info__",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "u",
    "x",
]

if TYPE_CHECKING:
    from flext_core import (
        FlextDecorators as d,
        FlextExceptions as e,
        FlextHandlers as h,
        FlextMixins as x,
        FlextService as s,
        r as r,
    )

    from flext_api.__version__ import (
        __version__ as __version__,
        __version_info__ as __version_info__,
    )
    from flext_api.adapters import FlextApiAdapters as FlextApiAdapters
    from flext_api.api import FlextApi as FlextApi
    from flext_api.app import FlextApiApp as FlextApiApp
    from flext_api.client import FlextApiClient as FlextApiClient
    from flext_api.constants import (
        FlextApiConstants as FlextApiConstants,
        FlextApiConstants as c,
    )
    from flext_api.exceptions import HttpError as HttpError
    from flext_api.lifecycle_manager import (
        FlextApiLifecycleManager as FlextApiLifecycleManager,
    )
    from flext_api.models import FlextApiModels as FlextApiModels, FlextApiModels as m
    from flext_api.plugins import FlextApiPlugins as FlextApiPlugins
    from flext_api.protocol_impls import (
        BaseProtocolImplementation as BaseProtocolImplementation,
        FlextWebClientImplementation as FlextWebClientImplementation,
        FlextWebProtocolPlugin as FlextWebProtocolPlugin,
        RFCProtocolImplementation as RFCProtocolImplementation,
        SSEProtocolPlugin as SSEProtocolPlugin,
        StorageBackendImplementation as StorageBackendImplementation,
        WebSocketProtocolPlugin as WebSocketProtocolPlugin,
    )
    from flext_api.protocols import (
        FlextApiProtocols as FlextApiProtocols,
        FlextApiProtocols as p,
    )
    from flext_api.schemas import (
        AsyncAPISchemaValidator as AsyncAPISchemaValidator,
        JSONSchemaValidator as JSONSchemaValidator,
        OpenAPISchemaValidator as OpenAPISchemaValidator,
    )
    from flext_api.server_factory import FlextApiServerFactory as FlextApiServerFactory
    from flext_api.settings import FlextApiSettings as FlextApiSettings
    from flext_api.settings_manager import (
        FlextApiSettingsManager as FlextApiSettingsManager,
    )
    from flext_api.storage import FlextApiStorage as FlextApiStorage
    from flext_api.typings import FlextApiTypes as FlextApiTypes, FlextApiTypes as t
    from flext_api.utilities import (
        FlextApiUtilities as FlextApiUtilities,
        FlextApiUtilities as u,
    )

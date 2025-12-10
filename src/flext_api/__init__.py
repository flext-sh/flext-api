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
        FlextApiConfig,        # Configuration
        FlextApiConstants,     # Constants
        FlextApiProtocols,     # Protocol definitions
    )

Forbidden - Never use internal imports:
    from flext_api.api import FlextApi  # Wrong - use root import
    from flext_api.models import FlextApiModels  # Wrong - use root import

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
    ...     method="GET", url="https://api.example.com/users", timeout=30.0
    ... )
    >>> result = api.request(request)

Example 4: Configuration:
    >>> config = api.Models.ClientConfig(
    ...     base_url="https://api.example.com", timeout=30.0, max_retries=3
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
   - FlextApiConfig - HTTP configuration
   - FlextApiConstants - HTTP constants
   - FlextApiConfigManager - Configuration management

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

from flext_core import (
    FlextDecorators,
    FlextExceptions,
    FlextHandlers,
    FlextMixins,
    FlextResult,
    FlextService,
)

from flext_api.__version__ import __version__, __version_info__
from flext_api.adapters import FlextApiAdapters
from flext_api.api import FlextApi
from flext_api.app import FlextApiApp
from flext_api.client import FlextApiClient
from flext_api.config import FlextApiConfig
from flext_api.config_manager import FlextApiConfigManager
from flext_api.constants import FlextApiConstants
from flext_api.exceptions import HttpError

# FlextApiOperations removed - use FlextApi or FlextApiClient directly
from flext_api.lifecycle_manager import FlextApiLifecycleManager
from flext_api.models import FlextApiModels
from flext_api.protocols import FlextApiProtocols
from flext_api.server_factory import FlextApiServerFactory
from flext_api.storage import FlextApiStorage
from flext_api.typings import FlextApiTypes
from flext_api.utilities import FlextApiUtilities

# Domain-specific aliases (extending flext-core base classes)
u = FlextApiUtilities  # Utilities (FlextApiUtilities extends FlextUtilities)
m = FlextApiModels  # Models (FlextApiModels extends FlextModels)
c = FlextApiConstants  # Constants (FlextApiConstants extends FlextConstants)
t = FlextApiTypes  # Types (FlextApiTypes extends FlextTypes)
p = FlextApiProtocols  # Protocols (FlextApiProtocols extends FlextProtocols)

r = FlextResult  # Shared from flext-core
e = FlextExceptions  # Shared from flext-core
d = FlextDecorators  # Shared from flext-core
s = FlextService  # Shared from flext-core
x = FlextMixins  # Shared from flext-core
h = FlextHandlers  # Shared from flext-core

__all__ = [
    "FlextApi",
    "FlextApiAdapters",
    "FlextApiApp",
    "FlextApiClient",
    "FlextApiConfig",
    "FlextApiConfigManager",
    "FlextApiConstants",
    "FlextApiLifecycleManager",
    "FlextApiModels",
    "FlextApiProtocols",
    "FlextApiServerFactory",
    "FlextApiStorage",
    "FlextApiTypes",
    "FlextApiUtilities",
    "HttpError",
    "__version__",
    "__version_info__",
    # Domain-specific aliases
    "c",
    # Global aliases
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

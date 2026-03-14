# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
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

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes

    from flext_api.__version__ import (
        __all__,
        __author__,
        __author_email__,
        __description__,
        __license__,
        __title__,
        __url__,
    )
    from flext_api.adapters import FlextApiAdapters
    from flext_api.api import FlextApi
    from flext_api.app import FlextApiApp
    from flext_api.client import FlextApiClient
    from flext_api.constants import FlextApiConstants, c
    from flext_api.exceptions import HttpError
    from flext_api.lifecycle_manager import FlextApiLifecycleManager
    from flext_api.middleware import FlextApiMiddleware
    from flext_api.models import FlextApiModels, m
    from flext_api.plugins import FlextApiPlugins
    from flext_api.protocol_impls.base import BaseProtocolImplementation
    from flext_api.protocol_impls.http import FlextWebProtocolPlugin
    from flext_api.protocol_impls.http_client import FlextWebClientImplementation
    from flext_api.protocol_impls.logger import LoggerProtocolImplementation
    from flext_api.protocol_impls.rfc import RFCProtocolImplementation
    from flext_api.protocol_impls.sse import SSEProtocolPlugin
    from flext_api.protocol_impls.storage_backend import StorageBackendImplementation
    from flext_api.protocol_impls.websocket import WebSocketProtocolPlugin
    from flext_api.protocols import FlextApiProtocols, p
    from flext_api.registry import FlextApiRegistry
    from flext_api.schemas.asyncapi import AsyncAPISchemaValidator
    from flext_api.schemas.jsonschema import JSONSchemaValidator
    from flext_api.schemas.openapi import OpenAPISchemaValidator
    from flext_api.serializers import FlextApiSerializers
    from flext_api.server import FlextApiServer
    from flext_api.server_factory import FlextApiServerFactory
    from flext_api.settings import FlextApiSettings
    from flext_api.settings_manager import FlextApiSettingsManager
    from flext_api.storage import FlextApiStorage
    from flext_api.transports import FlextApiTransports
    from flext_api.typings import FlextApiTypes, t
    from flext_api.utilities import FlextApiUtilities, u
    from flext_api.webhook import FlextWebhookHandler

# Lazy import mapping: export_name -> (module_path, attr_name)
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "AsyncAPISchemaValidator": (
        "flext_api.schemas.asyncapi",
        "AsyncAPISchemaValidator",
    ),
    "BaseProtocolImplementation": (
        "flext_api.protocol_impls.base",
        "BaseProtocolImplementation",
    ),
    "FlextApi": ("flext_api.api", "FlextApi"),
    "FlextApiAdapters": ("flext_api.adapters", "FlextApiAdapters"),
    "FlextApiApp": ("flext_api.app", "FlextApiApp"),
    "FlextApiClient": ("flext_api.client", "FlextApiClient"),
    "FlextApiConstants": ("flext_api.constants", "FlextApiConstants"),
    "FlextApiLifecycleManager": (
        "flext_api.lifecycle_manager",
        "FlextApiLifecycleManager",
    ),
    "FlextApiMiddleware": ("flext_api.middleware", "FlextApiMiddleware"),
    "FlextApiModels": ("flext_api.models", "FlextApiModels"),
    "FlextApiPlugins": ("flext_api.plugins", "FlextApiPlugins"),
    "FlextApiProtocols": ("flext_api.protocols", "FlextApiProtocols"),
    "FlextApiRegistry": ("flext_api.registry", "FlextApiRegistry"),
    "FlextApiSerializers": ("flext_api.serializers", "FlextApiSerializers"),
    "FlextApiServer": ("flext_api.server", "FlextApiServer"),
    "FlextApiServerFactory": ("flext_api.server_factory", "FlextApiServerFactory"),
    "FlextApiSettings": ("flext_api.settings", "FlextApiSettings"),
    "FlextApiSettingsManager": (
        "flext_api.settings_manager",
        "FlextApiSettingsManager",
    ),
    "FlextApiStorage": ("flext_api.storage", "FlextApiStorage"),
    "FlextApiTransports": ("flext_api.transports", "FlextApiTransports"),
    "FlextApiTypes": ("flext_api.typings", "FlextApiTypes"),
    "FlextApiUtilities": ("flext_api.utilities", "FlextApiUtilities"),
    "FlextWebClientImplementation": (
        "flext_api.protocol_impls.http_client",
        "FlextWebClientImplementation",
    ),
    "FlextWebProtocolPlugin": (
        "flext_api.protocol_impls.http",
        "FlextWebProtocolPlugin",
    ),
    "FlextWebhookHandler": ("flext_api.webhook", "FlextWebhookHandler"),
    "HttpError": ("flext_api.exceptions", "HttpError"),
    "JSONSchemaValidator": ("flext_api.schemas.jsonschema", "JSONSchemaValidator"),
    "LoggerProtocolImplementation": (
        "flext_api.protocol_impls.logger",
        "LoggerProtocolImplementation",
    ),
    "OpenAPISchemaValidator": ("flext_api.schemas.openapi", "OpenAPISchemaValidator"),
    "RFCProtocolImplementation": (
        "flext_api.protocol_impls.rfc",
        "RFCProtocolImplementation",
    ),
    "SSEProtocolPlugin": ("flext_api.protocol_impls.sse", "SSEProtocolPlugin"),
    "StorageBackendImplementation": (
        "flext_api.protocol_impls.storage_backend",
        "StorageBackendImplementation",
    ),
    "WebSocketProtocolPlugin": (
        "flext_api.protocol_impls.websocket",
        "WebSocketProtocolPlugin",
    ),
    "__all__": ("flext_api.__version__", "__all__"),
    "__author__": ("flext_api.__version__", "__author__"),
    "__author_email__": ("flext_api.__version__", "__author_email__"),
    "__description__": ("flext_api.__version__", "__description__"),
    "__license__": ("flext_api.__version__", "__license__"),
    "__title__": ("flext_api.__version__", "__title__"),
    "__url__": ("flext_api.__version__", "__url__"),
    "c": ("flext_api.constants", "c"),
    "m": ("flext_api.models", "m"),
    "p": ("flext_api.protocols", "p"),
    "t": ("flext_api.typings", "t"),
    "u": ("flext_api.utilities", "u"),
}

__all__ = [
    "AsyncAPISchemaValidator",
    "BaseProtocolImplementation",
    "FlextApi",
    "FlextApiAdapters",
    "FlextApiApp",
    "FlextApiClient",
    "FlextApiConstants",
    "FlextApiLifecycleManager",
    "FlextApiMiddleware",
    "FlextApiModels",
    "FlextApiPlugins",
    "FlextApiProtocols",
    "FlextApiRegistry",
    "FlextApiSerializers",
    "FlextApiServer",
    "FlextApiServerFactory",
    "FlextApiSettings",
    "FlextApiSettingsManager",
    "FlextApiStorage",
    "FlextApiTransports",
    "FlextApiTypes",
    "FlextApiUtilities",
    "FlextWebClientImplementation",
    "FlextWebProtocolPlugin",
    "FlextWebhookHandler",
    "HttpError",
    "JSONSchemaValidator",
    "LoggerProtocolImplementation",
    "OpenAPISchemaValidator",
    "RFCProtocolImplementation",
    "SSEProtocolPlugin",
    "StorageBackendImplementation",
    "WebSocketProtocolPlugin",
    "__all__",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "c",
    "m",
    "p",
    "t",
    "u",
]


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)

# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Flext api package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core import d, e, h, r, s, x
    from flext_core.typings import FlextTypes

    from flext_api import protocol_impls, schemas
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
    "d": ("flext_core", "d"),
    "e": ("flext_core", "e"),
    "h": ("flext_core", "h"),
    "m": ("flext_api.models", "m"),
    "p": ("flext_api.protocols", "p"),
    "protocol_impls": ("flext_api.protocol_impls", ""),
    "r": ("flext_core", "r"),
    "s": ("flext_core", "s"),
    "schemas": ("flext_api.schemas", ""),
    "t": ("flext_api.typings", "t"),
    "u": ("flext_api.utilities", "u"),
    "x": ("flext_core", "x"),
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
    "d",
    "e",
    "h",
    "m",
    "p",
    "protocol_impls",
    "r",
    "s",
    "schemas",
    "t",
    "u",
    "x",
]


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)

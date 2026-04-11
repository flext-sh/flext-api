# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api package."""

from __future__ import annotations

import typing as _t

from flext_api.__version__ import *
from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

if _t.TYPE_CHECKING:
    from flext_cli import d, e, h, r, s, x

    from flext_api._protocols.plugins import FlextApiPlugins
    from flext_api._protocols.serialization import FlextApiProtocolsSerialization
    from flext_api._protocols.transports import FlextApiTransports
    from flext_api._typings.serialization import FlextApiTypingsSerialization
    from flext_api._utilities.adapters import FlextApiAdapters
    from flext_api._utilities.app import FlextApiApp
    from flext_api._utilities.client import FlextApiClient
    from flext_api._utilities.lifecycle_manager import FlextApiLifecycleManager
    from flext_api._utilities.middleware import FlextApiMiddleware
    from flext_api._utilities.registry import FlextApiRegistry
    from flext_api._utilities.serializers import FlextApiUtilitiesSerializers
    from flext_api._utilities.server_factory import FlextApiServerFactory
    from flext_api._utilities.settings_manager import FlextApiUtilitiesSettingsManager
    from flext_api._utilities.storage import FlextApiStorage
    from flext_api._utilities.webhook import FlextWebhookHandler
    from flext_api.api import FlextApi, api
    from flext_api.constants import FlextApiConstants, c
    from flext_api.errors import FlextApiErrors
    from flext_api.models import FlextApiModels, m
    from flext_api.protocol_impls.base import FlextApiBaseProtocolImplementation
    from flext_api.protocol_impls.http import FlextWebProtocolPlugin
    from flext_api.protocol_impls.http_client import FlextWebClientImplementation
    from flext_api.protocol_impls.logger import FlextApiLoggerProtocolImplementation
    from flext_api.protocol_impls.rfc import FlextApiRfcProtocolImplementation
    from flext_api.protocol_impls.sse import FlextApiSseProtocolPlugin
    from flext_api.protocol_impls.storage_backend import (
        FlextApiStorageBackendImplementation,
    )
    from flext_api.protocol_impls.websocket import FlextApiWebsocketProtocolPlugin
    from flext_api.protocols import FlextApiProtocols, p
    from flext_api.schemas.asyncapi import FlextApiAsyncapiSchemaValidator
    from flext_api.schemas.jsonschema import FlextApiJsonschemaValidator
    from flext_api.schemas.openapi import FlextApiOpenapiSchemaValidator
    from flext_api.server import FlextApiServer
    from flext_api.settings import FlextApiSettings
    from flext_api.typings import FlextApiTypes, t
    from flext_api.utilities import FlextApiUtilities, u
_LAZY_IMPORTS = merge_lazy_imports(
    (
        "._protocols",
        "._typings",
        "._utilities",
        ".protocol_impls",
        ".schemas",
    ),
    build_lazy_import_map(
        {
            ".__version__": (
                "__author__",
                "__author_email__",
                "__description__",
                "__license__",
                "__title__",
                "__url__",
            ),
            ".api": (
                "FlextApi",
                "api",
            ),
            ".constants": (
                "FlextApiConstants",
                "c",
            ),
            ".errors": ("FlextApiErrors",),
            ".models": (
                "FlextApiModels",
                "m",
            ),
            ".protocols": (
                "FlextApiProtocols",
                "p",
            ),
            ".server": ("FlextApiServer",),
            ".settings": ("FlextApiSettings",),
            ".typings": (
                "FlextApiTypes",
                "t",
            ),
            ".utilities": (
                "FlextApiUtilities",
                "u",
            ),
            "flext_cli": (
                "d",
                "e",
                "h",
                "r",
                "s",
                "x",
            ),
        },
    ),
    exclude_names=(
        "cleanup_submodule_namespace",
        "install_lazy_exports",
        "lazy_getattr",
        "logger",
        "merge_lazy_imports",
        "output",
        "output_reporting",
    ),
    module_name=__name__,
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

__all__ = [
    "FlextApi",
    "FlextApiAdapters",
    "FlextApiApp",
    "FlextApiAsyncapiSchemaValidator",
    "FlextApiBaseProtocolImplementation",
    "FlextApiClient",
    "FlextApiConstants",
    "FlextApiErrors",
    "FlextApiJsonschemaValidator",
    "FlextApiLifecycleManager",
    "FlextApiLoggerProtocolImplementation",
    "FlextApiMiddleware",
    "FlextApiModels",
    "FlextApiOpenapiSchemaValidator",
    "FlextApiPlugins",
    "FlextApiProtocols",
    "FlextApiProtocolsSerialization",
    "FlextApiRegistry",
    "FlextApiRfcProtocolImplementation",
    "FlextApiServer",
    "FlextApiServerFactory",
    "FlextApiSettings",
    "FlextApiSseProtocolPlugin",
    "FlextApiStorage",
    "FlextApiStorageBackendImplementation",
    "FlextApiTransports",
    "FlextApiTypes",
    "FlextApiTypingsSerialization",
    "FlextApiUtilities",
    "FlextApiUtilitiesSerializers",
    "FlextApiUtilitiesSettingsManager",
    "FlextApiWebsocketProtocolPlugin",
    "FlextWebClientImplementation",
    "FlextWebProtocolPlugin",
    "FlextWebhookHandler",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "api",
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

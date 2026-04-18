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
    from flext_api._utilities.settings_manager import FlextApiUtilitiesSettingsManager
    from flext_api._utilities.storage import FlextApiStorage
    from flext_api._utilities.webhook import FlextApiWebhookHandler
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
    from flext_api.protocol_impls.websocket import FlextApiWebsocketProtocolPlugin
    from flext_api.protocols import FlextApiProtocols, p
    from flext_api.server import FlextApiServer
    from flext_api.settings import FlextApiSettings
    from flext_api.typings import FlextApiTypes, t
    from flext_api.utilities import FlextApiUtilities, u
    from flext_web import d, e, h, r, s, x
_LAZY_IMPORTS = merge_lazy_imports(
    (
        "._protocols",
        "._typings",
        "._utilities",
        ".protocol_impls",
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
                "__version__",
                "__version_info__",
            ),
            "._protocols.plugins": ("FlextApiPlugins",),
            "._protocols.serialization": ("FlextApiProtocolsSerialization",),
            "._protocols.transports": ("FlextApiTransports",),
            "._typings.serialization": ("FlextApiTypingsSerialization",),
            "._utilities.adapters": ("FlextApiAdapters",),
            "._utilities.app": ("FlextApiApp",),
            "._utilities.client": ("FlextApiClient",),
            "._utilities.lifecycle_manager": ("FlextApiLifecycleManager",),
            "._utilities.middleware": ("FlextApiMiddleware",),
            "._utilities.registry": ("FlextApiRegistry",),
            "._utilities.serializers": ("FlextApiUtilitiesSerializers",),
            "._utilities.settings_manager": ("FlextApiUtilitiesSettingsManager",),
            "._utilities.storage": ("FlextApiStorage",),
            "._utilities.webhook": ("FlextApiWebhookHandler",),
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
            ".protocol_impls.base": ("FlextApiBaseProtocolImplementation",),
            ".protocol_impls.http": ("FlextWebProtocolPlugin",),
            ".protocol_impls.http_client": ("FlextWebClientImplementation",),
            ".protocol_impls.logger": ("FlextApiLoggerProtocolImplementation",),
            ".protocol_impls.rfc": ("FlextApiRfcProtocolImplementation",),
            ".protocol_impls.sse": ("FlextApiSseProtocolPlugin",),
            ".protocol_impls.websocket": ("FlextApiWebsocketProtocolPlugin",),
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
            "flext_web": (
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

__all__: list[str] = [
    "FlextApi",
    "FlextApiAdapters",
    "FlextApiApp",
    "FlextApiBaseProtocolImplementation",
    "FlextApiClient",
    "FlextApiConstants",
    "FlextApiErrors",
    "FlextApiLifecycleManager",
    "FlextApiLoggerProtocolImplementation",
    "FlextApiMiddleware",
    "FlextApiModels",
    "FlextApiPlugins",
    "FlextApiProtocols",
    "FlextApiProtocolsSerialization",
    "FlextApiRegistry",
    "FlextApiRfcProtocolImplementation",
    "FlextApiServer",
    "FlextApiSettings",
    "FlextApiSseProtocolPlugin",
    "FlextApiStorage",
    "FlextApiTransports",
    "FlextApiTypes",
    "FlextApiTypingsSerialization",
    "FlextApiUtilities",
    "FlextApiUtilitiesSerializers",
    "FlextApiUtilitiesSettingsManager",
    "FlextApiWebhookHandler",
    "FlextApiWebsocketProtocolPlugin",
    "FlextWebClientImplementation",
    "FlextWebProtocolPlugin",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
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

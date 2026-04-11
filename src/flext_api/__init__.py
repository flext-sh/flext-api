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
    from _protocols.plugins import FlextApiPlugins
    from _protocols.transports import FlextApiTransports
    from _utilities.adapters import FlextApiAdapters
    from _utilities.app import FlextApiApp
    from _utilities.client import FlextApiClient
    from _utilities.lifecycle_manager import FlextApiLifecycleManager
    from _utilities.middleware import FlextApiMiddleware
    from _utilities.registry import FlextApiRegistry
    from _utilities.serializers import FlextApiUtilitiesSerializers
    from _utilities.server_factory import FlextApiServerFactory
    from _utilities.settings_manager import FlextApiUtilitiesSettingsManager
    from _utilities.storage import FlextApiStorage
    from _utilities.webhook import FlextWebhookHandler

    from flext_api.api import FlextApi
    from flext_api.asyncapi import FlextApiAsyncapiSchemaValidator
    from flext_api.base import FlextApiBaseProtocolImplementation
    from flext_api.constants import FlextApiConstants, c
    from flext_api.errors import FlextApiErrors
    from flext_api.http import FlextWebProtocolPlugin
    from flext_api.http_client import FlextWebClientImplementation
    from flext_api.jsonschema import FlextApiJsonschemaValidator
    from flext_api.logger import FlextApiLoggerProtocolImplementation
    from flext_api.models import FlextApiModels, m
    from flext_api.openapi import FlextApiOpenapiSchemaValidator
    from flext_api.protocols import FlextApiProtocols, p
    from flext_api.rfc import FlextApiRfcProtocolImplementation
    from flext_api.server import FlextApiServer
    from flext_api.settings import FlextApiSettings
    from flext_api.sse import FlextApiSseProtocolPlugin
    from flext_api.storage_backend import FlextApiStorageBackendImplementation
    from flext_api.typings import FlextApiTypes, t
    from flext_api.utilities import FlextApiUtilities, u
    from flext_api.websocket import FlextApiWebsocketProtocolPlugin
    from flext_core.decorators import d
    from flext_core.exceptions import e
    from flext_core.handlers import h
    from flext_core.mixins import x
    from flext_core.result import r
    from flext_core.service import s
_LAZY_IMPORTS = merge_lazy_imports(
    (
        "._protocols",
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
                "__version__",
                "__version_info__",
            ),
            ".api": ("FlextApi",),
            ".asyncapi": ("FlextApiAsyncapiSchemaValidator",),
            ".base": ("FlextApiBaseProtocolImplementation",),
            ".constants": (
                "FlextApiConstants",
                "c",
            ),
            ".errors": ("FlextApiErrors",),
            ".http": ("FlextWebProtocolPlugin",),
            ".http_client": ("FlextWebClientImplementation",),
            ".jsonschema": ("FlextApiJsonschemaValidator",),
            ".logger": ("FlextApiLoggerProtocolImplementation",),
            ".models": (
                "FlextApiModels",
                "m",
            ),
            ".openapi": ("FlextApiOpenapiSchemaValidator",),
            ".protocols": (
                "FlextApiProtocols",
                "p",
            ),
            ".rfc": ("FlextApiRfcProtocolImplementation",),
            ".server": ("FlextApiServer",),
            ".settings": ("FlextApiSettings",),
            ".sse": ("FlextApiSseProtocolPlugin",),
            ".storage_backend": ("FlextApiStorageBackendImplementation",),
            ".typings": (
                "FlextApiTypes",
                "t",
            ),
            ".utilities": (
                "FlextApiUtilities",
                "u",
            ),
            ".websocket": ("FlextApiWebsocketProtocolPlugin",),
            "_protocols.plugins": ("FlextApiPlugins",),
            "_protocols.transports": ("FlextApiTransports",),
            "_utilities.adapters": ("FlextApiAdapters",),
            "_utilities.app": ("FlextApiApp",),
            "_utilities.client": ("FlextApiClient",),
            "_utilities.lifecycle_manager": ("FlextApiLifecycleManager",),
            "_utilities.middleware": ("FlextApiMiddleware",),
            "_utilities.registry": ("FlextApiRegistry",),
            "_utilities.serializers": ("FlextApiUtilitiesSerializers",),
            "_utilities.server_factory": ("FlextApiServerFactory",),
            "_utilities.settings_manager": ("FlextApiUtilitiesSettingsManager",),
            "_utilities.storage": ("FlextApiStorage",),
            "_utilities.webhook": ("FlextWebhookHandler",),
            "flext_core.decorators": ("d",),
            "flext_core.exceptions": ("e",),
            "flext_core.handlers": ("h",),
            "flext_core.mixins": ("x",),
            "flext_core.result": ("r",),
            "flext_core.service": ("s",),
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

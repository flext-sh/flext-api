# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api package."""

from __future__ import annotations

import typing as _t

from flext_api.__version__ import *
from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _t.TYPE_CHECKING:
    from flext_api._protocols.plugins import FlextApiPlugins
    from flext_api._protocols.transports import FlextApiTransports
    from flext_api._utilities.adapters import FlextApiAdapters
    from flext_api._utilities.app import FlextApiApp
    from flext_api._utilities.client import FlextApiClient
    from flext_api._utilities.lifecycle_manager import FlextApiLifecycleManager
    from flext_api._utilities.middleware import FlextApiMiddleware
    from flext_api._utilities.registry import FlextApiRegistry
    from flext_api._utilities.serializers import FlextApiSerializers
    from flext_api._utilities.server_factory import FlextApiServerFactory
    from flext_api._utilities.settings_manager import FlextApiSettingsManager
    from flext_api._utilities.storage import FlextApiStorage
    from flext_api._utilities.webhook import FlextWebhookHandler
    from flext_api.api import FlextApi
    from flext_api.constants import FlextApiConstants, FlextApiConstants as c
    from flext_api.errors import FlextApiErrors
    from flext_api.models import FlextApiModels, FlextApiModels as m
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
    from flext_api.protocols import FlextApiProtocols, FlextApiProtocols as p
    from flext_api.schemas._shared import (
        FlextApiSchemaShared,
        is_container_value,
        is_object_mapping,
        load_and_validate_schema_document,
        load_schema_document,
        normalize_json_object,
        parse_dict_field,
        parse_int_field,
        parse_string_field,
        to_general_value,
    )
    from flext_api.schemas.asyncapi import FlextApiAsyncapiSchemaValidator
    from flext_api.schemas.jsonschema import FlextApiJsonschemaValidator
    from flext_api.schemas.openapi import FlextApiOpenapiSchemaValidator
    from flext_api.server import FlextApiServer
    from flext_api.settings import FlextApiSettings
    from flext_api.typings import FlextApiTypes, FlextApiTypes as t
    from flext_api.utilities import FlextApiUtilities, FlextApiUtilities as u
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
_LAZY_IMPORTS = merge_lazy_imports(
    (
        "._protocols",
        "._utilities",
        ".protocol_impls",
        ".schemas",
    ),
    {
        "FlextApi": ".api",
        "FlextApiConstants": ".constants",
        "FlextApiErrors": ".errors",
        "FlextApiModels": ".models",
        "FlextApiProtocols": ".protocols",
        "FlextApiServer": ".server",
        "FlextApiSettings": ".settings",
        "FlextApiTypes": ".typings",
        "FlextApiUtilities": ".utilities",
        "__author__": ".__version__",
        "__author_email__": ".__version__",
        "__description__": ".__version__",
        "__license__": ".__version__",
        "__title__": ".__version__",
        "__url__": ".__version__",
        "__version__": ".__version__",
        "__version_info__": ".__version__",
        "c": (".constants", "FlextApiConstants"),
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_core.exceptions", "FlextExceptions"),
        "h": ("flext_core.handlers", "FlextHandlers"),
        "m": (".models", "FlextApiModels"),
        "p": (".protocols", "FlextApiProtocols"),
        "r": ("flext_core.result", "FlextResult"),
        "s": ("flext_core.service", "FlextService"),
        "t": (".typings", "FlextApiTypes"),
        "u": (".utilities", "FlextApiUtilities"),
        "x": ("flext_core.mixins", "FlextMixins"),
    },
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
    "FlextApiSchemaShared",
    "FlextApiSerializers",
    "FlextApiServer",
    "FlextApiServerFactory",
    "FlextApiSettings",
    "FlextApiSettingsManager",
    "FlextApiSseProtocolPlugin",
    "FlextApiStorage",
    "FlextApiStorageBackendImplementation",
    "FlextApiTransports",
    "FlextApiTypes",
    "FlextApiUtilities",
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
    "is_container_value",
    "is_object_mapping",
    "load_and_validate_schema_document",
    "load_schema_document",
    "m",
    "normalize_json_object",
    "p",
    "parse_dict_field",
    "parse_int_field",
    "parse_string_field",
    "r",
    "s",
    "t",
    "to_general_value",
    "u",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

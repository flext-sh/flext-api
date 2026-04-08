# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext api package."""

from __future__ import annotations

import typing as _t

from flext_api.__version__ import *
from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _t.TYPE_CHECKING:
    import flext_api._protocols as _flext_api__protocols

    _protocols = _flext_api__protocols
    import flext_api._utilities as _flext_api__utilities
    from flext_api._protocols import FlextApiPlugins, FlextApiTransports

    _utilities = _flext_api__utilities
    import flext_api.api as _flext_api_api
    from flext_api._utilities import (
        FlextApiAdapters,
        FlextApiApp,
        FlextApiClient,
        FlextApiLifecycleManager,
        FlextApiMiddleware,
        FlextApiRegistry,
        FlextApiSerializers,
        FlextApiServerFactory,
        FlextApiSettingsManager,
        FlextApiStorage,
        FlextWebhookHandler,
    )

    api = _flext_api_api
    import flext_api.constants as _flext_api_constants
    from flext_api.api import FlextApi

    constants = _flext_api_constants
    import flext_api.errors as _flext_api_errors
    from flext_api.constants import FlextApiConstants, FlextApiConstants as c

    errors = _flext_api_errors
    import flext_api.models as _flext_api_models
    from flext_api.errors import FlextApiErrors

    models = _flext_api_models
    import flext_api.protocols as _flext_api_protocols
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

    protocols = _flext_api_protocols
    import flext_api.server as _flext_api_server
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

    server = _flext_api_server
    import flext_api.settings as _flext_api_settings
    from flext_api.server import FlextApiServer

    settings = _flext_api_settings
    import flext_api.typings as _flext_api_typings
    from flext_api.settings import FlextApiSettings

    typings = _flext_api_typings
    import flext_api.utilities as _flext_api_utilities
    from flext_api.typings import FlextApiTypes, FlextApiTypes as t

    utilities = _flext_api_utilities
    from flext_api.utilities import FlextApiUtilities, FlextApiUtilities as u
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
_LAZY_IMPORTS = merge_lazy_imports(
    (
        "flext_api._protocols",
        "flext_api._utilities",
    ),
    {
        "FlextApi": ("flext_api.api", "FlextApi"),
        "FlextApiAsyncapiSchemaValidator": (
            "flext_api.schemas.asyncapi",
            "FlextApiAsyncapiSchemaValidator",
        ),
        "FlextApiBaseProtocolImplementation": (
            "flext_api.protocol_impls.base",
            "FlextApiBaseProtocolImplementation",
        ),
        "FlextApiConstants": ("flext_api.constants", "FlextApiConstants"),
        "FlextApiErrors": ("flext_api.errors", "FlextApiErrors"),
        "FlextApiJsonschemaValidator": (
            "flext_api.schemas.jsonschema",
            "FlextApiJsonschemaValidator",
        ),
        "FlextApiLoggerProtocolImplementation": (
            "flext_api.protocol_impls.logger",
            "FlextApiLoggerProtocolImplementation",
        ),
        "FlextApiModels": ("flext_api.models", "FlextApiModels"),
        "FlextApiOpenapiSchemaValidator": (
            "flext_api.schemas.openapi",
            "FlextApiOpenapiSchemaValidator",
        ),
        "FlextApiProtocols": ("flext_api.protocols", "FlextApiProtocols"),
        "FlextApiRfcProtocolImplementation": (
            "flext_api.protocol_impls.rfc",
            "FlextApiRfcProtocolImplementation",
        ),
        "FlextApiSchemaShared": ("flext_api.schemas._shared", "FlextApiSchemaShared"),
        "FlextApiServer": ("flext_api.server", "FlextApiServer"),
        "FlextApiSettings": ("flext_api.settings", "FlextApiSettings"),
        "FlextApiSseProtocolPlugin": (
            "flext_api.protocol_impls.sse",
            "FlextApiSseProtocolPlugin",
        ),
        "FlextApiStorageBackendImplementation": (
            "flext_api.protocol_impls.storage_backend",
            "FlextApiStorageBackendImplementation",
        ),
        "FlextApiTypes": ("flext_api.typings", "FlextApiTypes"),
        "FlextApiUtilities": ("flext_api.utilities", "FlextApiUtilities"),
        "FlextApiWebsocketProtocolPlugin": (
            "flext_api.protocol_impls.websocket",
            "FlextApiWebsocketProtocolPlugin",
        ),
        "FlextWebClientImplementation": (
            "flext_api.protocol_impls.http_client",
            "FlextWebClientImplementation",
        ),
        "FlextWebProtocolPlugin": (
            "flext_api.protocol_impls.http",
            "FlextWebProtocolPlugin",
        ),
        "__author__": ("flext_api.__version__", "__author__"),
        "__author_email__": ("flext_api.__version__", "__author_email__"),
        "__description__": ("flext_api.__version__", "__description__"),
        "__license__": ("flext_api.__version__", "__license__"),
        "__title__": ("flext_api.__version__", "__title__"),
        "__url__": ("flext_api.__version__", "__url__"),
        "__version__": ("flext_api.__version__", "__version__"),
        "__version_info__": ("flext_api.__version__", "__version_info__"),
        "_protocols": "flext_api._protocols",
        "_utilities": "flext_api._utilities",
        "api": "flext_api.api",
        "c": ("flext_api.constants", "FlextApiConstants"),
        "constants": "flext_api.constants",
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_core.exceptions", "FlextExceptions"),
        "errors": "flext_api.errors",
        "h": ("flext_core.handlers", "FlextHandlers"),
        "is_container_value": ("flext_api.schemas._shared", "is_container_value"),
        "is_object_mapping": ("flext_api.schemas._shared", "is_object_mapping"),
        "load_and_validate_schema_document": (
            "flext_api.schemas._shared",
            "load_and_validate_schema_document",
        ),
        "load_schema_document": ("flext_api.schemas._shared", "load_schema_document"),
        "m": ("flext_api.models", "FlextApiModels"),
        "models": "flext_api.models",
        "normalize_json_object": ("flext_api.schemas._shared", "normalize_json_object"),
        "p": ("flext_api.protocols", "FlextApiProtocols"),
        "parse_dict_field": ("flext_api.schemas._shared", "parse_dict_field"),
        "parse_int_field": ("flext_api.schemas._shared", "parse_int_field"),
        "parse_string_field": ("flext_api.schemas._shared", "parse_string_field"),
        "protocols": "flext_api.protocols",
        "r": ("flext_core.result", "FlextResult"),
        "s": ("flext_core.service", "FlextService"),
        "server": "flext_api.server",
        "settings": "flext_api.settings",
        "t": ("flext_api.typings", "FlextApiTypes"),
        "to_general_value": ("flext_api.schemas._shared", "to_general_value"),
        "typings": "flext_api.typings",
        "u": ("flext_api.utilities", "FlextApiUtilities"),
        "utilities": "flext_api.utilities",
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)
_ = _LAZY_IMPORTS.pop("cleanup_submodule_namespace", None)
_ = _LAZY_IMPORTS.pop("install_lazy_exports", None)
_ = _LAZY_IMPORTS.pop("lazy_getattr", None)
_ = _LAZY_IMPORTS.pop("merge_lazy_imports", None)
_ = _LAZY_IMPORTS.pop("output", None)
_ = _LAZY_IMPORTS.pop("output_reporting", None)

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
    "_protocols",
    "_utilities",
    "api",
    "c",
    "constants",
    "d",
    "e",
    "errors",
    "h",
    "is_container_value",
    "is_object_mapping",
    "load_and_validate_schema_document",
    "load_schema_document",
    "m",
    "models",
    "normalize_json_object",
    "p",
    "parse_dict_field",
    "parse_int_field",
    "parse_string_field",
    "protocols",
    "r",
    "s",
    "server",
    "settings",
    "t",
    "to_general_value",
    "typings",
    "u",
    "utilities",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

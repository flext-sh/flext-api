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
    from flext_api.__version__ import (
        __author__,
        __author_email__,
        __description__,
        __license__,
        __title__,
        __url__,
        __version__,
        __version_info__,
    )

    _protocols = _flext_api__protocols
    import flext_api._protocols.plugins as _flext_api__protocols_plugins

    plugins = _flext_api__protocols_plugins
    import flext_api._protocols.transports as _flext_api__protocols_transports
    from flext_api._protocols.plugins import FlextApiPlugins

    transports = _flext_api__protocols_transports
    import flext_api._utilities as _flext_api__utilities
    from flext_api._protocols.transports import FlextApiTransports

    _utilities = _flext_api__utilities
    import flext_api._utilities.adapters as _flext_api__utilities_adapters

    adapters = _flext_api__utilities_adapters
    import flext_api._utilities.app as _flext_api__utilities_app
    from flext_api._utilities.adapters import FlextApiAdapters

    app = _flext_api__utilities_app
    import flext_api._utilities.client as _flext_api__utilities_client
    from flext_api._utilities.app import FlextApiApp

    client = _flext_api__utilities_client
    import flext_api._utilities.lifecycle_manager as _flext_api__utilities_lifecycle_manager
    from flext_api._utilities.client import FlextApiClient

    lifecycle_manager = _flext_api__utilities_lifecycle_manager
    import flext_api._utilities.middleware as _flext_api__utilities_middleware
    from flext_api._utilities.lifecycle_manager import FlextApiLifecycleManager

    middleware = _flext_api__utilities_middleware
    import flext_api._utilities.registry as _flext_api__utilities_registry
    from flext_api._utilities.middleware import FlextApiMiddleware

    registry = _flext_api__utilities_registry
    import flext_api._utilities.serializers as _flext_api__utilities_serializers
    from flext_api._utilities.registry import FlextApiRegistry

    serializers = _flext_api__utilities_serializers
    import flext_api._utilities.server_factory as _flext_api__utilities_server_factory
    from flext_api._utilities.serializers import FlextApiSerializers

    server_factory = _flext_api__utilities_server_factory
    import flext_api._utilities.settings_manager as _flext_api__utilities_settings_manager
    from flext_api._utilities.server_factory import FlextApiServerFactory

    settings_manager = _flext_api__utilities_settings_manager
    import flext_api._utilities.storage as _flext_api__utilities_storage
    from flext_api._utilities.settings_manager import FlextApiSettingsManager

    storage = _flext_api__utilities_storage
    import flext_api._utilities.webhook as _flext_api__utilities_webhook
    from flext_api._utilities.storage import FlextApiStorage

    webhook = _flext_api__utilities_webhook
    import flext_api.api as _flext_api_api
    from flext_api._utilities.webhook import FlextWebhookHandler

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
    import flext_api.protocol_impls as _flext_api_protocol_impls
    from flext_api.models import FlextApiModels, FlextApiModels as m

    protocol_impls = _flext_api_protocol_impls
    import flext_api.protocol_impls.base as _flext_api_protocol_impls_base

    base = _flext_api_protocol_impls_base
    import flext_api.protocol_impls.http as _flext_api_protocol_impls_http
    from flext_api.protocol_impls.base import FlextApiBaseProtocolImplementation

    http = _flext_api_protocol_impls_http
    import flext_api.protocol_impls.http_client as _flext_api_protocol_impls_http_client
    from flext_api.protocol_impls.http import FlextWebProtocolPlugin

    http_client = _flext_api_protocol_impls_http_client
    import flext_api.protocol_impls.logger as _flext_api_protocol_impls_logger
    from flext_api.protocol_impls.http_client import FlextWebClientImplementation

    logger = _flext_api_protocol_impls_logger
    import flext_api.protocol_impls.rfc as _flext_api_protocol_impls_rfc
    from flext_api.protocol_impls.logger import FlextApiLoggerProtocolImplementation

    rfc = _flext_api_protocol_impls_rfc
    import flext_api.protocol_impls.sse as _flext_api_protocol_impls_sse
    from flext_api.protocol_impls.rfc import FlextApiRfcProtocolImplementation

    sse = _flext_api_protocol_impls_sse
    import flext_api.protocol_impls.storage_backend as _flext_api_protocol_impls_storage_backend
    from flext_api.protocol_impls.sse import FlextApiSseProtocolPlugin

    storage_backend = _flext_api_protocol_impls_storage_backend
    import flext_api.protocol_impls.websocket as _flext_api_protocol_impls_websocket
    from flext_api.protocol_impls.storage_backend import (
        FlextApiStorageBackendImplementation,
    )

    websocket = _flext_api_protocol_impls_websocket
    import flext_api.protocols as _flext_api_protocols
    from flext_api.protocol_impls.websocket import FlextApiWebsocketProtocolPlugin

    protocols = _flext_api_protocols
    import flext_api.schemas as _flext_api_schemas
    from flext_api.protocols import FlextApiProtocols, FlextApiProtocols as p

    schemas = _flext_api_schemas
    import flext_api.schemas.asyncapi as _flext_api_schemas_asyncapi
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

    asyncapi = _flext_api_schemas_asyncapi
    import flext_api.schemas.jsonschema as _flext_api_schemas_jsonschema
    from flext_api.schemas.asyncapi import FlextApiAsyncapiSchemaValidator

    jsonschema = _flext_api_schemas_jsonschema
    import flext_api.schemas.openapi as _flext_api_schemas_openapi
    from flext_api.schemas.jsonschema import FlextApiJsonschemaValidator

    openapi = _flext_api_schemas_openapi
    import flext_api.server as _flext_api_server
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
        "flext_api.protocol_impls",
        "flext_api.schemas",
    ),
    {
        "FlextApi": "flext_api.api",
        "FlextApiConstants": "flext_api.constants",
        "FlextApiErrors": "flext_api.errors",
        "FlextApiModels": "flext_api.models",
        "FlextApiProtocols": "flext_api.protocols",
        "FlextApiServer": "flext_api.server",
        "FlextApiSettings": "flext_api.settings",
        "FlextApiTypes": "flext_api.typings",
        "FlextApiUtilities": "flext_api.utilities",
        "__author__": "flext_api.__version__",
        "__author_email__": "flext_api.__version__",
        "__description__": "flext_api.__version__",
        "__license__": "flext_api.__version__",
        "__title__": "flext_api.__version__",
        "__url__": "flext_api.__version__",
        "__version__": "flext_api.__version__",
        "__version_info__": "flext_api.__version__",
        "_protocols": "flext_api._protocols",
        "_utilities": "flext_api._utilities",
        "api": "flext_api.api",
        "c": ("flext_api.constants", "FlextApiConstants"),
        "constants": "flext_api.constants",
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_core.exceptions", "FlextExceptions"),
        "errors": "flext_api.errors",
        "h": ("flext_core.handlers", "FlextHandlers"),
        "m": ("flext_api.models", "FlextApiModels"),
        "models": "flext_api.models",
        "p": ("flext_api.protocols", "FlextApiProtocols"),
        "protocol_impls": "flext_api.protocol_impls",
        "protocols": "flext_api.protocols",
        "r": ("flext_core.result", "FlextResult"),
        "s": ("flext_core.service", "FlextService"),
        "schemas": "flext_api.schemas",
        "server": "flext_api.server",
        "settings": "flext_api.settings",
        "t": ("flext_api.typings", "FlextApiTypes"),
        "typings": "flext_api.typings",
        "u": ("flext_api.utilities", "FlextApiUtilities"),
        "utilities": "flext_api.utilities",
        "x": ("flext_core.mixins", "FlextMixins"),
    },
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
    "_protocols",
    "_utilities",
    "adapters",
    "api",
    "app",
    "asyncapi",
    "base",
    "c",
    "client",
    "constants",
    "d",
    "e",
    "errors",
    "h",
    "http",
    "http_client",
    "is_container_value",
    "is_object_mapping",
    "jsonschema",
    "lifecycle_manager",
    "load_and_validate_schema_document",
    "load_schema_document",
    "logger",
    "m",
    "middleware",
    "models",
    "normalize_json_object",
    "openapi",
    "p",
    "parse_dict_field",
    "parse_int_field",
    "parse_string_field",
    "plugins",
    "protocol_impls",
    "protocols",
    "r",
    "registry",
    "rfc",
    "s",
    "schemas",
    "serializers",
    "server",
    "server_factory",
    "settings",
    "settings_manager",
    "sse",
    "storage",
    "storage_backend",
    "t",
    "to_general_value",
    "transports",
    "typings",
    "u",
    "utilities",
    "webhook",
    "websocket",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

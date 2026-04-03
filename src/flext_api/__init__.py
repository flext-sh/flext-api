# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext api package."""

from __future__ import annotations

import typing as _t

from flext_api.__version__ import *
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
from flext_core.lazy import install_lazy_exports, merge_lazy_imports
from flext_core.mixins import FlextMixins as x
from flext_core.result import FlextResult as r
from flext_core.service import FlextService as s

if _t.TYPE_CHECKING:
    import flext_api._protocols as _flext_api__protocols

    _protocols = _flext_api__protocols
    import flext_api._protocols.plugins as _flext_api__protocols_plugins

    plugins = _flext_api__protocols_plugins
    import flext_api._protocols.transports as _flext_api__protocols_transports

    transports = _flext_api__protocols_transports
    import flext_api._utilities as _flext_api__utilities

    _utilities = _flext_api__utilities
    import flext_api._utilities.adapters as _flext_api__utilities_adapters

    adapters = _flext_api__utilities_adapters
    import flext_api._utilities.app as _flext_api__utilities_app

    app = _flext_api__utilities_app
    import flext_api._utilities.client as _flext_api__utilities_client

    client = _flext_api__utilities_client
    import flext_api._utilities.lifecycle_manager as _flext_api__utilities_lifecycle_manager

    lifecycle_manager = _flext_api__utilities_lifecycle_manager
    import flext_api._utilities.middleware as _flext_api__utilities_middleware

    middleware = _flext_api__utilities_middleware
    import flext_api._utilities.registry as _flext_api__utilities_registry

    registry = _flext_api__utilities_registry
    import flext_api._utilities.serializers as _flext_api__utilities_serializers

    serializers = _flext_api__utilities_serializers
    import flext_api._utilities.server_factory as _flext_api__utilities_server_factory

    server_factory = _flext_api__utilities_server_factory
    import flext_api._utilities.settings_manager as _flext_api__utilities_settings_manager

    settings_manager = _flext_api__utilities_settings_manager
    import flext_api._utilities.storage as _flext_api__utilities_storage

    storage = _flext_api__utilities_storage
    import flext_api._utilities.webhook as _flext_api__utilities_webhook

    webhook = _flext_api__utilities_webhook
    import flext_api.api as _flext_api_api

    api = _flext_api_api
    import flext_api.constants as _flext_api_constants

    constants = _flext_api_constants
    import flext_api.errors as _flext_api_errors

    errors = _flext_api_errors
    import flext_api.models as _flext_api_models

    models = _flext_api_models
    import flext_api.protocol_impls as _flext_api_protocol_impls

    protocol_impls = _flext_api_protocol_impls
    import flext_api.protocol_impls.base as _flext_api_protocol_impls_base

    base = _flext_api_protocol_impls_base
    import flext_api.protocol_impls.http as _flext_api_protocol_impls_http

    http = _flext_api_protocol_impls_http
    import flext_api.protocol_impls.http_client as _flext_api_protocol_impls_http_client

    http_client = _flext_api_protocol_impls_http_client
    import flext_api.protocol_impls.logger as _flext_api_protocol_impls_logger

    logger = _flext_api_protocol_impls_logger
    import flext_api.protocol_impls.rfc as _flext_api_protocol_impls_rfc

    rfc = _flext_api_protocol_impls_rfc
    import flext_api.protocol_impls.sse as _flext_api_protocol_impls_sse

    sse = _flext_api_protocol_impls_sse
    import flext_api.protocol_impls.storage_backend as _flext_api_protocol_impls_storage_backend

    storage_backend = _flext_api_protocol_impls_storage_backend
    import flext_api.protocol_impls.websocket as _flext_api_protocol_impls_websocket

    websocket = _flext_api_protocol_impls_websocket
    import flext_api.protocols as _flext_api_protocols

    protocols = _flext_api_protocols
    import flext_api.schemas as _flext_api_schemas

    schemas = _flext_api_schemas
    import flext_api.schemas.asyncapi as _flext_api_schemas_asyncapi

    asyncapi = _flext_api_schemas_asyncapi
    import flext_api.schemas.jsonschema as _flext_api_schemas_jsonschema

    jsonschema = _flext_api_schemas_jsonschema
    import flext_api.schemas.openapi as _flext_api_schemas_openapi

    openapi = _flext_api_schemas_openapi
    import flext_api.server as _flext_api_server

    server = _flext_api_server
    import flext_api.settings as _flext_api_settings

    settings = _flext_api_settings
    import flext_api.typings as _flext_api_typings

    typings = _flext_api_typings
    import flext_api.utilities as _flext_api_utilities

    utilities = _flext_api_utilities

    _ = (
        FlextApi,
        FlextApiAdapters,
        FlextApiApp,
        FlextApiAsyncapiSchemaValidator,
        FlextApiBaseProtocolImplementation,
        FlextApiClient,
        FlextApiConstants,
        FlextApiErrors,
        FlextApiJsonschemaValidator,
        FlextApiLifecycleManager,
        FlextApiLoggerProtocolImplementation,
        FlextApiMiddleware,
        FlextApiModels,
        FlextApiOpenapiSchemaValidator,
        FlextApiPlugins,
        FlextApiProtocols,
        FlextApiRegistry,
        FlextApiRfcProtocolImplementation,
        FlextApiSchemaShared,
        FlextApiSerializers,
        FlextApiServer,
        FlextApiServerFactory,
        FlextApiSettings,
        FlextApiSettingsManager,
        FlextApiSseProtocolPlugin,
        FlextApiStorage,
        FlextApiStorageBackendImplementation,
        FlextApiTransports,
        FlextApiTypes,
        FlextApiUtilities,
        FlextApiWebsocketProtocolPlugin,
        FlextWebClientImplementation,
        FlextWebProtocolPlugin,
        FlextWebhookHandler,
        __author__,
        __author_email__,
        __description__,
        __license__,
        __title__,
        __url__,
        __version__,
        __version_info__,
        _protocols,
        _utilities,
        adapters,
        api,
        app,
        asyncapi,
        base,
        c,
        client,
        constants,
        d,
        e,
        errors,
        h,
        http,
        http_client,
        is_container_value,
        is_object_mapping,
        jsonschema,
        lifecycle_manager,
        load_and_validate_schema_document,
        load_schema_document,
        logger,
        m,
        middleware,
        models,
        normalize_json_object,
        openapi,
        p,
        parse_dict_field,
        parse_int_field,
        parse_string_field,
        plugins,
        protocol_impls,
        protocols,
        r,
        registry,
        rfc,
        s,
        schemas,
        serializers,
        server,
        server_factory,
        settings,
        settings_manager,
        sse,
        storage,
        storage_backend,
        t,
        to_general_value,
        transports,
        typings,
        u,
        utilities,
        webhook,
        websocket,
        x,
    )
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

# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext api package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

from flext_api.__version__ import (
    __author__ as __author__,
    __author_email__ as __author_email__,
    __description__ as __description__,
    __license__ as __license__,
    __title__ as __title__,
    __url__ as __url__,
    __version__ as __version__,
    __version_info__ as __version_info__,
)

if TYPE_CHECKING:
    from flext_api import (
        _protocols as _protocols,
        _utilities as _utilities,
        api as api,
        constants as constants,
        errors as errors,
        models as models,
        protocol_impls as protocol_impls,
        protocols as protocols,
        schemas as schemas,
        server as server,
        settings as settings,
        typings as typings,
        utilities as utilities,
    )
    from flext_api._protocols import plugins as plugins, transports as transports
    from flext_api._protocols.plugins import FlextApiPlugins as FlextApiPlugins
    from flext_api._protocols.transports import FlextApiTransports as FlextApiTransports
    from flext_api._utilities import (
        adapters as adapters,
        app as app,
        client as client,
        lifecycle_manager as lifecycle_manager,
        middleware as middleware,
        registry as registry,
        serializers as serializers,
        server_factory as server_factory,
        settings_manager as settings_manager,
        storage as storage,
        webhook as webhook,
    )
    from flext_api._utilities.adapters import FlextApiAdapters as FlextApiAdapters
    from flext_api._utilities.app import FlextApiApp as FlextApiApp
    from flext_api._utilities.client import FlextApiClient as FlextApiClient
    from flext_api._utilities.lifecycle_manager import (
        FlextApiLifecycleManager as FlextApiLifecycleManager,
    )
    from flext_api._utilities.middleware import FlextApiMiddleware as FlextApiMiddleware
    from flext_api._utilities.registry import FlextApiRegistry as FlextApiRegistry
    from flext_api._utilities.serializers import (
        FlextApiSerializers as FlextApiSerializers,
    )
    from flext_api._utilities.server_factory import (
        FlextApiServerFactory as FlextApiServerFactory,
    )
    from flext_api._utilities.settings_manager import (
        FlextApiSettingsManager as FlextApiSettingsManager,
    )
    from flext_api._utilities.storage import FlextApiStorage as FlextApiStorage
    from flext_api._utilities.webhook import FlextWebhookHandler as FlextWebhookHandler
    from flext_api.api import FlextApi as FlextApi
    from flext_api.constants import (
        FlextApiConstants as FlextApiConstants,
        FlextApiConstants as c,
    )
    from flext_api.errors import FlextApiErrors as FlextApiErrors
    from flext_api.models import FlextApiModels as FlextApiModels, FlextApiModels as m
    from flext_api.protocol_impls import (
        base as base,
        http as http,
        http_client as http_client,
        logger as logger,
        rfc as rfc,
        sse as sse,
        storage_backend as storage_backend,
        websocket as websocket,
    )
    from flext_api.protocol_impls.base import (
        FlextApiBaseProtocolImplementation as FlextApiBaseProtocolImplementation,
    )
    from flext_api.protocol_impls.http import (
        FlextWebProtocolPlugin as FlextWebProtocolPlugin,
    )
    from flext_api.protocol_impls.http_client import (
        FlextWebClientImplementation as FlextWebClientImplementation,
    )
    from flext_api.protocol_impls.logger import (
        FlextApiLoggerProtocolImplementation as FlextApiLoggerProtocolImplementation,
    )
    from flext_api.protocol_impls.rfc import (
        FlextApiRfcProtocolImplementation as FlextApiRfcProtocolImplementation,
    )
    from flext_api.protocol_impls.sse import (
        FlextApiSseProtocolPlugin as FlextApiSseProtocolPlugin,
    )
    from flext_api.protocol_impls.storage_backend import (
        FlextApiStorageBackendImplementation as FlextApiStorageBackendImplementation,
    )
    from flext_api.protocol_impls.websocket import (
        FlextApiWebsocketProtocolPlugin as FlextApiWebsocketProtocolPlugin,
    )
    from flext_api.protocols import (
        FlextApiProtocols as FlextApiProtocols,
        FlextApiProtocols as p,
    )
    from flext_api.schemas import (
        asyncapi as asyncapi,
        jsonschema as jsonschema,
        openapi as openapi,
    )
    from flext_api.schemas._shared import (
        FlextApiSchemaShared as FlextApiSchemaShared,
        is_container_value as is_container_value,
        is_object_mapping as is_object_mapping,
        load_and_validate_schema_document as load_and_validate_schema_document,
        load_schema_document as load_schema_document,
        normalize_json_object as normalize_json_object,
        parse_dict_field as parse_dict_field,
        parse_int_field as parse_int_field,
        parse_string_field as parse_string_field,
        to_general_value as to_general_value,
    )
    from flext_api.schemas.asyncapi import (
        FlextApiAsyncapiSchemaValidator as FlextApiAsyncapiSchemaValidator,
    )
    from flext_api.schemas.jsonschema import (
        FlextApiJsonschemaValidator as FlextApiJsonschemaValidator,
    )
    from flext_api.schemas.openapi import (
        FlextApiOpenapiSchemaValidator as FlextApiOpenapiSchemaValidator,
    )
    from flext_api.server import FlextApiServer as FlextApiServer
    from flext_api.settings import FlextApiSettings as FlextApiSettings
    from flext_api.typings import FlextApiTypes as FlextApiTypes, FlextApiTypes as t
    from flext_api.utilities import (
        FlextApiUtilities as FlextApiUtilities,
        FlextApiUtilities as u,
    )

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "FlextApi": ["flext_api.api", "FlextApi"],
    "FlextApiAdapters": ["flext_api._utilities.adapters", "FlextApiAdapters"],
    "FlextApiApp": ["flext_api._utilities.app", "FlextApiApp"],
    "FlextApiAsyncapiSchemaValidator": [
        "flext_api.schemas.asyncapi",
        "FlextApiAsyncapiSchemaValidator",
    ],
    "FlextApiBaseProtocolImplementation": [
        "flext_api.protocol_impls.base",
        "FlextApiBaseProtocolImplementation",
    ],
    "FlextApiClient": ["flext_api._utilities.client", "FlextApiClient"],
    "FlextApiConstants": ["flext_api.constants", "FlextApiConstants"],
    "FlextApiErrors": ["flext_api.errors", "FlextApiErrors"],
    "FlextApiJsonschemaValidator": [
        "flext_api.schemas.jsonschema",
        "FlextApiJsonschemaValidator",
    ],
    "FlextApiLifecycleManager": [
        "flext_api._utilities.lifecycle_manager",
        "FlextApiLifecycleManager",
    ],
    "FlextApiLoggerProtocolImplementation": [
        "flext_api.protocol_impls.logger",
        "FlextApiLoggerProtocolImplementation",
    ],
    "FlextApiMiddleware": ["flext_api._utilities.middleware", "FlextApiMiddleware"],
    "FlextApiModels": ["flext_api.models", "FlextApiModels"],
    "FlextApiOpenapiSchemaValidator": [
        "flext_api.schemas.openapi",
        "FlextApiOpenapiSchemaValidator",
    ],
    "FlextApiPlugins": ["flext_api._protocols.plugins", "FlextApiPlugins"],
    "FlextApiProtocols": ["flext_api.protocols", "FlextApiProtocols"],
    "FlextApiRegistry": ["flext_api._utilities.registry", "FlextApiRegistry"],
    "FlextApiRfcProtocolImplementation": [
        "flext_api.protocol_impls.rfc",
        "FlextApiRfcProtocolImplementation",
    ],
    "FlextApiSchemaShared": ["flext_api.schemas._shared", "FlextApiSchemaShared"],
    "FlextApiSerializers": ["flext_api._utilities.serializers", "FlextApiSerializers"],
    "FlextApiServer": ["flext_api.server", "FlextApiServer"],
    "FlextApiServerFactory": [
        "flext_api._utilities.server_factory",
        "FlextApiServerFactory",
    ],
    "FlextApiSettings": ["flext_api.settings", "FlextApiSettings"],
    "FlextApiSettingsManager": [
        "flext_api._utilities.settings_manager",
        "FlextApiSettingsManager",
    ],
    "FlextApiSseProtocolPlugin": [
        "flext_api.protocol_impls.sse",
        "FlextApiSseProtocolPlugin",
    ],
    "FlextApiStorage": ["flext_api._utilities.storage", "FlextApiStorage"],
    "FlextApiStorageBackendImplementation": [
        "flext_api.protocol_impls.storage_backend",
        "FlextApiStorageBackendImplementation",
    ],
    "FlextApiTransports": ["flext_api._protocols.transports", "FlextApiTransports"],
    "FlextApiTypes": ["flext_api.typings", "FlextApiTypes"],
    "FlextApiUtilities": ["flext_api.utilities", "FlextApiUtilities"],
    "FlextApiWebsocketProtocolPlugin": [
        "flext_api.protocol_impls.websocket",
        "FlextApiWebsocketProtocolPlugin",
    ],
    "FlextWebClientImplementation": [
        "flext_api.protocol_impls.http_client",
        "FlextWebClientImplementation",
    ],
    "FlextWebProtocolPlugin": [
        "flext_api.protocol_impls.http",
        "FlextWebProtocolPlugin",
    ],
    "FlextWebhookHandler": ["flext_api._utilities.webhook", "FlextWebhookHandler"],
    "_protocols": ["flext_api._protocols", ""],
    "_utilities": ["flext_api._utilities", ""],
    "adapters": ["flext_api._utilities.adapters", ""],
    "api": ["flext_api.api", ""],
    "app": ["flext_api._utilities.app", ""],
    "asyncapi": ["flext_api.schemas.asyncapi", ""],
    "base": ["flext_api.protocol_impls.base", ""],
    "c": ["flext_api.constants", "FlextApiConstants"],
    "client": ["flext_api._utilities.client", ""],
    "constants": ["flext_api.constants", ""],
    "d": ["flext_web", "d"],
    "e": ["flext_web", "e"],
    "errors": ["flext_api.errors", ""],
    "h": ["flext_web", "h"],
    "http": ["flext_api.protocol_impls.http", ""],
    "http_client": ["flext_api.protocol_impls.http_client", ""],
    "is_container_value": ["flext_api.schemas._shared", "is_container_value"],
    "is_object_mapping": ["flext_api.schemas._shared", "is_object_mapping"],
    "jsonschema": ["flext_api.schemas.jsonschema", ""],
    "lifecycle_manager": ["flext_api._utilities.lifecycle_manager", ""],
    "load_and_validate_schema_document": [
        "flext_api.schemas._shared",
        "load_and_validate_schema_document",
    ],
    "load_schema_document": ["flext_api.schemas._shared", "load_schema_document"],
    "logger": ["flext_api.protocol_impls.logger", ""],
    "m": ["flext_api.models", "FlextApiModels"],
    "middleware": ["flext_api._utilities.middleware", ""],
    "models": ["flext_api.models", ""],
    "normalize_json_object": ["flext_api.schemas._shared", "normalize_json_object"],
    "openapi": ["flext_api.schemas.openapi", ""],
    "p": ["flext_api.protocols", "FlextApiProtocols"],
    "parse_dict_field": ["flext_api.schemas._shared", "parse_dict_field"],
    "parse_int_field": ["flext_api.schemas._shared", "parse_int_field"],
    "parse_string_field": ["flext_api.schemas._shared", "parse_string_field"],
    "plugins": ["flext_api._protocols.plugins", ""],
    "protocol_impls": ["flext_api.protocol_impls", ""],
    "protocols": ["flext_api.protocols", ""],
    "r": ["flext_web", "r"],
    "registry": ["flext_api._utilities.registry", ""],
    "rfc": ["flext_api.protocol_impls.rfc", ""],
    "s": ["flext_web", "s"],
    "schemas": ["flext_api.schemas", ""],
    "serializers": ["flext_api._utilities.serializers", ""],
    "server": ["flext_api.server", ""],
    "server_factory": ["flext_api._utilities.server_factory", ""],
    "settings": ["flext_api.settings", ""],
    "settings_manager": ["flext_api._utilities.settings_manager", ""],
    "sse": ["flext_api.protocol_impls.sse", ""],
    "storage": ["flext_api._utilities.storage", ""],
    "storage_backend": ["flext_api.protocol_impls.storage_backend", ""],
    "t": ["flext_api.typings", "FlextApiTypes"],
    "to_general_value": ["flext_api.schemas._shared", "to_general_value"],
    "transports": ["flext_api._protocols.transports", ""],
    "typings": ["flext_api.typings", ""],
    "u": ["flext_api.utilities", "FlextApiUtilities"],
    "utilities": ["flext_api.utilities", ""],
    "webhook": ["flext_api._utilities.webhook", ""],
    "websocket": ["flext_api.protocol_impls.websocket", ""],
    "x": ["flext_web", "x"],
}

_EXPORTS: Sequence[str] = [
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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)

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
    from flext_api._protocols import (
        FlextApiPlugins,
        FlextApiTransports,
        plugins,
        transports,
    )

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
        adapters,
        app,
        client,
        lifecycle_manager,
        middleware,
        registry,
        serializers,
        server_factory,
        settings_manager,
        storage,
        webhook,
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
    import flext_api.protocol_impls as _flext_api_protocol_impls
    from flext_api.models import FlextApiModels, FlextApiModels as m

    protocol_impls = _flext_api_protocol_impls
    import flext_api.protocols as _flext_api_protocols
    from flext_api.protocol_impls import (
        FlextApiBaseProtocolImplementation,
        FlextApiLoggerProtocolImplementation,
        FlextApiRfcProtocolImplementation,
        FlextApiSseProtocolPlugin,
        FlextApiStorageBackendImplementation,
        FlextApiWebsocketProtocolPlugin,
        FlextWebClientImplementation,
        FlextWebProtocolPlugin,
        base,
        http,
        http_client,
        logger,
        rfc,
        sse,
        storage_backend,
        websocket,
    )

    protocols = _flext_api_protocols
    import flext_api.schemas as _flext_api_schemas
    from flext_api.protocols import FlextApiProtocols, FlextApiProtocols as p

    schemas = _flext_api_schemas
    import flext_api.server as _flext_api_server
    from flext_api.schemas import (
        FlextApiAsyncapiSchemaValidator,
        FlextApiJsonschemaValidator,
        FlextApiOpenapiSchemaValidator,
        FlextApiSchemaShared,
        asyncapi,
        is_container_value,
        is_object_mapping,
        jsonschema,
        load_and_validate_schema_document,
        load_schema_document,
        normalize_json_object,
        openapi,
        parse_dict_field,
        parse_int_field,
        parse_string_field,
        to_general_value,
    )

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
        "FlextApi": ("flext_api.api", "FlextApi"),
        "FlextApiConstants": ("flext_api.constants", "FlextApiConstants"),
        "FlextApiErrors": ("flext_api.errors", "FlextApiErrors"),
        "FlextApiModels": ("flext_api.models", "FlextApiModels"),
        "FlextApiProtocols": ("flext_api.protocols", "FlextApiProtocols"),
        "FlextApiServer": ("flext_api.server", "FlextApiServer"),
        "FlextApiSettings": ("flext_api.settings", "FlextApiSettings"),
        "FlextApiTypes": ("flext_api.typings", "FlextApiTypes"),
        "FlextApiUtilities": ("flext_api.utilities", "FlextApiUtilities"),
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

# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext api package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_api.__version__ import (
    __all__,
    __author__,
    __author_email__,
    __description__,
    __license__,
    __title__,
    __url__,
    __version_info__,
)
from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _TYPE_CHECKING:
    from flext_api import (
        _protocols,
        _utilities,
        adapters,
        api,
        app,
        asyncapi,
        base,
        client,
        constants,
        errors,
        http,
        http_client,
        jsonschema,
        lifecycle_manager,
        logger,
        middleware,
        models,
        openapi,
        plugins,
        protocol_impls,
        protocols,
        registry,
        rfc,
        schemas,
        serializers,
        server,
        server_factory,
        settings,
        settings_manager,
        sse,
        storage,
        storage_backend,
        transports,
        typings,
        utilities,
        webhook,
        websocket,
    )
    from flext_api._protocols import FlextApiPlugins, FlextApiTransports
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
    from flext_api.api import FlextApi
    from flext_api.constants import FlextApiConstants, FlextApiConstants as c
    from flext_api.errors import FlextApiErrors
    from flext_api.models import FlextApiModels, FlextApiModels as m
    from flext_api.protocol_impls import (
        FlextApiBaseProtocolImplementation,
        FlextApiLoggerProtocolImplementation,
        FlextApiRfcProtocolImplementation,
        FlextApiSseProtocolPlugin,
        FlextApiStorageBackendImplementation,
        FlextApiWebsocketProtocolPlugin,
        FlextWebClientImplementation,
        FlextWebProtocolPlugin,
    )
    from flext_api.protocols import FlextApiProtocols, FlextApiProtocols as p
    from flext_api.schemas import (
        FlextApiAsyncapiSchemaValidator,
        FlextApiJsonschemaValidator,
        FlextApiOpenapiSchemaValidator,
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
    from flext_api.server import FlextApiServer
    from flext_api.settings import FlextApiSettings
    from flext_api.typings import FlextApiTypes, FlextApiTypes as t
    from flext_api.utilities import FlextApiUtilities, FlextApiUtilities as u
    from flext_core import FlextTypes
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s

__version__ = "0.12.0-dev"


_LAZY_IMPORTS: FlextTypes.LazyImportIndex = merge_lazy_imports(
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
        "_protocols": "flext_api._protocols",
        "_utilities": "flext_api._utilities",
        "adapters": "flext_api.adapters",
        "api": "flext_api.api",
        "app": "flext_api.app",
        "asyncapi": "flext_api.asyncapi",
        "base": "flext_api.base",
        "c": ("flext_api.constants", "FlextApiConstants"),
        "client": "flext_api.client",
        "constants": "flext_api.constants",
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_core.exceptions", "FlextExceptions"),
        "errors": "flext_api.errors",
        "h": ("flext_core.handlers", "FlextHandlers"),
        "http": "flext_api.http",
        "http_client": "flext_api.http_client",
        "jsonschema": "flext_api.jsonschema",
        "lifecycle_manager": "flext_api.lifecycle_manager",
        "logger": "flext_api.logger",
        "m": ("flext_api.models", "FlextApiModels"),
        "middleware": "flext_api.middleware",
        "models": "flext_api.models",
        "openapi": "flext_api.openapi",
        "p": ("flext_api.protocols", "FlextApiProtocols"),
        "plugins": "flext_api.plugins",
        "protocol_impls": "flext_api.protocol_impls",
        "protocols": "flext_api.protocols",
        "r": ("flext_core.result", "FlextResult"),
        "registry": "flext_api.registry",
        "rfc": "flext_api.rfc",
        "s": ("flext_core.service", "FlextService"),
        "schemas": "flext_api.schemas",
        "serializers": "flext_api.serializers",
        "server": "flext_api.server",
        "server_factory": "flext_api.server_factory",
        "settings": "flext_api.settings",
        "settings_manager": "flext_api.settings_manager",
        "sse": "flext_api.sse",
        "storage": "flext_api.storage",
        "storage_backend": "flext_api.storage_backend",
        "t": ("flext_api.typings", "FlextApiTypes"),
        "transports": "flext_api.transports",
        "typings": "flext_api.typings",
        "u": ("flext_api.utilities", "FlextApiUtilities"),
        "utilities": "flext_api.utilities",
        "webhook": "flext_api.webhook",
        "websocket": "flext_api.websocket",
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    [
        "__all__",
        "__author__",
        "__author_email__",
        "__description__",
        "__license__",
        "__title__",
        "__url__",
        "__version__",
        "__version_info__",
    ],
)

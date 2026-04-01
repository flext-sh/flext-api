# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext api package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports, merge_lazy_imports

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

if _TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_web import d, e, h, r, s, x

    from flext_api import (
        _protocols,
        _utilities,
        api,
        constants,
        errors,
        models,
        protocol_impls,
        protocols,
        schemas,
        server,
        settings,
        typings,
        utilities,
    )
    from flext_api._protocols import (
        FlextApiPlugins,
        FlextApiTransports,
        plugins,
        transports,
    )
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
        base,
        http,
        http_client,
        logger,
        rfc,
        sse,
        storage_backend,
        websocket,
    )
    from flext_api.protocols import FlextApiProtocols, FlextApiProtocols as p
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
    from flext_api.server import FlextApiServer
    from flext_api.settings import FlextApiSettings
    from flext_api.typings import FlextApiTypes, FlextApiTypes as t
    from flext_api.utilities import FlextApiUtilities, FlextApiUtilities as u

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = merge_lazy_imports(
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
        "api": "flext_api.api",
        "c": ("flext_api.constants", "FlextApiConstants"),
        "constants": "flext_api.constants",
        "d": "flext_web",
        "e": "flext_web",
        "errors": "flext_api.errors",
        "h": "flext_web",
        "m": ("flext_api.models", "FlextApiModels"),
        "models": "flext_api.models",
        "p": ("flext_api.protocols", "FlextApiProtocols"),
        "protocol_impls": "flext_api.protocol_impls",
        "protocols": "flext_api.protocols",
        "r": "flext_web",
        "s": "flext_web",
        "schemas": "flext_api.schemas",
        "server": "flext_api.server",
        "settings": "flext_api.settings",
        "t": ("flext_api.typings", "FlextApiTypes"),
        "typings": "flext_api.typings",
        "u": ("flext_api.utilities", "FlextApiUtilities"),
        "utilities": "flext_api.utilities",
        "x": "flext_web",
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    [
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

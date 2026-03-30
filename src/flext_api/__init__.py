# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext api package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

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

if TYPE_CHECKING:
    from flext_web import *

    from flext_api import (
        api,
        constants,
        errors,
        models,
        protocols,
        server,
        settings,
        typings,
        utilities,
    )
    from flext_api._protocols import *
    from flext_api._utilities import *
    from flext_api.api import *
    from flext_api.constants import *
    from flext_api.errors import *
    from flext_api.models import *
    from flext_api.protocol_impls import *
    from flext_api.protocols import *
    from flext_api.schemas import *
    from flext_api.server import *
    from flext_api.settings import *
    from flext_api.typings import *
    from flext_api.utilities import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "FlextApi": "flext_api.api",
    "FlextApiAdapters": "flext_api._utilities.adapters",
    "FlextApiApp": "flext_api._utilities.app",
    "FlextApiAsyncapiSchemaValidator": "flext_api.schemas.asyncapi",
    "FlextApiBaseProtocolImplementation": "flext_api.protocol_impls.base",
    "FlextApiClient": "flext_api._utilities.client",
    "FlextApiConstants": "flext_api.constants",
    "FlextApiErrors": "flext_api.errors",
    "FlextApiJsonschemaValidator": "flext_api.schemas.jsonschema",
    "FlextApiLifecycleManager": "flext_api._utilities.lifecycle_manager",
    "FlextApiLoggerProtocolImplementation": "flext_api.protocol_impls.logger",
    "FlextApiMiddleware": "flext_api._utilities.middleware",
    "FlextApiModels": "flext_api.models",
    "FlextApiOpenapiSchemaValidator": "flext_api.schemas.openapi",
    "FlextApiPlugins": "flext_api._protocols.plugins",
    "FlextApiProtocols": "flext_api.protocols",
    "FlextApiRegistry": "flext_api._utilities.registry",
    "FlextApiRfcProtocolImplementation": "flext_api.protocol_impls.rfc",
    "FlextApiSchemaShared": "flext_api.schemas._shared",
    "FlextApiSerializers": "flext_api._utilities.serializers",
    "FlextApiServer": "flext_api.server",
    "FlextApiServerFactory": "flext_api._utilities.server_factory",
    "FlextApiSettings": "flext_api.settings",
    "FlextApiSettingsManager": "flext_api._utilities.settings_manager",
    "FlextApiSseProtocolPlugin": "flext_api.protocol_impls.sse",
    "FlextApiStorage": "flext_api._utilities.storage",
    "FlextApiStorageBackendImplementation": "flext_api.protocol_impls.storage_backend",
    "FlextApiTransports": "flext_api._protocols.transports",
    "FlextApiTypes": "flext_api.typings",
    "FlextApiUtilities": "flext_api.utilities",
    "FlextApiWebsocketProtocolPlugin": "flext_api.protocol_impls.websocket",
    "FlextWebClientImplementation": "flext_api.protocol_impls.http_client",
    "FlextWebProtocolPlugin": "flext_api.protocol_impls.http",
    "FlextWebhookHandler": "flext_api._utilities.webhook",
    "_protocols": "flext_api._protocols",
    "_utilities": "flext_api._utilities",
    "adapters": "flext_api._utilities.adapters",
    "api": "flext_api.api",
    "app": "flext_api._utilities.app",
    "asyncapi": "flext_api.schemas.asyncapi",
    "base": "flext_api.protocol_impls.base",
    "c": ["flext_api.constants", "FlextApiConstants"],
    "client": "flext_api._utilities.client",
    "constants": "flext_api.constants",
    "d": "flext_web",
    "e": "flext_web",
    "errors": "flext_api.errors",
    "h": "flext_web",
    "http": "flext_api.protocol_impls.http",
    "http_client": "flext_api.protocol_impls.http_client",
    "is_container_value": "flext_api.schemas._shared",
    "is_object_mapping": "flext_api.schemas._shared",
    "jsonschema": "flext_api.schemas.jsonschema",
    "lifecycle_manager": "flext_api._utilities.lifecycle_manager",
    "load_and_validate_schema_document": "flext_api.schemas._shared",
    "load_schema_document": "flext_api.schemas._shared",
    "logger": "flext_api.protocol_impls.logger",
    "m": ["flext_api.models", "FlextApiModels"],
    "middleware": "flext_api._utilities.middleware",
    "models": "flext_api.models",
    "normalize_json_object": "flext_api.schemas._shared",
    "openapi": "flext_api.schemas.openapi",
    "p": ["flext_api.protocols", "FlextApiProtocols"],
    "parse_dict_field": "flext_api.schemas._shared",
    "parse_int_field": "flext_api.schemas._shared",
    "parse_string_field": "flext_api.schemas._shared",
    "plugins": "flext_api._protocols.plugins",
    "protocol_impls": "flext_api.protocol_impls",
    "protocols": "flext_api.protocols",
    "r": "flext_web",
    "registry": "flext_api._utilities.registry",
    "rfc": "flext_api.protocol_impls.rfc",
    "s": "flext_web",
    "schemas": "flext_api.schemas",
    "serializers": "flext_api._utilities.serializers",
    "server": "flext_api.server",
    "server_factory": "flext_api._utilities.server_factory",
    "settings": "flext_api.settings",
    "settings_manager": "flext_api._utilities.settings_manager",
    "sse": "flext_api.protocol_impls.sse",
    "storage": "flext_api._utilities.storage",
    "storage_backend": "flext_api.protocol_impls.storage_backend",
    "t": ["flext_api.typings", "FlextApiTypes"],
    "to_general_value": "flext_api.schemas._shared",
    "transports": "flext_api._protocols.transports",
    "typings": "flext_api.typings",
    "u": ["flext_api.utilities", "FlextApiUtilities"],
    "utilities": "flext_api.utilities",
    "webhook": "flext_api._utilities.webhook",
    "websocket": "flext_api.protocol_impls.websocket",
    "x": "flext_web",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, sorted(_LAZY_IMPORTS))

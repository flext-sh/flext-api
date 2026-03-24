# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Flext api package."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_web import d, e, h, r, s, x

    from flext_api import protocol_impls, schemas
    from flext_api.__version__ import (
        __all__,
        __author__,
        __author_email__,
        __description__,
        __license__,
        __title__,
        __url__,
    )
    from flext_api.adapters import FlextApiAdapters
    from flext_api.api import FlextApi
    from flext_api.app import FlextApiApp
    from flext_api.client import FlextApiClient
    from flext_api.constants import FlextApiConstants, FlextApiConstants as c
    from flext_api.exceptions import HttpError
    from flext_api.lifecycle_manager import FlextApiLifecycleManager
    from flext_api.middleware import FlextApiMiddleware
    from flext_api.models import FlextApiModels, FlextApiModels as m
    from flext_api.plugins import FlextApiPlugins
    from flext_api.protocol_impls.base import BaseProtocolImplementation
    from flext_api.protocol_impls.http import FlextWebProtocolPlugin
    from flext_api.protocol_impls.http_client import FlextWebClientImplementation
    from flext_api.protocol_impls.logger import LoggerProtocolImplementation
    from flext_api.protocol_impls.rfc import RFCProtocolImplementation
    from flext_api.protocol_impls.sse import SSEProtocolPlugin
    from flext_api.protocol_impls.storage_backend import StorageBackendImplementation
    from flext_api.protocol_impls.websocket import WebSocketProtocolPlugin
    from flext_api.protocols import FlextApiProtocols, FlextApiProtocols as p
    from flext_api.registry import FlextApiRegistry
    from flext_api.schemas._shared import (
        DictField,
        IntField,
        StringField,
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
    from flext_api.schemas.asyncapi import AsyncAPISchemaValidator
    from flext_api.schemas.jsonschema import JSONSchemaValidator
    from flext_api.schemas.openapi import OpenAPISchemaValidator
    from flext_api.serializers import FlextApiSerializers
    from flext_api.server import FlextApiServer
    from flext_api.server_factory import FlextApiServerFactory
    from flext_api.settings import FlextApiSettings
    from flext_api.settings_manager import FlextApiSettingsManager
    from flext_api.storage import FlextApiStorage
    from flext_api.transports import FlextApiTransports
    from flext_api.typings import FlextApiTypes, FlextApiTypes as t
    from flext_api.utilities import FlextApiUtilities, FlextApiUtilities as u
    from flext_api.webhook import FlextWebhookHandler

_LAZY_IMPORTS: Mapping[str, tuple[str, str]] = {
    "AsyncAPISchemaValidator": (
        "flext_api.schemas.asyncapi",
        "AsyncAPISchemaValidator",
    ),
    "BaseProtocolImplementation": (
        "flext_api.protocol_impls.base",
        "BaseProtocolImplementation",
    ),
    "DictField": ("flext_api.schemas._shared", "DictField"),
    "FlextApi": ("flext_api.api", "FlextApi"),
    "FlextApiAdapters": ("flext_api.adapters", "FlextApiAdapters"),
    "FlextApiApp": ("flext_api.app", "FlextApiApp"),
    "FlextApiClient": ("flext_api.client", "FlextApiClient"),
    "FlextApiConstants": ("flext_api.constants", "FlextApiConstants"),
    "FlextApiLifecycleManager": (
        "flext_api.lifecycle_manager",
        "FlextApiLifecycleManager",
    ),
    "FlextApiMiddleware": ("flext_api.middleware", "FlextApiMiddleware"),
    "FlextApiModels": ("flext_api.models", "FlextApiModels"),
    "FlextApiPlugins": ("flext_api.plugins", "FlextApiPlugins"),
    "FlextApiProtocols": ("flext_api.protocols", "FlextApiProtocols"),
    "FlextApiRegistry": ("flext_api.registry", "FlextApiRegistry"),
    "FlextApiSerializers": ("flext_api.serializers", "FlextApiSerializers"),
    "FlextApiServer": ("flext_api.server", "FlextApiServer"),
    "FlextApiServerFactory": ("flext_api.server_factory", "FlextApiServerFactory"),
    "FlextApiSettings": ("flext_api.settings", "FlextApiSettings"),
    "FlextApiSettingsManager": (
        "flext_api.settings_manager",
        "FlextApiSettingsManager",
    ),
    "FlextApiStorage": ("flext_api.storage", "FlextApiStorage"),
    "FlextApiTransports": ("flext_api.transports", "FlextApiTransports"),
    "FlextApiTypes": ("flext_api.typings", "FlextApiTypes"),
    "FlextApiUtilities": ("flext_api.utilities", "FlextApiUtilities"),
    "FlextWebClientImplementation": (
        "flext_api.protocol_impls.http_client",
        "FlextWebClientImplementation",
    ),
    "FlextWebProtocolPlugin": (
        "flext_api.protocol_impls.http",
        "FlextWebProtocolPlugin",
    ),
    "FlextWebhookHandler": ("flext_api.webhook", "FlextWebhookHandler"),
    "HttpError": ("flext_api.exceptions", "HttpError"),
    "IntField": ("flext_api.schemas._shared", "IntField"),
    "JSONSchemaValidator": ("flext_api.schemas.jsonschema", "JSONSchemaValidator"),
    "LoggerProtocolImplementation": (
        "flext_api.protocol_impls.logger",
        "LoggerProtocolImplementation",
    ),
    "OpenAPISchemaValidator": ("flext_api.schemas.openapi", "OpenAPISchemaValidator"),
    "RFCProtocolImplementation": (
        "flext_api.protocol_impls.rfc",
        "RFCProtocolImplementation",
    ),
    "SSEProtocolPlugin": ("flext_api.protocol_impls.sse", "SSEProtocolPlugin"),
    "StorageBackendImplementation": (
        "flext_api.protocol_impls.storage_backend",
        "StorageBackendImplementation",
    ),
    "StringField": ("flext_api.schemas._shared", "StringField"),
    "WebSocketProtocolPlugin": (
        "flext_api.protocol_impls.websocket",
        "WebSocketProtocolPlugin",
    ),
    "__all__": ("flext_api.__version__", "__all__"),
    "__author__": ("flext_api.__version__", "__author__"),
    "__author_email__": ("flext_api.__version__", "__author_email__"),
    "__description__": ("flext_api.__version__", "__description__"),
    "__license__": ("flext_api.__version__", "__license__"),
    "__title__": ("flext_api.__version__", "__title__"),
    "__url__": ("flext_api.__version__", "__url__"),
    "c": ("flext_api.constants", "FlextApiConstants"),
    "d": ("flext_web", "d"),
    "e": ("flext_web", "e"),
    "h": ("flext_web", "h"),
    "is_container_value": ("flext_api.schemas._shared", "is_container_value"),
    "is_object_mapping": ("flext_api.schemas._shared", "is_object_mapping"),
    "load_and_validate_schema_document": (
        "flext_api.schemas._shared",
        "load_and_validate_schema_document",
    ),
    "load_schema_document": ("flext_api.schemas._shared", "load_schema_document"),
    "m": ("flext_api.models", "FlextApiModels"),
    "normalize_json_object": ("flext_api.schemas._shared", "normalize_json_object"),
    "p": ("flext_api.protocols", "FlextApiProtocols"),
    "parse_dict_field": ("flext_api.schemas._shared", "parse_dict_field"),
    "parse_int_field": ("flext_api.schemas._shared", "parse_int_field"),
    "parse_string_field": ("flext_api.schemas._shared", "parse_string_field"),
    "protocol_impls": ("flext_api.protocol_impls", ""),
    "r": ("flext_web", "r"),
    "s": ("flext_web", "s"),
    "schemas": ("flext_api.schemas", ""),
    "t": ("flext_api.typings", "FlextApiTypes"),
    "to_general_value": ("flext_api.schemas._shared", "to_general_value"),
    "u": ("flext_api.utilities", "FlextApiUtilities"),
    "x": ("flext_web", "x"),
}

__all__ = [
    "AsyncAPISchemaValidator",
    "BaseProtocolImplementation",
    "DictField",
    "FlextApi",
    "FlextApiAdapters",
    "FlextApiApp",
    "FlextApiClient",
    "FlextApiConstants",
    "FlextApiLifecycleManager",
    "FlextApiMiddleware",
    "FlextApiModels",
    "FlextApiPlugins",
    "FlextApiProtocols",
    "FlextApiRegistry",
    "FlextApiSerializers",
    "FlextApiServer",
    "FlextApiServerFactory",
    "FlextApiSettings",
    "FlextApiSettingsManager",
    "FlextApiStorage",
    "FlextApiTransports",
    "FlextApiTypes",
    "FlextApiUtilities",
    "FlextWebClientImplementation",
    "FlextWebProtocolPlugin",
    "FlextWebhookHandler",
    "HttpError",
    "IntField",
    "JSONSchemaValidator",
    "LoggerProtocolImplementation",
    "OpenAPISchemaValidator",
    "RFCProtocolImplementation",
    "SSEProtocolPlugin",
    "StorageBackendImplementation",
    "StringField",
    "WebSocketProtocolPlugin",
    "__all__",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
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
    "protocol_impls",
    "r",
    "s",
    "schemas",
    "t",
    "to_general_value",
    "u",
    "x",
]


_LAZY_CACHE: MutableMapping[str, FlextTypes.ModuleExport] = {}


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562).

    A local cache ``_LAZY_CACHE`` persists resolved objects across repeated
    accesses during process lifetime.

    Args:
        name: Attribute name requested by dir()/import.

    Returns:
        Lazy-loaded module export type.

    Raises:
        AttributeError: If attribute not registered.

    """
    if name in _LAZY_CACHE:
        return _LAZY_CACHE[name]

    value = lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)
    _LAZY_CACHE[name] = value
    return value


def __dir__() -> Sequence[str]:
    """Return list of available attributes for dir() and autocomplete.

    Returns:
        List of public names from module exports.

    """
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)

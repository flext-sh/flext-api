"""Lazy export wiring for the flext_api package."""

from __future__ import annotations

import sys
from collections.abc import Callable, Mapping, Sequence
from types import ModuleType
from typing import Final

from flext_core import FlextTypes
from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

type LazyModuleExport = (
    FlextTypes.JsonValue
    | Mapping[str, LazyModuleExport]
    | Sequence[str]
    | ModuleType
    | type
    | Callable[..., LazyModuleExport]
    | Callable[..., FlextTypes.JsonValue | Sequence[str] | ModuleType | type | None]
    | None
)

_MODULE_NAME: Final = "flext_api"

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "AsyncAPISchemaValidator": ("flext_api.schemas", "AsyncAPISchemaValidator"),
    "BaseProtocolImplementation": (
        "flext_api.protocol_impls",
        "BaseProtocolImplementation",
    ),
    "FlextApi": ("flext_api.api", "FlextApi"),
    "FlextApiAdapters": ("flext_api.adapters", "FlextApiAdapters"),
    "FlextApiApp": ("flext_api.app", "FlextApiApp"),
    "FlextApiClient": ("flext_api.client", "FlextApiClient"),
    "FlextApiConstants": ("flext_api.constants", "FlextApiConstants"),
    "FlextApiLifecycleManager": (
        "flext_api.lifecycle_manager",
        "FlextApiLifecycleManager",
    ),
    "FlextApiModels": ("flext_api.models", "FlextApiModels"),
    "FlextApiPlugins": ("flext_api.plugins", "FlextApiPlugins"),
    "FlextApiProtocols": ("flext_api.protocols", "FlextApiProtocols"),
    "FlextApiServerFactory": ("flext_api.server_factory", "FlextApiServerFactory"),
    "FlextApiSettings": ("flext_api.settings", "FlextApiSettings"),
    "FlextApiSettingsManager": (
        "flext_api.settings_manager",
        "FlextApiSettingsManager",
    ),
    "FlextApiStorage": ("flext_api.storage", "FlextApiStorage"),
    "FlextApiTypes": ("flext_api.typings", "FlextApiTypes"),
    "FlextApiUtilities": ("flext_api.utilities", "FlextApiUtilities"),
    "FlextWebClientImplementation": (
        "flext_api.protocol_impls",
        "FlextWebClientImplementation",
    ),
    "FlextWebProtocolPlugin": ("flext_api.protocol_impls", "FlextWebProtocolPlugin"),
    "HttpError": ("flext_api.exceptions", "HttpError"),
    "JSONSchemaValidator": ("flext_api.schemas", "JSONSchemaValidator"),
    "OpenAPISchemaValidator": ("flext_api.schemas", "OpenAPISchemaValidator"),
    "RFCProtocolImplementation": (
        "flext_api.protocol_impls",
        "RFCProtocolImplementation",
    ),
    "SSEProtocolPlugin": ("flext_api.protocol_impls", "SSEProtocolPlugin"),
    "StorageBackendImplementation": (
        "flext_api.protocol_impls",
        "StorageBackendImplementation",
    ),
    "WebSocketProtocolPlugin": ("flext_api.protocol_impls", "WebSocketProtocolPlugin"),
    "__version__": ("flext_api.__version__", "__version__"),
    "__version_info__": ("flext_api.__version__", "__version_info__"),
    "c": ("flext_api.constants", "FlextApiConstants"),
    "d": ("flext_core", "FlextDecorators"),
    "e": ("flext_core", "FlextExceptions"),
    "h": ("flext_core", "FlextHandlers"),
    "m": ("flext_api.models", "FlextApiModels"),
    "p": ("flext_api.protocols", "FlextApiProtocols"),
    "r": ("flext_core", "r"),
    "s": ("flext_core", "FlextService"),
    "t": ("flext_api.typings", "FlextApiTypes"),
    "u": ("flext_api.utilities", "FlextApiUtilities"),
    "x": ("flext_core", "FlextMixins"),
}

__all__ = list(_LAZY_IMPORTS)


def __getattr__(name: str) -> LazyModuleExport:
    """Lazy-load package attributes on first access."""
    return lazy_getattr(
        name, _LAZY_IMPORTS, vars(sys.modules[_MODULE_NAME]), _MODULE_NAME
    )


def __dir__() -> list[str]:
    """Return available package exports for autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(_MODULE_NAME, _LAZY_IMPORTS)

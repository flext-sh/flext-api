# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Protocol impls package."""

from __future__ import annotations

from flext_core.lazy import install_lazy_exports

_LAZY_IMPORTS = {
    "FlextApiBaseProtocolImplementation": (
        "flext_api.protocol_impls.base",
        "FlextApiBaseProtocolImplementation",
    ),
    "FlextApiLoggerProtocolImplementation": (
        "flext_api.protocol_impls.logger",
        "FlextApiLoggerProtocolImplementation",
    ),
    "FlextApiRfcProtocolImplementation": (
        "flext_api.protocol_impls.rfc",
        "FlextApiRfcProtocolImplementation",
    ),
    "FlextApiSseProtocolPlugin": (
        "flext_api.protocol_impls.sse",
        "FlextApiSseProtocolPlugin",
    ),
    "FlextApiStorageBackendImplementation": (
        "flext_api.protocol_impls.storage_backend",
        "FlextApiStorageBackendImplementation",
    ),
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
    "base": "flext_api.protocol_impls.base",
    "c": ("flext_core.constants", "FlextConstants"),
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "http": "flext_api.protocol_impls.http",
    "http_client": "flext_api.protocol_impls.http_client",
    "logger": "flext_api.protocol_impls.logger",
    "m": ("flext_core.models", "FlextModels"),
    "p": ("flext_core.protocols", "FlextProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "rfc": "flext_api.protocol_impls.rfc",
    "s": ("flext_core.service", "FlextService"),
    "sse": "flext_api.protocol_impls.sse",
    "storage_backend": "flext_api.protocol_impls.storage_backend",
    "t": ("flext_core.typings", "FlextTypes"),
    "u": ("flext_core.utilities", "FlextUtilities"),
    "websocket": "flext_api.protocol_impls.websocket",
    "x": ("flext_core.mixins", "FlextMixins"),
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)

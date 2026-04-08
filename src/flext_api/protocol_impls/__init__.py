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
    "http": "flext_api.protocol_impls.http",
    "http_client": "flext_api.protocol_impls.http_client",
    "logger": "flext_api.protocol_impls.logger",
    "rfc": "flext_api.protocol_impls.rfc",
    "sse": "flext_api.protocol_impls.sse",
    "storage_backend": "flext_api.protocol_impls.storage_backend",
    "websocket": "flext_api.protocol_impls.websocket",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)

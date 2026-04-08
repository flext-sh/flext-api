# AUTO-GENERATED FILE — Regenerate with: make gen
from __future__ import annotations

from flext_core.lazy import install_lazy_exports

_LAZY_IMPORTS = {
    "FlextApiBaseProtocolImplementation": ".base",
    "FlextApiLoggerProtocolImplementation": ".logger",
    "FlextApiRfcProtocolImplementation": ".rfc",
    "FlextApiSseProtocolPlugin": ".sse",
    "FlextApiStorageBackendImplementation": ".storage_backend",
    "FlextApiWebsocketProtocolPlugin": ".websocket",
    "FlextWebClientImplementation": ".http_client",
    "FlextWebProtocolPlugin": ".http",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)

# AUTO-GENERATED FILE — Regenerate with: make gen
"""Protocol Impls package."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".base": ("FlextApiBaseProtocolImplementation",),
        ".http": ("FlextWebProtocolPlugin",),
        ".http_client": ("FlextWebClientImplementation",),
        ".logger": ("FlextApiLoggerProtocolImplementation",),
        ".rfc": ("FlextApiRfcProtocolImplementation",),
        ".sse": ("FlextApiSseProtocolPlugin",),
        ".storage_backend": ("FlextApiStorageBackendImplementation",),
        ".websocket": ("FlextApiWebsocketProtocolPlugin",),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)

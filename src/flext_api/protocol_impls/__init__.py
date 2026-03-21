# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Protocol implementations for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes

    from flext_api.protocol_impls.base import BaseProtocolImplementation
    from flext_api.protocol_impls.http import FlextWebProtocolPlugin
    from flext_api.protocol_impls.http_client import FlextWebClientImplementation
    from flext_api.protocol_impls.logger import LoggerProtocolImplementation
    from flext_api.protocol_impls.rfc import RFCProtocolImplementation
    from flext_api.protocol_impls.sse import SSEProtocolPlugin
    from flext_api.protocol_impls.storage_backend import StorageBackendImplementation
    from flext_api.protocol_impls.websocket import WebSocketProtocolPlugin

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "BaseProtocolImplementation": (
        "flext_api.protocol_impls.base",
        "BaseProtocolImplementation",
    ),
    "FlextWebClientImplementation": (
        "flext_api.protocol_impls.http_client",
        "FlextWebClientImplementation",
    ),
    "FlextWebProtocolPlugin": (
        "flext_api.protocol_impls.http",
        "FlextWebProtocolPlugin",
    ),
    "LoggerProtocolImplementation": (
        "flext_api.protocol_impls.logger",
        "LoggerProtocolImplementation",
    ),
    "RFCProtocolImplementation": (
        "flext_api.protocol_impls.rfc",
        "RFCProtocolImplementation",
    ),
    "SSEProtocolPlugin": ("flext_api.protocol_impls.sse", "SSEProtocolPlugin"),
    "StorageBackendImplementation": (
        "flext_api.protocol_impls.storage_backend",
        "StorageBackendImplementation",
    ),
    "WebSocketProtocolPlugin": (
        "flext_api.protocol_impls.websocket",
        "WebSocketProtocolPlugin",
    ),
}

__all__ = [
    "BaseProtocolImplementation",
    "FlextWebClientImplementation",
    "FlextWebProtocolPlugin",
    "LoggerProtocolImplementation",
    "RFCProtocolImplementation",
    "SSEProtocolPlugin",
    "StorageBackendImplementation",
    "WebSocketProtocolPlugin",
]


_LAZY_CACHE: dict[str, object] = {}


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


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete.

    Returns:
        List of public names from module exports.

    """
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)

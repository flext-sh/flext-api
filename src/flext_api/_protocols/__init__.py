# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api. Protocols package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_api._protocols.base import FlextApiProtocolsBase
    from flext_api._protocols.base_grpc import FlextApiProtocolsGrpc
    from flext_api._protocols.base_http import FlextApiProtocolsHttpClient
    from flext_api._protocols.base_resources import FlextApiProtocolsResources
    from flext_api._protocols.base_serialization import FlextApiProtocolsSerializer
    from flext_api._protocols.base_storage import FlextApiProtocolsStorage
    from flext_api._protocols.base_transport import FlextApiProtocolsTransport
    from flext_api._protocols.plugin_manager import FlextApiProtocolPluginManager
    from flext_api._protocols.plugin_types import FlextApiProtocolPluginTypes
    from flext_api._protocols.plugins import FlextApiProtocolPlugins
    from flext_api._protocols.serialization import FlextApiProtocolsSerialization
    from flext_api._protocols.transports import FlextApiProtocolsTransports


__all__: tuple[str, ...] = (
    "FlextApiProtocolPluginManager",
    "FlextApiProtocolPluginTypes",
    "FlextApiProtocolPlugins",
    "FlextApiProtocolsBase",
    "FlextApiProtocolsGrpc",
    "FlextApiProtocolsHttpClient",
    "FlextApiProtocolsResources",
    "FlextApiProtocolsSerialization",
    "FlextApiProtocolsSerializer",
    "FlextApiProtocolsStorage",
    "FlextApiProtocolsTransport",
    "FlextApiProtocolsTransports",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextApiProtocolPluginManager": ".plugin_manager",
        "FlextApiProtocolPluginTypes": ".plugin_types",
        "FlextApiProtocolPlugins": ".plugins",
        "FlextApiProtocolsBase": ".base",
        "FlextApiProtocolsGrpc": ".base_grpc",
        "FlextApiProtocolsHttpClient": ".base_http",
        "FlextApiProtocolsResources": ".base_resources",
        "FlextApiProtocolsSerialization": ".serialization",
        "FlextApiProtocolsSerializer": ".base_serialization",
        "FlextApiProtocolsStorage": ".base_storage",
        "FlextApiProtocolsTransport": ".base_transport",
        "FlextApiProtocolsTransports": ".transports",
    }),
    public_exports=__all__,
)

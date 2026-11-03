# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api. Protocols package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_api._protocols.base import FlextApiProtocolsBase
    from flext_api._protocols.base_grpc import FlextApiProtocolsGrpc
    from flext_api._protocols.base_http import FlextApiProtocolsHttpClient
    from flext_api._protocols.base_resources import FlextApiProtocolsResources
    from flext_api._protocols.base_serialization import FlextApiProtocolsSerializer
    from flext_api._protocols.base_storage import FlextApiProtocolsBaseStorage
    from flext_api._protocols.base_transport import FlextApiProtocolsTransport
    from flext_api._protocols.plugin_manager import FlextApiProtocolPluginManager
    from flext_api._protocols.plugin_types import FlextApiTypesProtocolPlugin
    from flext_api._protocols.plugins import FlextApiProtocolPlugins
    from flext_api._protocols.request import FlextApiProtocolsRequest
    from flext_api._protocols.response import FlextApiProtocolsResponse
    from flext_api._protocols.serialization import FlextApiProtocolsSerialization
    from flext_api._protocols.storage import FlextApiProtocolsStorage
    from flext_api._protocols.transports import FlextApiProtocolsTransports
    from flext_api._protocols.webhook import FlextApiProtocolsWebhook


__all__: tuple[str, ...] = (
    "FlextApiProtocolPluginManager",
    "FlextApiProtocolPlugins",
    "FlextApiProtocolsBase",
    "FlextApiProtocolsBaseStorage",
    "FlextApiProtocolsGrpc",
    "FlextApiProtocolsHttpClient",
    "FlextApiProtocolsRequest",
    "FlextApiProtocolsResources",
    "FlextApiProtocolsResponse",
    "FlextApiProtocolsSerialization",
    "FlextApiProtocolsSerializer",
    "FlextApiProtocolsStorage",
    "FlextApiProtocolsTransport",
    "FlextApiProtocolsTransports",
    "FlextApiProtocolsWebhook",
    "FlextApiTypesProtocolPlugin",
)

install_lazy_exports(
    __name__,
    globals(),
    {
        "FlextApiProtocolPluginManager": ".plugin_manager",
        "FlextApiProtocolPlugins": ".plugins",
        "FlextApiProtocolsBase": ".base",
        "FlextApiProtocolsBaseStorage": ".base_storage",
        "FlextApiProtocolsGrpc": ".base_grpc",
        "FlextApiProtocolsHttpClient": ".base_http",
        "FlextApiProtocolsRequest": ".request",
        "FlextApiProtocolsResources": ".base_resources",
        "FlextApiProtocolsResponse": ".response",
        "FlextApiProtocolsSerialization": ".serialization",
        "FlextApiProtocolsSerializer": ".base_serialization",
        "FlextApiProtocolsStorage": ".storage",
        "FlextApiProtocolsTransport": ".base_transport",
        "FlextApiProtocolsTransports": ".transports",
        "FlextApiProtocolsWebhook": ".webhook",
        "FlextApiTypesProtocolPlugin": ".plugin_types",
    },
    public_exports=__all__,
)

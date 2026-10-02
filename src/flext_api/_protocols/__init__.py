# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api. Protocols package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_api._protocols._transports_config import FlextApiTransportsConfigMixin
    from flext_api._protocols._transports_request import FlextApiTransportsRequestMixin
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
    "FlextApiTransportsConfigMixin",
    "FlextApiTransportsRequestMixin",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            "._transports_config": ("FlextApiTransportsConfigMixin",),
            "._transports_request": ("FlextApiTransportsRequestMixin",),
            ".base": ("FlextApiProtocolsBase",),
            ".base_grpc": ("FlextApiProtocolsGrpc",),
            ".base_http": ("FlextApiProtocolsHttpClient",),
            ".base_resources": ("FlextApiProtocolsResources",),
            ".base_serialization": ("FlextApiProtocolsSerializer",),
            ".base_storage": ("FlextApiProtocolsStorage",),
            ".base_transport": ("FlextApiProtocolsTransport",),
            ".plugin_manager": ("FlextApiProtocolPluginManager",),
            ".plugin_types": ("FlextApiProtocolPluginTypes",),
            ".plugins": ("FlextApiProtocolPlugins",),
            ".serialization": ("FlextApiProtocolsSerialization",),
            ".transports": ("FlextApiProtocolsTransports",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)

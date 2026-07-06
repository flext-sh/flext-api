# AUTO-GENERATED FILE — Regenerate with: make gen
"""Protocols package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

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
_LAZY_IMPORTS = build_lazy_import_map(
    {
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
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)

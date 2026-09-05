# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api. Protocols package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from ._transports_config import FlextApiTransportsConfigMixin
    from ._transports_request import FlextApiTransportsRequestMixin
    from .base import FlextApiProtocolsBase
    from .base_grpc import FlextApiProtocolsGrpc
    from .base_http import FlextApiProtocolsHttpClient
    from .base_resources import FlextApiProtocolsResources
    from .base_serialization import FlextApiProtocolsSerializer
    from .base_storage import FlextApiProtocolsStorage
    from .base_transport import FlextApiProtocolsTransport
    from .plugin_manager import FlextApiProtocolPluginManager
    from .plugin_types import FlextApiProtocolPluginTypes
    from .plugins import FlextApiProtocolPlugins
    from .serialization import FlextApiProtocolsSerialization
    from .transports import FlextApiProtocolsTransports
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
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)

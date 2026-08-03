# @generated AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api. Protocols package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from ._transports_config import (
        FlextApiTransportsConfigMixin as FlextApiTransportsConfigMixin,
    )
    from ._transports_request import (
        FlextApiTransportsRequestMixin as FlextApiTransportsRequestMixin,
    )
    from .base import FlextApiProtocolsBase as FlextApiProtocolsBase
    from .base_grpc import FlextApiProtocolsGrpc as FlextApiProtocolsGrpc
    from .base_http import FlextApiProtocolsHttpClient as FlextApiProtocolsHttpClient
    from .base_resources import FlextApiProtocolsResources as FlextApiProtocolsResources
    from .base_serialization import (
        FlextApiProtocolsSerializer as FlextApiProtocolsSerializer,
    )
    from .base_storage import FlextApiProtocolsStorage as FlextApiProtocolsStorage
    from .base_transport import FlextApiProtocolsTransport as FlextApiProtocolsTransport
    from .plugin_manager import (
        FlextApiProtocolPluginManager as FlextApiProtocolPluginManager,
    )
    from .plugin_types import FlextApiProtocolPluginTypes as FlextApiProtocolPluginTypes
    from .plugins import FlextApiProtocolPlugins as FlextApiProtocolPlugins
    from .serialization import (
        FlextApiProtocolsSerialization as FlextApiProtocolsSerialization,
    )
    from .transports import FlextApiProtocolsTransports as FlextApiProtocolsTransports

_LAZY_MODULES: dict[str, tuple[str, ...]] = {
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
}


_LAZY_ALIAS_GROUPS: dict[str, tuple[tuple[str, str], ...]] = {}


_LAZY_IMPORTS = build_lazy_import_map(
    _LAZY_MODULES, alias_groups=_LAZY_ALIAS_GROUPS, sort_keys=False
)

_PUBLIC_EXPORTS: tuple[str, ...] = (
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

__all__: tuple[str, ...] = tuple(_PUBLIC_EXPORTS)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)

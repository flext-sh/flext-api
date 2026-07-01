# AUTO-GENERATED FILE — Regenerate with: make gen
"""Protocols package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_api._protocols._transports_config import (
        FlextApiTransportsConfigMixin as FlextApiTransportsConfigMixin,
    )
    from flext_api._protocols._transports_request import (
        FlextApiTransportsRequestMixin as FlextApiTransportsRequestMixin,
    )
    from flext_api._protocols.base import FlextApiProtocolsBase as FlextApiProtocolsBase
    from flext_api._protocols.base_grpc import (
        FlextApiProtocolsGrpc as FlextApiProtocolsGrpc,
    )
    from flext_api._protocols.base_http import (
        FlextApiProtocolsHttpClient as FlextApiProtocolsHttpClient,
    )
    from flext_api._protocols.base_resources import (
        FlextApiProtocolsResources as FlextApiProtocolsResources,
    )
    from flext_api._protocols.base_serialization import (
        FlextApiProtocolsSerializer as FlextApiProtocolsSerializer,
    )
    from flext_api._protocols.base_storage import (
        FlextApiProtocolsStorage as FlextApiProtocolsStorage,
    )
    from flext_api._protocols.base_transport import (
        FlextApiProtocolsTransport as FlextApiProtocolsTransport,
    )
    from flext_api._protocols.plugin_manager import (
        FlextApiProtocolPluginManager as FlextApiProtocolPluginManager,
    )
    from flext_api._protocols.plugin_types import (
        FlextApiProtocolPluginTypes as FlextApiProtocolPluginTypes,
    )
    from flext_api._protocols.plugins import (
        FlextApiProtocolPlugins as FlextApiProtocolPlugins,
    )
    from flext_api._protocols.serialization import (
        FlextApiProtocolsSerialization as FlextApiProtocolsSerialization,
    )
    from flext_api._protocols.transports import (
        FlextApiProtocolsTransports as FlextApiProtocolsTransports,
    )
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

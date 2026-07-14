# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_api.__version__ import (
    __author__ as __author__,
    __author_email__ as __author_email__,
    __description__ as __description__,
    __license__ as __license__,
    __title__ as __title__,
    __url__ as __url__,
    __version__ as __version__,
    __version_info__ as __version_info__,
)
from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_web import d, e, h, r, x

    from ._config import FlextApiConfig, config
    from ._constants.api import FlextApiConstantsApi
    from ._constants.api_enums import FlextApiConstantsEnums
    from ._constants.api_values import FlextApiConstantsValues
    from ._models.client import FlextApiModelsClient
    from ._models.request import FlextApiModelsRequest
    from ._models.response import FlextApiModelsResponse
    from ._models.storage import FlextApiModelsStorage
    from ._models.webhook import FlextApiModelsWebhook
    from ._protocols._transports_config import FlextApiTransportsConfigMixin
    from ._protocols._transports_request import FlextApiTransportsRequestMixin
    from ._protocols.base import FlextApiProtocolsBase
    from ._protocols.base_grpc import FlextApiProtocolsGrpc
    from ._protocols.base_http import FlextApiProtocolsHttpClient
    from ._protocols.base_resources import FlextApiProtocolsResources
    from ._protocols.base_serialization import FlextApiProtocolsSerializer
    from ._protocols.base_storage import FlextApiProtocolsStorage
    from ._protocols.base_transport import FlextApiProtocolsTransport
    from ._protocols.plugin_manager import FlextApiProtocolPluginManager
    from ._protocols.plugin_types import FlextApiProtocolPluginTypes
    from ._protocols.plugins import FlextApiProtocolPlugins
    from ._protocols.serialization import FlextApiProtocolsSerialization
    from ._protocols.transports import FlextApiProtocolsTransports
    from ._settings import FlextApiSettings, settings
    from ._typings.serialization import FlextApiTypingsSerialization
    from ._utilities.api_pydantic import FlextApiUtilitiesApiPydantic
    from ._utilities.client import FlextApiClient
    from ._utilities.client_codec import FlextApiClientCodecMixin
    from ._utilities.client_request import FlextApiClientRequestMixin
    from ._utilities.request_utils import FlextApiUtilitiesRequestUtils
    from ._utilities.serializers import FlextApiUtilitiesSerializers
    from ._utilities.settings_manager import FlextApiUtilitiesSettingsManager
    from .api import FlextApi, api
    from .base import FlextApiServiceBase, s
    from .constants import FlextApiConstants, FlextApiConstants as c
    from .models import FlextApiModels, FlextApiModels as m
    from .protocols import FlextApiProtocols, FlextApiProtocols as p
    from .typings import FlextApiTypes, FlextApiTypes as t
    from .utilities import FlextApiUtilities, FlextApiUtilities as u

    _ = (
        c,
        FlextApiConstants,
        t,
        FlextApiTypes,
        p,
        FlextApiProtocols,
        m,
        FlextApiModels,
        u,
        FlextApiUtilities,
        d,
        e,
        h,
        r,
        x,
        s,
        FlextApiServiceBase,
        FlextApiConfig,
        config,
        FlextApiConstantsApi,
        FlextApiConstantsEnums,
        FlextApiConstantsValues,
        FlextApiModelsClient,
        FlextApiModelsRequest,
        FlextApiModelsResponse,
        FlextApiModelsStorage,
        FlextApiModelsWebhook,
        FlextApiTransportsConfigMixin,
        FlextApiTransportsRequestMixin,
        FlextApiProtocolsBase,
        FlextApiProtocolsGrpc,
        FlextApiProtocolsHttpClient,
        FlextApiProtocolsResources,
        FlextApiProtocolsSerializer,
        FlextApiProtocolsStorage,
        FlextApiProtocolsTransport,
        FlextApiProtocolPluginManager,
        FlextApiProtocolPluginTypes,
        FlextApiProtocolPlugins,
        FlextApiProtocolsSerialization,
        FlextApiProtocolsTransports,
        FlextApiSettings,
        settings,
        FlextApiTypingsSerialization,
        FlextApiUtilitiesApiPydantic,
        FlextApiClient,
        FlextApiClientCodecMixin,
        FlextApiClientRequestMixin,
        FlextApiUtilitiesRequestUtils,
        FlextApiUtilitiesSerializers,
        FlextApiUtilitiesSettingsManager,
        FlextApi,
        api,
    )


_LAZY_MODULES: dict[str, tuple[str, ...]] = {
    "._config": ("FlextApiConfig", "config"),
    "._constants.api": ("FlextApiConstantsApi",),
    "._constants.api_enums": ("FlextApiConstantsEnums",),
    "._constants.api_values": ("FlextApiConstantsValues",),
    "._models.client": ("FlextApiModelsClient",),
    "._models.request": ("FlextApiModelsRequest",),
    "._models.response": ("FlextApiModelsResponse",),
    "._models.storage": ("FlextApiModelsStorage",),
    "._models.webhook": ("FlextApiModelsWebhook",),
    "._protocols._transports_config": ("FlextApiTransportsConfigMixin",),
    "._protocols._transports_request": ("FlextApiTransportsRequestMixin",),
    "._protocols.base": ("FlextApiProtocolsBase",),
    "._protocols.base_grpc": ("FlextApiProtocolsGrpc",),
    "._protocols.base_http": ("FlextApiProtocolsHttpClient",),
    "._protocols.base_resources": ("FlextApiProtocolsResources",),
    "._protocols.base_serialization": ("FlextApiProtocolsSerializer",),
    "._protocols.base_storage": ("FlextApiProtocolsStorage",),
    "._protocols.base_transport": ("FlextApiProtocolsTransport",),
    "._protocols.plugin_manager": ("FlextApiProtocolPluginManager",),
    "._protocols.plugin_types": ("FlextApiProtocolPluginTypes",),
    "._protocols.plugins": ("FlextApiProtocolPlugins",),
    "._protocols.serialization": ("FlextApiProtocolsSerialization",),
    "._protocols.transports": ("FlextApiProtocolsTransports",),
    "._settings": ("FlextApiSettings", "settings"),
    "._typings.serialization": ("FlextApiTypingsSerialization",),
    "._utilities.api_pydantic": ("FlextApiUtilitiesApiPydantic",),
    "._utilities.client": ("FlextApiClient",),
    "._utilities.client_codec": ("FlextApiClientCodecMixin",),
    "._utilities.client_request": ("FlextApiClientRequestMixin",),
    "._utilities.request_utils": ("FlextApiUtilitiesRequestUtils",),
    "._utilities.serializers": ("FlextApiUtilitiesSerializers",),
    "._utilities.settings_manager": ("FlextApiUtilitiesSettingsManager",),
    ".api": ("FlextApi", "api"),
    ".base": ("FlextApiServiceBase", "s"),
    ".constants": ("FlextApiConstants", "c"),
    ".models": ("FlextApiModels", "m"),
    ".protocols": ("FlextApiProtocols", "p"),
    ".typings": ("FlextApiTypes", "t"),
    ".utilities": ("FlextApiUtilities", "u"),
    "flext_web": ("d", "e", "h", "r", "x"),
}


_LAZY_ALIAS_GROUPS: dict[str, tuple[tuple[str, str], ...]] = {}


_LAZY_IMPORTS = build_lazy_import_map(
    _LAZY_MODULES, alias_groups=_LAZY_ALIAS_GROUPS, sort_keys=False
)

_DIRECT_IMPORTS: tuple[str, ...] = (
    "FlextApi",
    "FlextApiClient",
    "FlextApiClientCodecMixin",
    "FlextApiClientRequestMixin",
    "FlextApiConfig",
    "FlextApiConstants",
    "FlextApiConstantsApi",
    "FlextApiConstantsEnums",
    "FlextApiConstantsValues",
    "FlextApiModels",
    "FlextApiModelsClient",
    "FlextApiModelsRequest",
    "FlextApiModelsResponse",
    "FlextApiModelsStorage",
    "FlextApiModelsWebhook",
    "FlextApiProtocolPluginManager",
    "FlextApiProtocolPluginTypes",
    "FlextApiProtocolPlugins",
    "FlextApiProtocols",
    "FlextApiProtocolsBase",
    "FlextApiProtocolsGrpc",
    "FlextApiProtocolsHttpClient",
    "FlextApiProtocolsResources",
    "FlextApiProtocolsSerialization",
    "FlextApiProtocolsSerializer",
    "FlextApiProtocolsStorage",
    "FlextApiProtocolsTransport",
    "FlextApiProtocolsTransports",
    "FlextApiServiceBase",
    "FlextApiSettings",
    "FlextApiTransportsConfigMixin",
    "FlextApiTransportsRequestMixin",
    "FlextApiTypes",
    "FlextApiTypingsSerialization",
    "FlextApiUtilities",
    "FlextApiUtilitiesApiPydantic",
    "FlextApiUtilitiesRequestUtils",
    "FlextApiUtilitiesSerializers",
    "FlextApiUtilitiesSettingsManager",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "api",
    "build_lazy_import_map",
    "c",
    "config",
    "d",
    "e",
    "h",
    "install_lazy_exports",
    "m",
    "p",
    "r",
    "s",
    "settings",
    "t",
    "u",
    "x",
)

__all__: tuple[str, ...] = (
    "FlextApi",
    "FlextApiConstants",
    "FlextApiModels",
    "FlextApiProtocols",
    "FlextApiServiceBase",
    "FlextApiSettings",
    "FlextApiTypes",
    "FlextApiUtilities",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "api",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "settings",
    "t",
    "u",
    "x",
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)

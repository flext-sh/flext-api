# AUTO-GENERATED FILE — Regenerate with: make gen
"""Lazy export map part."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map

FLEXT_API_LAZY_IMPORTS_PART_01 = build_lazy_import_map(
    {
        "._constants.api": ("FlextApiConstantsApi",),
        "._constants.api_enums": ("FlextApiConstantsEnums",),
        "._constants.api_values": ("FlextApiConstantsValues",),
        "._models.client": ("FlextApiModelsClient",),
        "._models.request": ("FlextApiModelsRequest",),
        "._models.response": ("FlextApiModelsResponse",),
        "._models.storage": ("FlextApiModelsStorage",),
        "._models.webhook": ("FlextApiModelsWebhook",),
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
        "._typings.serialization": ("FlextApiTypingsSerialization",),
        "._utilities.client": ("FlextApiClient",),
        "._utilities.client_codec": ("FlextApiClientCodecMixin",),
        "._utilities.client_request": ("FlextApiClientRequestMixin",),
        ".api": ("FlextApi",),
        ".base": ("FlextApiServiceBase",),
        ".constants": ("FlextApiConstants",),
        ".models": ("FlextApiModels",),
        ".protocols": ("FlextApiProtocols",),
        ".settings": ("FlextApiSettings",),
        ".typings": ("FlextApiTypes",),
        ".utilities": ("FlextApiUtilities",),
    },
)

__all__: list[str] = ["FLEXT_API_LAZY_IMPORTS_PART_01"]

# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Utilities package."""

from __future__ import annotations

import typing as _t

from flext_api._utilities.adapters import FlextApiAdapters
from flext_api._utilities.app import FlextApiApp
from flext_api._utilities.client import FlextApiClient
from flext_api._utilities.lifecycle_manager import FlextApiLifecycleManager
from flext_api._utilities.middleware import FlextApiMiddleware
from flext_api._utilities.registry import FlextApiRegistry
from flext_api._utilities.serializers import FlextApiSerializers
from flext_api._utilities.server_factory import FlextApiServerFactory
from flext_api._utilities.settings_manager import FlextApiSettingsManager
from flext_api._utilities.storage import FlextApiStorage
from flext_api._utilities.webhook import FlextWebhookHandler
from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import flext_api._utilities.adapters as _flext_api__utilities_adapters

    adapters = _flext_api__utilities_adapters
    import flext_api._utilities.app as _flext_api__utilities_app

    app = _flext_api__utilities_app
    import flext_api._utilities.client as _flext_api__utilities_client

    client = _flext_api__utilities_client
    import flext_api._utilities.lifecycle_manager as _flext_api__utilities_lifecycle_manager

    lifecycle_manager = _flext_api__utilities_lifecycle_manager
    import flext_api._utilities.middleware as _flext_api__utilities_middleware

    middleware = _flext_api__utilities_middleware
    import flext_api._utilities.registry as _flext_api__utilities_registry

    registry = _flext_api__utilities_registry
    import flext_api._utilities.serializers as _flext_api__utilities_serializers

    serializers = _flext_api__utilities_serializers
    import flext_api._utilities.server_factory as _flext_api__utilities_server_factory

    server_factory = _flext_api__utilities_server_factory
    import flext_api._utilities.settings_manager as _flext_api__utilities_settings_manager

    settings_manager = _flext_api__utilities_settings_manager
    import flext_api._utilities.storage as _flext_api__utilities_storage

    storage = _flext_api__utilities_storage
    import flext_api._utilities.webhook as _flext_api__utilities_webhook

    webhook = _flext_api__utilities_webhook

    _ = (
        FlextApiAdapters,
        FlextApiApp,
        FlextApiClient,
        FlextApiLifecycleManager,
        FlextApiMiddleware,
        FlextApiRegistry,
        FlextApiSerializers,
        FlextApiServerFactory,
        FlextApiSettingsManager,
        FlextApiStorage,
        FlextWebhookHandler,
        adapters,
        app,
        client,
        lifecycle_manager,
        middleware,
        registry,
        serializers,
        server_factory,
        settings_manager,
        storage,
        webhook,
    )
_LAZY_IMPORTS = {
    "FlextApiAdapters": "flext_api._utilities.adapters",
    "FlextApiApp": "flext_api._utilities.app",
    "FlextApiClient": "flext_api._utilities.client",
    "FlextApiLifecycleManager": "flext_api._utilities.lifecycle_manager",
    "FlextApiMiddleware": "flext_api._utilities.middleware",
    "FlextApiRegistry": "flext_api._utilities.registry",
    "FlextApiSerializers": "flext_api._utilities.serializers",
    "FlextApiServerFactory": "flext_api._utilities.server_factory",
    "FlextApiSettingsManager": "flext_api._utilities.settings_manager",
    "FlextApiStorage": "flext_api._utilities.storage",
    "FlextWebhookHandler": "flext_api._utilities.webhook",
    "adapters": "flext_api._utilities.adapters",
    "app": "flext_api._utilities.app",
    "client": "flext_api._utilities.client",
    "lifecycle_manager": "flext_api._utilities.lifecycle_manager",
    "middleware": "flext_api._utilities.middleware",
    "registry": "flext_api._utilities.registry",
    "serializers": "flext_api._utilities.serializers",
    "server_factory": "flext_api._utilities.server_factory",
    "settings_manager": "flext_api._utilities.settings_manager",
    "storage": "flext_api._utilities.storage",
    "webhook": "flext_api._utilities.webhook",
}

__all__ = [
    "FlextApiAdapters",
    "FlextApiApp",
    "FlextApiClient",
    "FlextApiLifecycleManager",
    "FlextApiMiddleware",
    "FlextApiRegistry",
    "FlextApiSerializers",
    "FlextApiServerFactory",
    "FlextApiSettingsManager",
    "FlextApiStorage",
    "FlextWebhookHandler",
    "adapters",
    "app",
    "client",
    "lifecycle_manager",
    "middleware",
    "registry",
    "serializers",
    "server_factory",
    "settings_manager",
    "storage",
    "webhook",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

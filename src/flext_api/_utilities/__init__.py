# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Utilities package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_api import (
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
    from flext_api.adapters import FlextApiAdapters
    from flext_api.app import FlextApiApp
    from flext_api.client import FlextApiClient
    from flext_api.lifecycle_manager import FlextApiLifecycleManager
    from flext_api.middleware import FlextApiMiddleware
    from flext_api.registry import FlextApiRegistry
    from flext_api.serializers import FlextApiSerializers
    from flext_api.server_factory import FlextApiServerFactory
    from flext_api.settings_manager import FlextApiSettingsManager
    from flext_api.storage import FlextApiStorage
    from flext_api.webhook import FlextWebhookHandler
    from flext_core import FlextTypes

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = {
    "FlextApiAdapters": "flext_api.adapters",
    "FlextApiApp": "flext_api.app",
    "FlextApiClient": "flext_api.client",
    "FlextApiLifecycleManager": "flext_api.lifecycle_manager",
    "FlextApiMiddleware": "flext_api.middleware",
    "FlextApiRegistry": "flext_api.registry",
    "FlextApiSerializers": "flext_api.serializers",
    "FlextApiServerFactory": "flext_api.server_factory",
    "FlextApiSettingsManager": "flext_api.settings_manager",
    "FlextApiStorage": "flext_api.storage",
    "FlextWebhookHandler": "flext_api.webhook",
    "adapters": "flext_api.adapters",
    "app": "flext_api.app",
    "client": "flext_api.client",
    "lifecycle_manager": "flext_api.lifecycle_manager",
    "middleware": "flext_api.middleware",
    "registry": "flext_api.registry",
    "serializers": "flext_api.serializers",
    "server_factory": "flext_api.server_factory",
    "settings_manager": "flext_api.settings_manager",
    "storage": "flext_api.storage",
    "webhook": "flext_api.webhook",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

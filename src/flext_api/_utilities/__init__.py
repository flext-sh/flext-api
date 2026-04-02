# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""FlextApi utilities subpackage."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_api._utilities import (
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
    from flext_core import FlextTypes

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = {
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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

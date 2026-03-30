# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""FlextApi utilities subpackage."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_api._utilities import (
        adapters as adapters,
        app as app,
        client as client,
        lifecycle_manager as lifecycle_manager,
        middleware as middleware,
        registry as registry,
        serializers as serializers,
        server_factory as server_factory,
        settings_manager as settings_manager,
        storage as storage,
        webhook as webhook,
    )
    from flext_api._utilities.adapters import FlextApiAdapters as FlextApiAdapters
    from flext_api._utilities.app import FlextApiApp as FlextApiApp
    from flext_api._utilities.client import FlextApiClient as FlextApiClient
    from flext_api._utilities.lifecycle_manager import (
        FlextApiLifecycleManager as FlextApiLifecycleManager,
    )
    from flext_api._utilities.middleware import FlextApiMiddleware as FlextApiMiddleware
    from flext_api._utilities.registry import FlextApiRegistry as FlextApiRegistry
    from flext_api._utilities.serializers import (
        FlextApiSerializers as FlextApiSerializers,
    )
    from flext_api._utilities.server_factory import (
        FlextApiServerFactory as FlextApiServerFactory,
    )
    from flext_api._utilities.settings_manager import (
        FlextApiSettingsManager as FlextApiSettingsManager,
    )
    from flext_api._utilities.storage import FlextApiStorage as FlextApiStorage
    from flext_api._utilities.webhook import FlextWebhookHandler as FlextWebhookHandler

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "FlextApiAdapters": ["flext_api._utilities.adapters", "FlextApiAdapters"],
    "FlextApiApp": ["flext_api._utilities.app", "FlextApiApp"],
    "FlextApiClient": ["flext_api._utilities.client", "FlextApiClient"],
    "FlextApiLifecycleManager": [
        "flext_api._utilities.lifecycle_manager",
        "FlextApiLifecycleManager",
    ],
    "FlextApiMiddleware": ["flext_api._utilities.middleware", "FlextApiMiddleware"],
    "FlextApiRegistry": ["flext_api._utilities.registry", "FlextApiRegistry"],
    "FlextApiSerializers": ["flext_api._utilities.serializers", "FlextApiSerializers"],
    "FlextApiServerFactory": [
        "flext_api._utilities.server_factory",
        "FlextApiServerFactory",
    ],
    "FlextApiSettingsManager": [
        "flext_api._utilities.settings_manager",
        "FlextApiSettingsManager",
    ],
    "FlextApiStorage": ["flext_api._utilities.storage", "FlextApiStorage"],
    "FlextWebhookHandler": ["flext_api._utilities.webhook", "FlextWebhookHandler"],
    "adapters": ["flext_api._utilities.adapters", ""],
    "app": ["flext_api._utilities.app", ""],
    "client": ["flext_api._utilities.client", ""],
    "lifecycle_manager": ["flext_api._utilities.lifecycle_manager", ""],
    "middleware": ["flext_api._utilities.middleware", ""],
    "registry": ["flext_api._utilities.registry", ""],
    "serializers": ["flext_api._utilities.serializers", ""],
    "server_factory": ["flext_api._utilities.server_factory", ""],
    "settings_manager": ["flext_api._utilities.settings_manager", ""],
    "storage": ["flext_api._utilities.storage", ""],
    "webhook": ["flext_api._utilities.webhook", ""],
}

_EXPORTS: Sequence[str] = [
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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)

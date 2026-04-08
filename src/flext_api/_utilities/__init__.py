# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Utilities package."""

from __future__ import annotations

from flext_core.lazy import install_lazy_exports

_LAZY_IMPORTS = {
    "FlextApiAdapters": ("flext_api._utilities.adapters", "FlextApiAdapters"),
    "FlextApiApp": ("flext_api._utilities.app", "FlextApiApp"),
    "FlextApiClient": ("flext_api._utilities.client", "FlextApiClient"),
    "FlextApiLifecycleManager": (
        "flext_api._utilities.lifecycle_manager",
        "FlextApiLifecycleManager",
    ),
    "FlextApiMiddleware": ("flext_api._utilities.middleware", "FlextApiMiddleware"),
    "FlextApiRegistry": ("flext_api._utilities.registry", "FlextApiRegistry"),
    "FlextApiSerializers": ("flext_api._utilities.serializers", "FlextApiSerializers"),
    "FlextApiServerFactory": (
        "flext_api._utilities.server_factory",
        "FlextApiServerFactory",
    ),
    "FlextApiSettingsManager": (
        "flext_api._utilities.settings_manager",
        "FlextApiSettingsManager",
    ),
    "FlextApiStorage": ("flext_api._utilities.storage", "FlextApiStorage"),
    "FlextWebhookHandler": ("flext_api._utilities.webhook", "FlextWebhookHandler"),
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)

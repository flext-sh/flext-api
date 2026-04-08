# AUTO-GENERATED FILE — Regenerate with: make gen
"""Utilities package."""

from __future__ import annotations

from flext_core.lazy import install_lazy_exports

_LAZY_IMPORTS = {
    "FlextApiAdapters": ".adapters",
    "FlextApiApp": ".app",
    "FlextApiClient": ".client",
    "FlextApiLifecycleManager": ".lifecycle_manager",
    "FlextApiMiddleware": ".middleware",
    "FlextApiRegistry": ".registry",
    "FlextApiSerializers": ".serializers",
    "FlextApiServerFactory": ".server_factory",
    "FlextApiSettingsManager": ".settings_manager",
    "FlextApiStorage": ".storage",
    "FlextWebhookHandler": ".webhook",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)

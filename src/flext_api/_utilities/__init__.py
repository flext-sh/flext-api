# AUTO-GENERATED FILE — Regenerate with: make gen
"""Utilities package."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".adapters": ("FlextApiAdapters",),
        ".app": ("FlextApiApp",),
        ".client": ("FlextApiClient",),
        ".lifecycle_manager": ("FlextApiLifecycleManager",),
        ".middleware": ("FlextApiMiddleware",),
        ".registry": ("FlextApiRegistry",),
        ".serializers": ("FlextApiUtilitiesSerializers",),
        ".server_factory": ("FlextApiServerFactory",),
        ".settings_manager": ("FlextApiUtilitiesSettingsManager",),
        ".storage": ("FlextApiStorage",),
        ".webhook": ("FlextWebhookHandler",),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)

from __future__ import annotations

# AUTO-GENERATED FILE — Regenerate with: make gen
"""Utilities package."""


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
        ".settings_manager": ("FlextApiUtilitiesSettingsManager",),
        ".storage": ("FlextApiStorage",),
        ".webhook": ("FlextApiWebhookHandler",),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)

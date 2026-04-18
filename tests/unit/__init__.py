# AUTO-GENERATED FILE — Regenerate with: make gen
"""Unit package."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".test_serializers": ("TestMessagePackUnpackb",),
        ".test_smoke": (
            "TestConstants",
            "TestFacadeContract",
            "TestModels",
            "TestSerializers",
        ),
        ".test_storage": ("TestStorageContract",),
        ".test_webhook": ("TestWebhookContract",),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
